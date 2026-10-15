#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Read-only package guard. Unknown administration/signing state blocks DKMS."""
from pathlib import Path
import re
import shlex
import stat
import sys

OWNER_UID = 0  # Internal fixture seam; never an environment or CLI override.
KERNEL = re.compile(r'[0-9]+\.[0-9]+\.[0-9]+\+rpt-rpi-(?:2712|v8)')


def regular(path, mode=None):
    for part in [path, *path.parents]:
        if part.is_symlink():
            raise ValueError('unsafe symlink: '+str(part))
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != OWNER_UID or info.st_mode & 0o022:
        raise ValueError('unsafe administrator file: '+str(path))
    if mode is not None and stat.S_IMODE(info.st_mode) != mode:
        raise ValueError('unsafe signing key mode')
    if info.st_size > 64*1024*1024:
        raise ValueError('administrator file exceeds bound')
    if mode is not None:
        return None
    with path.open('rb') as stream:
        value = stream.read(64*1024*1024+1)
    if len(value) > 64*1024*1024:
        raise ValueError('administrator file exceeds bound')
    return value


def framework(root):
    values = {}
    config = root/'etc/dkms'
    for path in [config/'framework.conf', *sorted((config/'framework.conf.d').glob('*.conf'))]:
        if not path.exists() and not path.is_symlink():
            continue
        for line in regular(path).decode().splitlines():
            words = shlex.split(line, comments=True)
            if not words:
                continue
            if len(words) != 1 or not re.fullmatch(r'[a-z_]+=[A-Za-z0-9/_.:+ -]*', words[0]):
                raise ValueError('dynamic DKMS configuration requires administrator review')
            key, value = words[0].split('=', 1)
            values[key] = value
    for key in ('modprobe_on_install', 'post_transaction', 'symlink_modules'):
        # DKMS treats any nonempty value, including "false", as enabled.
        if values.get(key):
            raise ValueError('non-passive DKMS configuration: '+key)
    for key, default in (('source_tree', '/usr/src'), ('dkms_tree', '/var/lib/dkms'),
                         ('install_tree', '/lib/modules')):
        if values.get(key, default) != default:
            raise ValueError('noncanonical DKMS tree: '+key)
    return values


