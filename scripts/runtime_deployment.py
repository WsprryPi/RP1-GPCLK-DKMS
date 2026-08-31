#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Reviewed, journaled runtime-profile filesystem deployment. Never loads modules."""
import argparse
import base64
import fcntl
import json
import os
from pathlib import Path
import stat
import tempfile
import runtime_controller_admin as admin
from runtime_layout import INVENTORY

BINDING = str(admin.BINDING)
JOURNALS = {str(admin.STATE / name) for name in ('transaction.json', 'manager.json')}
DESTINATIONS = set(INVENTORY) | {BINDING} | JOURNALS


def encode(data):
    return None if data is None else base64.b64encode(data).decode('ascii')


def decode(data):
    return None if data is None else base64.b64decode(data, validate=True)


def payloads(directory):
    binding = admin.strict_json((directory / 'binding.json').read_bytes())
    if set(binding.get('files', {})) != set(INVENTORY) or binding.get('kernel') != admin.KERNEL:
        raise ValueError('bundle inventory/kernel mismatch')
    result = {}
    for destination in sorted(INVENTORY):
        data = (directory / (admin.digest(destination.encode())+'.bin')).read_bytes()
        if len(data) > 32*1024*1024 or admin.digest(data) != binding['files'][destination]:
            raise ValueError('bundle hash mismatch')
        result[destination] = data
    result[BINDING] = (directory / 'binding.json').read_bytes()
    result.update({path: None for path in JOURNALS})
    return result


class Files:
    """Production paths only. Tests substitute this adapter, not environment paths."""
    def read(self, path):
        try:
            admin.safe_directory(Path(path).parent)
            if path in INVENTORY or path == BINDING:
                if stat.S_IMODE(Path(path).lstat().st_mode) != 0o644:
                    raise ValueError('destination mode is not 0644; preserve and review: '+path)
            return admin.read_regular(path, 32*1024*1024)
        except FileNotFoundError:
            return None

    def write(self, path, data):
        path = Path(path)
        missing = []
        parent = path.parent
        while not parent.exists():
            missing.append(parent)
            parent = parent.parent
        admin.safe_directory(parent)
        for directory in reversed(missing):
            directory.mkdir(mode=0o755)
            admin.fsync_dir(directory.parent)
        admin.safe_directory(path.parent)
        if data is None:
            path.unlink(missing_ok=True)
            admin.fsync_dir(path.parent)
            return
        fd, temporary = tempfile.mkstemp(prefix='.runtime-', dir=path.parent)
        try:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(data)
                stream.flush()
                os.fchmod(stream.fileno(), 0o600 if path.is_relative_to(admin.STATE) else 0o644)
                os.fsync(stream.fileno())
            os.replace(temporary, path)
            admin.fsync_dir(path.parent)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def quiesce(self):
        # No automatic module unload or boot edits. The operator must separately
        # establish a neutral deployment window; a loaded module is a hard stop.
        for name in ('rp1_gpclk_dkms', 'rp1_route_controller'):
            if Path('/sys/module', name).exists():
                raise ValueError('loaded module; separately authorize neutral migration first')
        shell = admin.Linux.__new__(admin.Linux)
        shell.boot = admin.read_regular('/proc/sys/kernel/random/boot_id').decode().strip()
        shell.inhibit()

    def refresh(self):
        admin.run(('/usr/sbin/depmod', '-a', admin.KERNEL))
        admin.run(('/usr/bin/systemctl', 'daemon-reload'))


def plan(files, values):
    if set(values) != DESTINATIONS:
        raise ValueError('fixed deployment inventory required')
    return {'version': 1, 'files': {path: {'before': encode(files.read(path)),
        'after': encode(values[path])} for path in sorted(values)}}


def plan_hash(value):
    return admin.digest(json.dumps(value, sort_keys=True, separators=(',', ':')).encode())


def apply(files, value, approved, recover=False):
    if plan_hash(value) != approved or value.get('version') != 1 or set(value['files']) != DESTINATIONS:
        raise ValueError('reviewed plan digest/inventory required')
    # Check ALL ownership before any restoration; preserve foreign changes.
    for path, record in value['files'].items():
        current = files.read(path)
        allowed = (decode(record['before']), decode(record['after'])) if recover else (decode(record['before']),)
        if current not in allowed:
            raise ValueError('destination changed since review: '+path)
    pending = str(admin.STATE / 'deployment-pending.json')
    existing = files.read(pending)
    if existing is not None and admin.strict_json(existing) != value:
        raise ValueError('another deployment requires recovery')
    files.write(pending, (json.dumps(value, sort_keys=True)+'\n').encode())
    files.quiesce()
    # Binding and profile are last. The persistent barrier covers all partial
    # updates and all refresh failures, including after every file was written.
    paths = sorted(value['files'], key=lambda p: (p == BINDING or p.endswith('.conf'), p))
    for path in paths:
        files.write(path, decode(value['files'][path]['before' if recover else 'after']))
    files.refresh()
    files.write(str(admin.STATE / 'last-deployment.json'), (json.dumps(value, sort_keys=True)+'\n').encode())
    files.write(pending, None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('plan', 'install', 'recover'))
    parser.add_argument('--bundle', type=Path)
    parser.add_argument('--plan-sha256')
    args = parser.parse_args()
    if os.geteuid() != 0 or os.uname().release != admin.KERNEL:
        raise ValueError('root and exact kernel required')
    # Provisioning STATE is a separately visible filesystem action. Other
    # directories are created only by an approved deployment.
    admin.safe_directory(admin.STATE)
    fd = os.open(admin.STATE / 'lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o077:
            raise ValueError('lock ownership')
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        files = Files()
        journal = files.read(str(admin.STATE / 'transaction.json'))
        if journal is not None:
            record = admin.strict_json(journal)
            if record.get('phase') != 'recovered-inhibited' or record.get('observation', {}).get('id') != 0:
                raise ValueError('runtime journal is not recovered to no route; preserve and investigate')
        pending = files.read(str(admin.STATE / 'deployment-pending.json'))
        if args.operation == 'recover':
            if pending is None:
                raise ValueError('no pending deployment')
            value = admin.strict_json(pending)
        else:
            if pending is not None:
                raise ValueError('pending deployment requires recovery')
            if args.bundle is None:
                raise ValueError('bundle required')
            value = plan(files, payloads(args.bundle))
        if args.operation == 'plan' or not args.plan_sha256:
            print(json.dumps({'planSha256':plan_hash(value), 'destinations':{path:{side:None if data is None else admin.digest(decode(data)) for side,data in record.items()} for path,record in value['files'].items()},
                              'applicationRemainsInhibited':True}, indent=2))
            return
        apply(files, value, args.plan_sha256, args.operation == 'recover')
        print('Files deployed/recovered; application remains masked. No module activated.')
    finally:
        os.close(fd)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit('STOP: '+str(error))
