#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Opt-in clock-disabled administration. Installation is a separate gate.

CLI paths and subprocesses are fixed. An installed root-owned exact-artifact
binding is mandatory. This is cooperative service inhibition, not root isolation.
"""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import selectors
import time
import struct
import subprocess
import sys
import tempfile
import uuid

KERNEL = '6.18.34+rpt-rpi-2712'
STATE = Path('/var/lib/rp1-gpclk-dkms/runtime-admin')
BINDING = Path('/etc/rp1-gpclk-dkms/runtime-controller.json')
ENDPOINT = '/dev/rp1-route-admin'
UNIT_DIR = Path('/etc/systemd/system')
FORMAT = struct.Struct('=IIIIQQiiIIQQ')
IOCTL = 0xc040b801
STATUS, APPLY, REMOVE = 0, 1, 2
FAULT, CONSUMER, PINNED = 1, 2, 4


def strict_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON field')
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=pairs)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_regular(path, limit=1024*1024):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
            raise ValueError('untrusted file: ' + str(path))
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            data = stream.read(limit + 1)
        if len(data) > limit:
            raise ValueError('file limit')
        return data
    finally:
        os.close(fd)


def fsync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        info = os.fstat(fd)
        if info.st_uid != 0 or info.st_mode & 0o022:
            raise ValueError('untrusted directory')
        os.fsync(fd)
    finally:
        os.close(fd)


def safe_directory(path):
    # Validate every ancestor; never follow a caller-controlled state symlink.
    current = Path('/')
    for part in path.parts[1:]:
        current /= part
        info = current.lstat()
        if current == Path('/lib') and stat.S_ISLNK(info.st_mode):
            if info.st_uid != 0 or os.readlink(current) not in ('usr/lib', '/usr/lib'):
                raise ValueError('untrusted system library alias')
            current = Path('/usr/lib')
            safe_directory(current)
            continue
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
            raise ValueError('untrusted directory: ' + str(current))


def run(argv):
    process = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, env={'PATH': '/usr/sbin:/usr/bin:/sbin:/bin',
                                     'LC_ALL': 'C', 'SYSTEMD_PAGER': 'cat'})
    output = bytearray()
    deadline = time.monotonic() + 15
    try:
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0 or not selector.select(remaining):
                    raise ValueError('command timeout; kernel effects may still be pending')
                chunk = os.read(process.stdout.fileno(), min(4096, 65537-len(output)))
                if not chunk:
                    break
                output.extend(chunk)
                if len(output) > 65536:
                    raise ValueError('command output limit')
        code = process.wait(timeout=max(0.001, deadline-time.monotonic()))
        if code:
            raise ValueError('fixed command failed: ' + argv[0] + ' exit=' + str(code) + ': ' + output.decode('utf-8', errors='replace')[-2048:].strip())
        return output.decode('utf-8').strip()
    finally:
        if process.poll() is None:
            process.kill()
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                pass  # Never turn a userspace timeout into a kernel completion claim.
        process.stdout.close()


class Linux:
    def __init__(self):
        self.lock = self.fd = None
        try:
            self.initialize()
        except BaseException:
            self.close()
            raise

    def __enter__(self):
        return self

    def __exit__(self, *unused):
        self.close()

    def close(self):
        for name in ('fd', 'lock'):
            fd = getattr(self, name, None)
            if fd is not None:
                os.close(fd)
                setattr(self, name, None)

    def initialize(self):
        if os.geteuid() != 0 or os.uname().release != KERNEL:
            raise ValueError('root and exact reviewed kernel required')
        safe_directory(STATE)
        self.lock = os.open(STATE / 'lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        info = os.fstat(self.lock)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o077:
            raise ValueError('lock ownership')
        fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if (STATE / 'deployment-pending.json').exists():
            raise ValueError('unfinished deployment; recover before route administration')
        safe_directory(BINDING.parent)
        raw = read_regular(BINDING)
        self.binding = strict_json(raw)
        self.binding_hash = digest(raw)
        if not isinstance(self.binding, dict) or set(self.binding) != {'schemaVersion', 'kernel', 'files', 'controllerNoteSha256',
                                 'consumerNoteSha256'} or type(self.binding['schemaVersion']) is not int or self.binding['schemaVersion'] != 1 or self.binding['kernel'] != KERNEL:
            raise ValueError('binding schema')
        base = f'/lib/modules/{KERNEL}/updates/dkms/'
        from runtime_layout import INVENTORY
        expected = set(INVENTORY)
        if not isinstance(self.binding['files'], dict) or set(self.binding['files']) != expected:
            raise ValueError('fixed artifact inventory required')
        for name, sha in self.binding['files'].items():
            safe_directory(Path(name).parent)
            if not isinstance(sha, str) or len(sha) != 64 or digest(read_regular(name, 32*1024*1024)) != sha:
                raise ValueError('artifact mismatch: ' + name)
        if digest(Path(__file__).read_bytes()) != self.binding['files']['/usr/lib/rp1-gpclk-dkms/runtime_controller_admin.py']:
            raise ValueError('executing tool mismatch')
        for module in ('rp1_gpclk_dkms', 'rp1_route_controller'):
            if run(('/usr/sbin/modinfo', '-F', 'filename', module)) != base+module+'.ko':
                raise ValueError('module resolution mismatch')
        if run(('/usr/sbin/modinfo', '-F', 'rp1_runtime_controller', 'rp1_gpclk_dkms')) != '1':
            raise ValueError('consumer lacks interlock')
        self.boot = read_regular('/proc/sys/kernel/random/boot_id').decode().strip()
        uuid.UUID(self.boot)
        self.note('rp1_route_controller', 'controllerNoteSha256')
        if Path('/sys/module/rp1_gpclk_dkms').exists():
            self.note('rp1_gpclk_dkms', 'consumerNoteSha256')
            if read_regular('/sys/module/rp1_gpclk_dkms/parameters/live_output').strip() not in (b'N', b'0'):
                raise ValueError('loaded consumer output is not disabled')
        self.fd = os.open(ENDPOINT, os.O_RDWR | os.O_NOFOLLOW)
        info = os.fstat(self.fd)
        if not stat.S_ISCHR(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o077:
            raise ValueError('controller endpoint ownership')
        major, minor = read_regular('/sys/class/misc/rp1-route-admin/dev').decode().strip().split(':')
        if info.st_rdev != os.makedev(int(major), int(minor)):
            raise ValueError('controller endpoint identity')

    def note(self, module, key):
        if digest(read_regular(f'/sys/module/{module}/notes/.note.gnu.build-id')) != self.binding[key]:
            raise ValueError('loaded build note mismatch')

    def call(self, operation=STATUS, route=0, before=None):
        before = before or {'session': 0, 'generation': 0}
        data = bytearray(FORMAT.pack(1, operation, route, 0, before['session'],
                                    before['generation'], 0, 0, 0, 0, 0, 0))
        fcntl.ioctl(self.fd, IOCTL, data, True)
        abi, op, route, reserved, session, generation, oid, error, active, flags, r1, r2 = FORMAT.unpack(data)
        if abi != 1 or op or route or reserved or r1 or r2 or not session or active not in (0, 1, 2) or flags & ~7:
            raise ValueError('controller response schema')
        result = dict(session=session, generation=generation, id=oid, error=error, route=active, flags=flags)
        validate_observation(result)
        if operation and (session != before['session'] or generation != before['generation'] + 1):
            raise ValueError('effect response generation/session mismatch')
        return result

    def inhibit(self):
        # Persistent mask covers normal systemd starts/restarts and reboot. Never
        # overwrite an existing administrator-owned service file or unmask here.
        directory = UNIT_DIR
        safe_directory(directory)
        mask = directory / 'wsprrypi.service'
        try:
            os.symlink('/dev/null', mask)
        except FileExistsError:
            if not mask.is_symlink() or os.readlink(mask) != '/dev/null':
                raise ValueError('foreign service unit; cannot inhibit safely')
        fsync_dir(directory)
        run(('/usr/bin/systemctl', 'daemon-reload'))
        run(('/usr/bin/systemctl', 'stop', 'wsprrypi.service'))
        self.check_inhibit()

    def check_inhibit(self):
        mask = UNIT_DIR / 'wsprrypi.service'
        if not mask.is_symlink() or os.readlink(mask) != '/dev/null':
            raise ValueError('persistent inhibit lost')
        if run(('/usr/bin/systemctl', 'show', 'wsprrypi.service', '--property=ActiveState', '--value')) not in ('inactive', 'failed'):
            raise ValueError('application still active')
        if read_regular('/proc/sys/kernel/random/boot_id').decode().strip() != self.boot:
            raise ValueError('boot changed')

    def unload(self):
        self.check_inhibit()
        if Path('/sys/module/rp1_gpclk_dkms').exists():
            self.note('rp1_gpclk_dkms', 'consumerNoteSha256')
            if read_regular('/sys/module/rp1_gpclk_dkms/parameters/live_output').strip() not in (b'N', b'0'):
                raise ValueError('consumer output gate not disabled')
            run(('/usr/sbin/rmmod', 'rp1_gpclk_dkms'))
        if Path('/sys/module/rp1_gpclk_dkms').exists():
            raise ValueError('consumer remains loaded')

    def load(self):
        self.check_inhibit()
        run(('/usr/sbin/insmod', f'/lib/modules/{KERNEL}/updates/dkms/rp1_gpclk_dkms.ko', 'live_output=0'))
        self.note('rp1_gpclk_dkms', 'consumerNoteSha256')
        if read_regular('/sys/module/rp1_gpclk_dkms/parameters/live_output').strip() not in (b'N', b'0'):
            raise ValueError('consumer gate mismatch')

    def inhibited(self):
        try:
            self.check_inhibit()
            return True
        except ValueError:
            return False

    def read_manager_record(self):
        return self.read_record('manager.json')

    def write_manager_record(self, value):
        self.write_record('manager.json', value)

    def read_journal(self):
        return self.read_record('transaction.json')

    def read_record(self, name):
        try:
            return strict_json(read_regular(STATE / name))
        except FileNotFoundError:
            return None

    def write_journal(self, value):
        self.write_record('transaction.json', value)

    def write_record(self, filename, value):
        data = (json.dumps(value, sort_keys=True) + '\n').encode()
        fd, name = tempfile.mkstemp(prefix='journal-', dir=STATE)
        try:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, STATE / filename)
            fsync_dir(STATE)
        finally:
            if os.path.exists(name):
                os.unlink(name)


def validate_observation(value):
    if (not isinstance(value, dict) or set(value) != {'session', 'generation', 'id', 'error', 'route', 'flags'} or
            any(type(v) is not int for v in value.values()) or not 0 < value['session'] < 2**64 or
            not 0 <= value['generation'] < 2**64 or not 0 <= value['id'] < 2**31 or
            not -4095 <= value['error'] <= 0 or value['route'] not in (0, 1, 2) or
            not 0 <= value['flags'] <= 7 or
            (value['id'] == 0) != (value['route'] == 0) or
            (value['id'] > 0 and not value['flags'] & PINNED) or
            (value['flags'] & CONSUMER and value['id'] == 0)):
        raise ValueError('invalid controller observation')


def execute(system, route=None, recover=False):
    previous = system.read_journal()
    current = system.call()
    validate_observation(current)
    if previous is not None:
        if (not isinstance(previous, dict) or set(previous) != {'version', 'boot', 'session', 'binding', 'request', 'target', 'phase', 'observation'} or
                type(previous['version']) is not int or previous['version'] != 1 or
                not isinstance(previous['request'], str) or type(previous['target']) is not int or
                previous['boot'] != system.boot or
                previous['session'] != current['session'] or previous['binding'] != system.binding_hash or
                previous['target'] not in (1, 2) or previous['phase'] not in
                ('inhibit-intent', 'unload-intent', 'remove-intent', 'apply-intent', 'load-intent', 'complete-inhibited', 'recovered-inhibited')):
            raise ValueError('journal mismatch; preserve inhibition and investigate')
        uuid.UUID(previous['request'])
        observed = previous['observation']
        validate_observation(observed)
        if observed['session'] != current['session']:
            raise ValueError('journal observation session mismatch')
        delta = current['generation'] - observed['generation']
        if delta not in (0, 1) or (delta == 1 and previous['phase'] not in ('apply-intent', 'remove-intent')):
            raise ValueError('unattributable controller generation')
        if delta == 0 and any(current[k] != observed[k] for k in ('id', 'route', 'error')):
            # Cleanup fault is a recorded consumer outcome, never permission for
            # a successor. Permit only explicit cleanup recovery of that fault.
            if not (recover and current['flags'] & FAULT and current['id'] == observed['id']):
                raise ValueError('controller changed outside the recorded effect')
        if delta == 1 and previous['phase'] == 'apply-intent' and current['id'] > 0 and current['route'] != previous['target']:
            raise ValueError('applied route differs from journal')
        if not recover and previous['phase'] not in ('complete-inhibited', 'recovered-inhibited'):
            raise ValueError('unfinished transaction requires explicit recovery')
    if recover and previous is None:
        raise ValueError('no attributable transaction')
    if not recover and route not in (1, 2):
        raise ValueError('route required')
    if previous is None and (current['id'] or current['flags']):
        raise ValueError('existing controller state has no attributable journal')
    if current['flags'] & FAULT and not recover:
        raise ValueError('controller fault; no successor permitted')
    record = previous.copy() if recover else dict(version=1, boot=system.boot,
        session=current['session'], binding=system.binding_hash, request=str(uuid.uuid4()), target=route,
        phase='inhibit-intent', observation=current)

    def journal(phase):
        record.update(phase=phase, observation=current)
        system.write_journal(record)

    journal('inhibit-intent')
    system.inhibit()
    journal('unload-intent')
    system.unload()
    before_unload = current
    current = system.call()
    if (any(current[k] != before_unload[k] for k in ('session', 'generation', 'id', 'route')) or
            current['flags'] & CONSUMER):
        raise ValueError('consumer exclusion/session lost')
    if current['id'] > 0:
        journal('remove-intent')
        system.check_inhibit()
        current = system.call(REMOVE, before=current)
        if current['error'] or current['id']:
            raise ValueError('overlay removal failed; preserve controller ID/error and inhibition')
    if current['flags'] & FAULT:
        raise ValueError('latched controller fault; no successor or inhibit release')
    if recover:
        journal('recovered-inhibited')
        return current
    journal('apply-intent')
    system.check_inhibit()
    current = system.call(APPLY, route, current)
    if current['error'] or current['flags'] & FAULT or current['route'] != route or current['id'] <= 0:
        raise ValueError('overlay apply failed; explicit recovery required')
    journal('load-intent')
    system.load()
    before_load = current
    current = system.call()
    if (any(current[k] != before_load[k] for k in ('session', 'generation', 'id', 'route')) or
            current['flags'] & FAULT or not current['flags'] & CONSUMER):
        raise ValueError('consumer binding not established')
    journal('complete-inhibited')
    return current


def main():
    if sys.argv[1:] not in (['switch', 'gpio4'], ['switch', 'gpio20'], ['recover'], ['status']):
        raise SystemExit('usage: runtime_controller_admin.py switch gpio4|gpio20 | recover | status')
    system = Linux()
    if sys.argv[1] == 'status':
        print(json.dumps({'state': system.call(), 'qualification': False}))
        return
    result = execute(system, route={'gpio4': 1, 'gpio20': 2}.get(sys.argv[-1]),
                     recover=sys.argv[1] == 'recover')
    print(json.dumps({'state': result, 'applicationInhibited': True, 'qualification': False}))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        raise SystemExit('STOP: ' + str(error) + '; do not release inhibition or assume an effect stopped')
