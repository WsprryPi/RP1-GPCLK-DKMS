#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Create local deployment-review metadata from compiled modules; never install."""
import hashlib
import json
from pathlib import Path
import sys
from runtime_inventory import module_note
from runtime_controller_admin import KERNEL

ROOT = Path(__file__).resolve().parents[1]


def build(directory):
    base = f'/lib/modules/{KERNEL}/updates/dkms/'
    values = {'schemaVersion': 1, 'kernel': KERNEL, 'files': {}}
    for module, field in (('rp1_route_controller', 'controllerNoteSha256'),
                          ('rp1_gpclk_dkms', 'consumerNoteSha256')):
        payload = (directory / (module + '.ko')).read_bytes()
        values['files'][base + module + '.ko'] = hashlib.sha256(payload).hexdigest()
        values[field] = hashlib.sha256(module_note(payload)).hexdigest()
    values['files']['/usr/lib/rp1-gpclk-dkms/runtime_controller_admin.py'] = hashlib.sha256(
        (ROOT / 'scripts/runtime_controller_admin.py').read_bytes()).hexdigest()
    return values


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('usage: build_runtime_binding.py LOCAL_COMPILED_MODULE_DIRECTORY')
    print(json.dumps(build(Path(sys.argv[1])), indent=2, sort_keys=True))
