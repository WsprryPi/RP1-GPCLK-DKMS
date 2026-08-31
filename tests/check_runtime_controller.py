#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Offline tests of the actual kernel entrypoint and concrete admin sequencing."""
import copy
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import runtime_controller_admin as admin
from build_runtime_controller import generate


class Machine:
    boot = '11111111-2222-3333-4444-555555555555'
    binding_hash = 'a'*64
    def __init__(self):
        self.value = dict(session=7, generation=0, id=0, error=0, route=0, flags=0)
        self.journal = None
        self.mask = False
        self.events = []
        self.crash = None
        self.remove_error = 0
        self.apply_error = 0
    def event(self, name):
        self.events.append(name)
        if len(self.events) == self.crash:
            raise OSError('injected process death')
    def read_journal(self): return copy.deepcopy(self.journal)
    def write_journal(self, value):
        self.event('journal-before')
        self.journal = copy.deepcopy(value)
        self.event('journal-after')
    def inhibit(self):
        self.event('inhibit-before')
        self.mask = True
        self.event('inhibit-after')
    def check_inhibit(self):
        assert self.mask
        self.event('inhibit-check')
    def unload(self):
        self.check_inhibit()
        self.value['flags'] &= ~admin.CONSUMER
        self.event('unload')
    def load(self):
        self.check_inhibit()
        self.value['flags'] |= admin.CONSUMER
        self.event('load')
    def call(self, operation=0, route=0, before=None):
        if operation:
            self.check_inhibit()
            assert not self.value['flags'] & admin.CONSUMER
            assert before['session'] == self.value['session']
            assert before['generation'] == self.value['generation']
            self.event('effect-before')
            self.value['generation'] += 1
            old_fault = self.value['flags'] & admin.FAULT
            if operation == admin.APPLY:
                assert self.value['id'] == 0
                self.value.update(id=9, route=route, error=self.apply_error, flags=admin.PINNED)
            else:
                self.value.update(id=9 if self.remove_error else 0,
                                  route=self.value['route'] if self.remove_error else 0,
                                  error=self.remove_error, flags=admin.PINNED if self.remove_error else 0)
            self.value['flags'] |= old_fault
            if self.value['error']: self.value['flags'] |= admin.FAULT
            self.event('effect-after')
        return self.value.copy()


