#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Create local deployment-review metadata from compiled modules; never install."""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from runtime_inventory import module_note
from runtime_layout import INVENTORY, KERNEL
from runtime_binding import (APPLICATION, COMPATIBILITY, CONTRACT, EXTERNAL_SOURCES, PRODUCT_VERSION,
                             canonical_digest, validate)

ROOT = Path(__file__).resolve().parents[1]


def validate_module_version(payload):
    """Do not bind predecessor modules to current userspace/overlay source."""
    versions = re.findall(rb'(?:^|\x00)version=([^\x00]+)\x00', payload)
    if versions != [b'0.9.0']:
        raise ValueError('runtime module version differs from 0.9.0 development source')


def source_commit():
    value = subprocess.run(('git', '-C', str(ROOT), 'rev-parse', 'HEAD'),
        check=True, stdout=subprocess.PIPE, text=True).stdout.strip()
    if not re.fullmatch('[0-9a-f]{40}', value):
        raise ValueError('source commit identity unavailable')
    return value


def companion_bytes(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError('application companion must be a regular file')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            value = stream.read(4*1024*1024 + 1)
        if len(value) > 4*1024*1024:
            raise ValueError('application companion exceeds bound')
        return value
    finally:
        os.close(fd)


def build(directory, application_companion):
    from build_runtime_controller import generate
    generate(ROOT / "build/runtime-controller")
    base = f'/lib/modules/{KERNEL}/updates/dkms/'
    companion = Path(application_companion)
    companion = companion_bytes(companion)
    values = {'schemaVersion': 2, 'contract': CONTRACT,
              'productVersion': PRODUCT_VERSION,
              'compatibilityIdentities': COMPATIBILITY,
              'sourceCommit': source_commit(), 'kernel': KERNEL, 'files': {},
              'externalFiles': {APPLICATION: hashlib.sha256(companion).hexdigest(),
                  **{destination: hashlib.sha256((ROOT/source).read_bytes()).hexdigest()
                     for destination, source in EXTERNAL_SOURCES.items()}},
              'uapiSha256': {}}
    for module, field in (('rp1_route_controller', 'controllerNoteSha256'),
                          ('rp1_gpclk_dkms', 'consumerNoteSha256')):
        payload = (directory / (module + '.ko')).read_bytes()
        validate_module_version(payload)
        values['files'][base + module + '.ko'] = hashlib.sha256(payload).hexdigest()
        values[field] = hashlib.sha256(module_note(payload)).hexdigest()
    for destination, source in INVENTORY.items():
        if not source.endswith('.ko'):
            values['files'][destination] = hashlib.sha256((ROOT / source).read_bytes()).hexdigest()
    values['uapiSha256'] = {
        'consumer': values['files']['/usr/lib/rp1-gpclk-dkms/runtime-uapi/rp1_gpclk.h'],
        'controller': values['files']['/usr/lib/rp1-gpclk-dkms/runtime-uapi/rp1_route_admin.h']}
    values['artifactSetSha256'] = canonical_digest(values)
    return validate(values)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('usage: build_runtime_binding.py LOCAL_COMPILED_MODULE_DIRECTORY WSPRRYPI_APPLICATION_COMPANION')
    print(json.dumps(build(Path(sys.argv[1]), Path(sys.argv[2])), indent=2, sort_keys=True))
