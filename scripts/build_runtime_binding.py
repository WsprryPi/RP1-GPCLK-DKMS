#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Create local deployment-review metadata from compiled modules; never install."""
import hashlib
import json
from pathlib import Path
import re
import sys
from runtime_inventory import module_note
from runtime_controller_admin import KERNEL
from runtime_layout import INVENTORY

ROOT = Path(__file__).resolve().parents[1]


def validate_module_version(payload):
    """Do not bind predecessor modules to current userspace/overlay source."""
    versions = re.findall(rb'(?:^|\x00)version=([^\x00]+)\x00', payload)
    if versions != [b'0.9.0']:
        raise ValueError('runtime module version differs from 0.9.0 development source')


def build(directory):
    from build_runtime_controller import generate
    generate(ROOT / "build/runtime-controller")
    base = f'/lib/modules/{KERNEL}/updates/dkms/'
    values = {'schemaVersion': 1, 'kernel': KERNEL, 'files': {}}
    for module, field in (('rp1_route_controller', 'controllerNoteSha256'),
                          ('rp1_gpclk_dkms', 'consumerNoteSha256')):
        payload = (directory / (module + '.ko')).read_bytes()
        validate_module_version(payload)
        values['files'][base + module + '.ko'] = hashlib.sha256(payload).hexdigest()
        values[field] = hashlib.sha256(module_note(payload)).hexdigest()
    for destination, source in INVENTORY.items():
        if not source.endswith('.ko'):
            values['files'][destination] = hashlib.sha256((ROOT / source).read_bytes()).hexdigest()
    return values


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('usage: build_runtime_binding.py LOCAL_COMPILED_MODULE_DIRECTORY')
    print(json.dumps(build(Path(sys.argv[1])), indent=2, sort_keys=True))