def module_elf(path):
    import bz2
    import gzip
    import io
    import lzma
    import subprocess
    data = regular(path)
    limit = 64*1024*1024
    if path.name.endswith('.ko'):
        value = data
    elif path.suffix == '.gz':
        with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:
            value = stream.read(limit+1)
    elif path.suffix in ('.xz', '.bz2'):
        decoder = (lzma.LZMADecompressor(memlimit=128*1024*1024) if path.suffix == '.xz'
                   else bz2.BZ2Decompressor())
        value = decoder.decompress(data, max_length=limit+1)
        if not decoder.eof or decoder.unused_data:
            raise ValueError('truncated, oversized or trailing module compression')
    elif path.suffix == '.zst':
        import tempfile
        with tempfile.TemporaryFile() as source:
            source.write(data)
            source.seek(0)
            with subprocess.Popen(['/usr/bin/zstd', '-q', '-d', '-c'], stdin=source,
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as process:
                value = process.stdout.read(limit+1)
                if len(value) > limit:
                    process.kill()
                if process.wait(timeout=10):
                    raise ValueError('module decompression failed')
    else:
        raise ValueError('unrecognized module compression')
    if (len(value) > limit or not value.startswith(b'\x7fELF\x02\x01') or
            re.findall(rb'(?:^|\x00)version=([^\x00]+)\x00', value) != [b'1.0.0']):
        raise ValueError('module ELF/version differs from package')
    return value


def module_ownership(root):
    base = root/'var/lib/dkms/rp1-gpclk-dkms'
    if (base/'original_module').exists():
        raise ValueError('DKMS predecessor backup requires owning recovery')
    installed = (root/'lib/modules').resolve()
    for name in ('rp1_gpclk_dkms', 'rp1_route_controller'):
        for path in installed.rglob(name+'.ko*'):
            parts = path.relative_to(installed).parts
            if (len(parts) != 4 or not KERNEL.fullmatch(parts[0]) or
                    parts[1:3] != ('updates', 'dkms') or path.is_symlink()):
                raise ValueError('foreign provider module path')
            source = base/'1.0.0/source'
            if (not source.is_symlink() or source.resolve() !=
                    (root/'usr/src/rp1-gpclk-dkms-1.0.0').resolve()):
                raise ValueError('provider module has no current DKMS source ownership')
            cached = list((base/'1.0.0'/parts[0]).glob('*/module/'+name+'.ko*'))
            if len(cached) != 1 or cached[0].is_symlink() or module_elf(path) != module_elf(cached[0]):
                raise ValueError('foreign or modified provider module preserved')


def check(root=Path('/'), operation='configure'):
    for name in ('rp1_gpclk_dkms', 'rp1_route_controller'):
        if (root/'sys/module'/name).exists():
            raise ValueError('loaded provider blocks package mutation')
    for name in ('dev/rp1-gpclk', 'dev/rp1-route-admin',
                 'run/rp1-gpclk-dkms/route-manager.sock',
                 'etc/rp1-gpclk-dkms/runtime-controller.json',
                 'var/lib/rp1-gpclk-dkms/runtime-admin',
                 'var/lib/rp1-gpclk-dkms/route-transactions',
                 'var/lib/rp1-gpclk-dkms/development',
                 'etc/systemd/system/wsprrypi.service.d/90-rp1-route-inhibit.conf',
                 'etc/systemd/system/wsprrypi.service.d/91-rp1-route-idle.conf'):
        path = root/name
        if path.exists() or path.is_symlink():
            raise ValueError('recover through owning workflow before package mutation: '+name)
    for path in (root/'sys/firmware/devicetree/base').rglob('compatible'):
        data = path.read_bytes()
        if b'wsprrypi,rp1-gpclk-dkms-v1' in data.split(b'\0'):
            raise ValueError('firmware or foreign RP1 route node blocks package mutation')
    config = root/'boot/firmware/config.txt'
    if config.exists() and re.search(r'^\s*(?:include\b|dtoverlay\s*=\s*rp1-gpclk-)',
                                    regular(config).decode(), re.M):
        raise ValueError('configured or included route state requires administrator review')
    module_ownership(root)
    values = framework(root)
    if operation != 'configure':
        return
    kernels = sorted(p for p in (root/'lib/modules').glob('*') if KERNEL.fullmatch(p.name))
    for kernel in kernels:
        if kernel.is_symlink():
            raise ValueError('unsafe installed kernel directory')
        config = kernel/'build/.config'
        if not config.exists():
            if (kernel/'build').exists() or (kernel/'build').is_symlink():
                raise ValueError('kernel header configuration unavailable')
            continue
        # The headers build link is distribution-owned; inspect the resolved config.
        text = regular(config.resolve()).decode()
        if re.search(r'^CONFIG_MODULE_SIG_HASH=', text, re.M):
            if values.get('sign_file'):
                configured = root/values['sign_file'].lstrip('/')
                canonical = kernel/'build/scripts/sign-file'
                if not values['sign_file'].startswith('/') or regular(configured.resolve()) != regular(canonical.resolve()):
                    raise ValueError('noncanonical signing command requires separate review')
            key = values.get('mok_signing_key', '/var/lib/dkms/mok.key')
            cert = values.get('mok_certificate', '/var/lib/dkms/mok.pub')
            if not key.startswith('/') or not cert.startswith('/'):
                raise ValueError('explicit filesystem signing identity required')
            regular(root/key.lstrip('/'), 0o600)
            certificate = root/cert.lstrip('/')
            regular(certificate)
            if stat.S_IMODE(certificate.stat().st_mode) & ~0o644:
                raise ValueError('unsafe public certificate mode')
    # Package-specific DKMS overrides can replace the reviewed build/hooks/signing.
    if any((root/'etc/dkms').glob('rp1-gpclk-dkms*.conf')):
        raise ValueError('administrator module override requires separate review')


if __name__ == '__main__':
    try:
        if sys.argv[1:] not in (['configure'], ['remove']):
            raise ValueError('expected configure or remove')
        check(operation=sys.argv[1])
    except (OSError, ValueError) as error:
        raise SystemExit('rp1-gpclk-dkms: '+str(error))