class Tests(unittest.TestCase):
    def test_actual_kernel_entrypoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            generate(tmp)
            (tmp / 'linux').mkdir()
            names = ('capability', 'compat', 'fs', 'miscdevice', 'module', 'mutex', 'of',
                     'random', 'uaccess', 'utsname', 'types', 'ioctl')
            stub = ROOT / 'tests/fixtures/runtime_controller_stubs.h'
            for name in names:
                (tmp / 'linux' / (name+'.h')).write_text(f'#include "{stub}"\n')
            binary = tmp / 'controller-test'
            subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-Wno-unused-parameter',
                            '-I'+str(tmp), '-I'+str(ROOT/'include/uapi'), '-I'+str(ROOT/'controller'),
                            str(ROOT/'tests/fixtures/runtime_controller_harness.c'), '-o', str(binary)], check=True)
            subprocess.run([str(binary)], check=True)

    def test_switch_both_directions(self):
        machine = Machine()
        for route in (1, 2, 1):
            result = admin.execute(machine, route)
            self.assertEqual(result['route'], route)
            self.assertTrue(machine.mask)
            self.assertEqual(machine.journal['phase'], 'complete-inhibited')

    def test_crash_every_boundary_requires_explicit_recovery(self):
        sample = Machine(); admin.execute(sample, 1)
        for point in range(1, len(sample.events)+1):
            machine = Machine(); machine.crash = point
            with self.assertRaises(OSError): admin.execute(machine, 1)
            machine.crash = None
            if machine.journal is None: continue
            if machine.journal['phase'] != 'complete-inhibited':
                with self.assertRaises(ValueError): admin.execute(machine, 2)
            result = admin.execute(machine, recover=True)
            self.assertEqual(result['id'], 0)
            self.assertTrue(machine.mask)
            self.assertEqual(machine.journal['phase'], 'recovered-inhibited')

    def test_remove_error_prevents_successor(self):
        machine = Machine(); admin.execute(machine, 1)
        machine.remove_error = -16
        with self.assertRaises(ValueError): admin.execute(machine, 2)
        self.assertEqual(machine.value['route'], 1)
        self.assertEqual(machine.value['id'], 9)
        self.assertTrue(machine.mask)
        self.assertEqual(machine.journal['phase'], 'remove-intent')

    def test_apply_error_preserves_recovery_record(self):
        machine = Machine(); machine.apply_error = -5
        with self.assertRaises(ValueError): admin.execute(machine, 1)
        self.assertEqual(machine.journal['phase'], 'apply-intent')
        self.assertTrue(machine.mask)
        self.assertEqual(machine.value['id'], 9)

    def test_reboot_binding_or_session_change_never_adopted(self):
        for field, value in [('boot', 'changed'), ('session', 999), ('binding', 'changed')]:
            machine = Machine(); admin.execute(machine, 1)
            machine.journal[field] = value
            start = len(machine.events)
            with self.assertRaises(ValueError): admin.execute(machine, recover=True)
            self.assertEqual(len(machine.events), start)

    def test_concrete_fixed_load_and_unload_commands(self):
        system = object.__new__(admin.Linux)
        system.check_inhibit = lambda: None
        system.note = lambda *args: None
        calls = []
        with patch.object(admin, 'run', side_effect=lambda argv: calls.append(argv)), \
             patch.object(admin, 'read_regular', return_value=b'N\n'):
            system.load()
            with patch.object(Path, 'exists', side_effect=[True, False]): system.unload()
        self.assertEqual(calls, [('/usr/sbin/insmod', '/lib/modules/'+admin.KERNEL+'/updates/dkms/rp1_gpclk_dkms.ko', 'live_output=0'),
                                 ('/usr/sbin/rmmod', 'rp1_gpclk_dkms')])
        self.assertFalse(any('force' in token or token in ('-f', '--force') for argv in calls for token in argv))

    def test_persistent_mask_precedes_commands_and_survives_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            system = object.__new__(admin.Linux)
            system.check_inhibit = lambda: None
            events = []
            def command(argv):
                self.assertEqual(os.readlink(directory/'wsprrypi.service'), '/dev/null')
                self.assertEqual(events[0], 'directory-fsync')
                events.append(argv)
                if 'stop' in argv:
                    raise ValueError('stop failed')
            with patch.object(admin, 'UNIT_DIR', directory), \
                 patch.object(admin, 'safe_directory'), \
                 patch.object(admin, 'fsync_dir', side_effect=lambda path: events.append('directory-fsync')), \
                 patch.object(admin, 'run', side_effect=command):
                with self.assertRaises(ValueError): system.inhibit()
            self.assertTrue((directory/'wsprrypi.service').is_symlink())
            self.assertEqual(events[1:], [('/usr/bin/systemctl', 'daemon-reload'),
                                         ('/usr/bin/systemctl', 'stop', 'wsprrypi.service')])
            (directory/'wsprrypi.service').unlink()
            (directory/'wsprrypi.service').write_text('foreign unit')
            with patch.object(admin, 'UNIT_DIR', directory), patch.object(admin, 'safe_directory'):
                with self.assertRaises(ValueError): system.inhibit()
            self.assertEqual((directory/'wsprrypi.service').read_text(), 'foreign unit')

    def test_journal_real_atomic_replace_and_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            system = object.__new__(admin.Linux)
            directory = Path(tmp)
            with patch.object(admin, 'STATE', directory), patch.object(admin, 'fsync_dir') as sync:
                system.write_journal({'phase': 'before'})
                self.assertEqual((directory/'transaction.json').stat().st_mode & 0o777, 0o600)
                sync.assert_called_once_with(directory)
                before = (directory/'transaction.json').read_bytes()
                with patch.object(admin.os, 'replace', side_effect=OSError('interrupted')):
                    with self.assertRaises(OSError): system.write_journal({'phase': 'after'})
                self.assertEqual((directory/'transaction.json').read_bytes(), before)
                self.assertEqual([p.name for p in directory.iterdir()], ['transaction.json'])

    def test_unrelated_generations_and_malformed_observation_refused(self):
        for change in ('generation', 'observation', 'request', 'target'):
            machine = Machine(); admin.execute(machine, 1)
            if change == 'generation': machine.value['generation'] += 2
            elif change == 'observation': machine.journal['observation']['generation'] = True
            elif change == 'request': machine.journal['request'] = 'not-a-uuid'
            else: machine.journal['target'] = True
            count = len(machine.events)
            with self.assertRaises(ValueError): admin.execute(machine, recover=True)
            self.assertEqual(len(machine.events), count)
        with self.assertRaises(ValueError): admin.strict_json('{"x":1,"x":2}')

    def test_crashes_during_route_replacement(self):
        base = Machine(); admin.execute(base, 1); base.events = []
        sample = copy.deepcopy(base); admin.execute(sample, 2)
        for point in range(1, len(sample.events)+1):
            machine = copy.deepcopy(base); machine.crash = point
            with self.assertRaises(OSError): admin.execute(machine, 2)
            machine.crash = None
            result = admin.execute(machine, recover=True)
            self.assertEqual(result['id'], 0)
            self.assertTrue(machine.mask)

    def test_external_route_change_during_consumer_lifecycle_stops(self):
        for stage in ('load', 'unload'):
            machine = Machine()
            original = getattr(machine, stage)
            def altered():
                original()
                machine.value['generation'] += 1
            setattr(machine, stage, altered)
            with self.assertRaises(ValueError): admin.execute(machine, 1)
            self.assertTrue(machine.mask)
            self.assertNotEqual(machine.journal['phase'], 'complete-inhibited')

    def test_actual_bounded_command_runner(self):
        self.assertEqual(admin.run((sys.executable, '-c', 'print("ok")')), 'ok')
        with self.assertRaises(ValueError): admin.run((sys.executable, '-c', 'print("x"*70000)'))
        with self.assertRaises(ValueError): admin.run((sys.executable, '-c', 'raise SystemExit(7)'))

    def test_retained_fault_never_recovers_to_success(self):
        machine = Machine(); machine.apply_error = -5
        with self.assertRaises(ValueError): admin.execute(machine, 1)
        with self.assertRaises(ValueError): admin.execute(machine, recover=True)
        self.assertEqual(machine.value['id'], 0)
        self.assertTrue(machine.value['flags'] & admin.FAULT)
        self.assertTrue(machine.mask)

    def test_ioctl_encoding_and_error_response(self):
        self.assertEqual(admin.FORMAT.size, 64)
        system = object.__new__(admin.Linux); system.fd = 99
        def ioctl(fd, command, data, mutate):
            self.assertEqual((fd, command, mutate), (99, 0xc040b801, True))
            self.assertEqual(admin.FORMAT.unpack(data)[:6], (1, 2, 0, 0, 7, 8))
            data[:] = admin.FORMAT.pack(1, 0, 0, 0, 7, 9, 12, -16, 1, 5, 0, 0)
        with patch.object(admin.fcntl, 'ioctl', side_effect=ioctl):
            result = system.call(admin.REMOVE, before={'session': 7, 'generation': 8})
        self.assertEqual(result['error'], -16)
        self.assertEqual(result['id'], 12)


if __name__ == '__main__':
    unittest.main()
