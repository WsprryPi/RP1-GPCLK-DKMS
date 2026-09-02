#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Runtime route reconciliation and explicit application resumption. No command in this module starts a clock."""
import fcntl
import os
from pathlib import Path
import stat
import struct
import runtime_controller_admin as admin

SNAPSHOT = struct.Struct('=HHI18I6Q64s64s64s8Q')
SNAPSHOT_IOCTL = 0xc180b828


def parse_snapshot(data):
    if len(data) != SNAPSHOT.size:
        raise ValueError('passive snapshot ABI size')
    values = SNAPSHOT.unpack(data)
    if values[:3] != (SNAPSHOT.size, 0, 0):
        raise ValueError('passive snapshot ABI mismatch')
    keys = ('route','compatibility','reason','operation','terminal','event','flags','fault','owner','lease',
            'outputInhibited','operationalReady','drain','gpio','clock','dma','stable','reserved')
    result = dict(zip(keys, values[3:21]))
    if result['reserved'] or any(values[-8:]) or result['flags'] & ~7:
        raise ValueError('passive snapshot reserved fields')
    return result


def snapshot():
    fd = os.open('/dev/rp1-gpclk', os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        info = os.fstat(fd)
        major, minor = admin.read_regular('/sys/class/misc/rp1-gpclk/dev').decode().strip().split(':')
        if not stat.S_ISCHR(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o007 or info.st_rdev != os.makedev(int(major), int(minor)):
            raise ValueError('consumer endpoint identity')
        data = bytearray(SNAPSHOT.size)
        struct.pack_into('=HHI', data, 0, SNAPSHOT.size, 0, 0)
        fcntl.ioctl(fd, SNAPSHOT_IOCTL, data, True)
        return parse_snapshot(data)
    finally:
        os.close(fd)


def require_idle(value, route):
    if (value['route'] != route or value['compatibility'] != 3 or
            any(value[k] != 1 for k in ('fault','owner','lease','outputInhibited')) or
            any(value[k] != 2 for k in ('operationalReady','gpio','clock','dma','stable'))):
        raise ValueError('consumer is not operationally ready, closed and quiescent')


def ready(system, state, route):
    admin.validate_observation(state)
    journal = system.read_journal()
    if (state['route'] != route or state['flags'] != admin.CONSUMER | admin.PINNED or
            state['error'] or not journal or journal.get('phase') != 'complete-inhibited' or
            journal.get('boot') != system.boot or journal.get('binding') != system.binding_hash or
            journal.get('session') != state['session'] or journal.get('observation') != state):
        raise ValueError('runtime route is unresolved or mismatched')
    observed = system.output_snapshot()
    require_idle(observed, route)
    return observed


def dispatch(system, request, state):
    route = {'gpio4': 1, 'gpio20': 2}[request['route']]
    observed = ready(system, state, route)
    result = {'ready': True, 'productionAuthority': 'root-owned-endpoint', 'route': request['route'],
              'controller': state, 'bootId': system.boot, 'bindingSha256': system.binding_hash,
              'snapshot': observed}
    if request['operation'] == 'idle':
        return result
    if request['operation'] == 'resume':
        # No synchronous start here: application startup queries the same lock.
        system.check_inhibit()
        system.output_resume()
        return result
    # Reconciliation proves route and lifecycle state. Product policy and
    # operator workflow remain the application's responsibility.
    return result


def parse(value):
    if not isinstance(value, dict) or value.get('schemaVersion') != 3 or type(value.get('schemaVersion')) is not int:
        raise ValueError('runtime output request schema')
    operation = value.get('operation')
    fields = {'schemaVersion','operation','route'}
    if operation not in ('idle','reconcile-output','resume') or value.get('route') not in ('gpio4','gpio20'):
        raise ValueError('unsupported runtime output operation/route')
    if operation == 'resume':
        fields |= {'execute'}
        if value.get('execute') is not True: raise ValueError('explicit execution required')
    if set(value) != fields: raise ValueError('unexpected output request fields')
    return value
