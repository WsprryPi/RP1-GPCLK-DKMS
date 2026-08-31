#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Public manager workflow with real journals/drop-ins and fake system effects."""
import contextlib
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import runtime_application as app
import runtime_controller_admin as admin
import runtime_manager as manager
from check_runtime_controller import Machine


class System(Machine):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.active = True
        self.masked = False
        self.loaded = True
        self.locked = False
        self.configured = 'gpio4'
        self.started = 0
        self.fail = None
        self.pid = 321

    def __enter__(self):
        assert not self.locked, 'startup would deadlock on manager lock'
        self.locked = True
        return self

    def __exit__(self, *args): self.locked = False
    def read_record(self, name):
        path = self.root/name
        return json.loads(path.read_text()) if path.exists() else None
    write_record = admin.Linux.write_record
    def read_journal(self): return self.read_record('transaction.json')
    def write_journal(self, value): self.write_record('transaction.json', value)
    def read_manager_record(self): return self.read_record('manager.json')
    def write_manager_record(self, value): self.write_record('manager.json', value)
    def inhibit(self):
        app.write_owned(app.unit_file(app.DROPIN), app.INHIBIT)
        self.active = False
        self.mask = True
        self.event('inhibit')
    def check_inhibit(self):
        assert not self.active
        assert app.unit_file(app.DROPIN).read_bytes() == app.INHIBIT
    def inhibited(self): return app.unit_file(app.DROPIN).exists() and not self.active
    def output_snapshot(self):
        return dict(route=self.value['route'], compatibility=2, fault=1, owner=1,
                    lease=1, live=1, eligible=2, gpio=2, clock=2, dma=2, stable=2)
    def observation(self):
        return dict(LoadState='masked' if self.masked else ('loaded' if self.loaded else 'not-found'),
                    ActiveState='active' if self.active else 'inactive',
                    UnitFileState='masked' if self.masked else 'enabled', MainPID=str(self.pid if self.active else 0))
    def helper(self, operation, *args):
        if self.fail == operation:
            raise ValueError('injected '+operation)
        if operation == 'configure':
            assert not self.active
            self.configured = args[0]
        return dict(contract='wsprrypi-route-application-v1', route=self.configured, transmit=False)
    def command(self, argv):
        if 'start' in argv:
            assert not self.locked
            assert not app.unit_file(app.DROPIN).exists()
            self.started += 1
            if self.fail == 'start': raise ValueError('injected start')
            self.active = True
            record = self.read_record('application.json')
            # An independent startup connection exercises public dispatch while
            # the mutation workflow is alive but its controller lock is released.
            manager.dispatch(dict(schemaVersion=3, operation='idle', route=self.configured), lambda:self)
            manager.dispatch(dict(schemaVersion=3, operation='application-ready', route=self.configured,
                token=record['token'], pid=self.pid, transmit=False), lambda:self)
        return ''


class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.system = System(root)
        self.stack = contextlib.ExitStack()
        for obj, name, value in (
            (admin,'STATE',root), (admin,'UNIT_DIR',root),
            (admin,'safe_directory',lambda path:None), (admin,'fsync_dir',lambda path:None),
            (admin,'read_regular',lambda path,*args:Path(path).read_bytes()),
            (admin,'run',self.system.command), (app,'service',self.system.observation),
            (app,'helper',self.system.helper), (app,'mutation_lock',contextlib.nullcontext)):
            self.stack.enter_context(patch.object(obj, name, value))
    def tearDown(self):
        self.stack.close()
        self.tmp.cleanup()
    def dispatch(self, value): return manager.dispatch(value, lambda:self.system)
    def switch(self, route='gpio20', ident='request-0001'):
        checked = self.dispatch(dict(schemaVersion=3, operation='preflight', route=route))
        return self.dispatch(dict(schemaVersion=3, operation='switch', route=route,
            requestId=ident, actor='offline.test', execute=True, preflightToken=checked['state']['preflightToken']))
    def test_running_application_restored_and_requester_not_required(self):
        result = self.switch()
        self.assertEqual(result['status'], 'restored')
        self.assertTrue(self.system.active)
        self.assertEqual(self.system.configured, 'gpio20')
        self.assertEqual(self.system.started, 1)
        self.assertFalse(app.unit_file(app.DROPIN).exists())
        self.assertFalse(app.unit_file(app.IDLE_DROPIN).exists())
        self.assertEqual(self.dispatch(dict(schemaVersion=3,operation='query'))['state']['application']['phase'], 'restored')
    def test_stopped_and_administrator_masked_are_not_started(self):
        for masked in (False, True):
            with self.subTest(masked=masked):
                self.system.active = False
                self.system.masked = masked
                result = self.switch(ident='request-'+str(masked)+'-0001')
                self.assertEqual(result['status'], 'administrator-masked' if masked else 'stopped')
                self.assertEqual(self.system.started, 0)
                self.assertEqual(self.system.masked, masked)
                self.assertTrue(app.unit_file(app.IDLE_DROPIN).exists())
    def test_missing_and_foreign_service_are_not_overwritten(self):
        self.system.loaded = False
        with self.assertRaises(ValueError): self.switch()
        self.assertFalse(self.system.events)
        self.assertIsNone(self.system.read_record('application.json'))
    def test_removal_error_preserves_errno_and_id(self):
        self.switch()
        self.system.remove_error = -16
        result = self.switch('gpio4', 'request-0002')
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['error']['kernelError'], -16)
        self.assertEqual(result['error']['overlayId'], 9)
        self.assertEqual(self.system.configured, 'gpio20')
        self.assertFalse(self.system.active)
    def test_configuration_and_restart_failure_can_restore_without_overlay_effects(self):
        for failure in ('configure', 'start'):
            with self.subTest(failure=failure):
                self.system.fail = failure
                result = self.switch(ident='request-'+failure+'-0001')
                self.assertEqual(result['error']['code'], 'application-restoration-failed')
                before = copy.deepcopy(self.system.value)
                self.assertFalse(self.system.active)
                self.system.fail = None
                result = self.dispatch(dict(schemaVersion=3, operation='restore', execute=True))
                self.assertEqual(result['status'], 'restored')
                self.assertEqual(self.system.value, before)
    def test_foreign_dropin_survives(self):
        path = app.unit_file(app.DROPIN)
        path.parent.mkdir()
        path.write_bytes(b'foreign')
        with self.assertRaises(ValueError): self.switch()
        self.assertEqual(path.read_bytes(), b'foreign')
        self.assertTrue(self.system.active)
    def test_stale_ack_and_pending_output_are_rejected(self):
        self.system.fail = 'start'
        self.switch()
        with self.assertRaises(ValueError):
            self.dispatch(dict(schemaVersion=3,operation='reconcile-output',route='gpio20'))
        with self.assertRaises(ValueError):
            self.dispatch(dict(schemaVersion=3,operation='application-ready',route='gpio20',token='a'*36,pid=321,transmit=False))
    def test_prior_boot_restoration_does_not_start(self):
        self.system.fail = 'start'
        self.switch()
        self.system.boot = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
        with self.assertRaises(ValueError):
            self.dispatch(dict(schemaVersion=3,operation='restore',execute=True))
        self.assertFalse(self.system.active)

    def test_every_durable_journal_boundary_has_a_recovery_path(self):
        class Crash(BaseException): pass
        writes = []
        original = self.system.write_record
        def trace(name, value):
            original(name, value)
            writes.append((name, value.get('phase')))
        with patch.object(self.system, 'write_record', trace):
            self.switch()
        for boundary in range(1, len(writes)+1):
            with self.subTest(boundary=boundary, write=writes[boundary-1]):
                self.tearDown()
                self.setUp()
                original = self.system.write_record
                count = 0
                def crash(name, value):
                    nonlocal count
                    original(name, value)
                    count += 1
                    if count == boundary: raise Crash()
                with patch.object(self.system, 'write_record', crash):
                    with self.assertRaises(Crash): self.switch()
                record = self.system.read_record('application.json')
                journal = self.system.read_journal()
                if journal and journal['phase'] == 'complete-inhibited' and self.system.value['route'] == 2:
                    result = self.dispatch(dict(schemaVersion=3, operation='restore', execute=True))
                else:
                    result = self.dispatch(dict(schemaVersion=3, operation='recover', execute=True,
                        requestId='recovery-0001', actor='offline.test'))
                    self.assertNotEqual(result['status'], 'error')
                    result = self.switch(ident='request-0002')
                self.assertEqual(result['status'], 'restored', record)
                self.assertTrue(self.system.active)
                self.assertEqual(self.system.configured, 'gpio20')

    def test_stopped_first_start_acknowledgement_removes_only_owned_override(self):
        self.system.active = False
        self.switch()
        self.system.active = True
        record = self.system.read_record('application.json')
        self.dispatch(dict(schemaVersion=3,operation='application-ready',route='gpio20',
            token=record['token'],pid=self.system.pid,transmit=False))
        self.assertFalse(app.unit_file(app.IDLE_DROPIN).exists())
        self.assertEqual(self.system.read_record('application.json')['phase'], 'restored')

    def test_real_mutation_lock_excludes_a_second_worker(self):
        # Re-enable the real lock, replacing only its root-owner observation.
        self.stack.close()
        with patch.object(admin, 'STATE', Path(self.tmp.name)), patch.object(admin, 'safe_directory'), patch.object(os, 'fstat', return_value=type('Info', (), {'st_uid':0, 'st_mode':0o100600})()):
            with app.mutation_lock():
                with self.assertRaises(BlockingIOError):
                    with app.mutation_lock(): pass

    def test_first_switch_after_deployment_inhibition(self):
        self.system.inhibit()
        self.assertEqual(self.switch()['status'], 'stopped')
        self.assertFalse(app.unit_file(app.DROPIN).exists())

    def test_recover_second_switch_preserves_prior_idle_override_ownership(self):
        self.system.active = False
        self.switch()
        self.system.fail = 'configure'
        self.assertEqual(self.switch('gpio4', 'request-0002')['status'], 'error')
        result = self.dispatch(dict(schemaVersion=3,operation='recover',execute=True,
            requestId='recover-0001',actor='offline.test'))
        self.assertNotEqual(result['status'], 'error')
        self.system.fail = None
        self.assertEqual(self.switch(ident='request-0003')['status'], 'stopped')

    def test_malformed_application_journal_is_not_used_for_service_effects(self):
        self.switch()
        record = self.system.read_record('application.json')
        record['token'] = 'token\nExecStart=/foreign'
        self.system.write_record('application.json', record)
        before = list(self.system.events)
        with self.assertRaises(ValueError):
            self.dispatch(dict(schemaVersion=3,operation='restore',execute=True))
        self.assertEqual(self.system.events, before)

    def test_process_exit_after_acknowledgement_is_not_reported_as_restored(self):
        def observation():
            value = self.system.observation()
            record = self.system.read_record('application.json')
            if self.system.locked and record and record['ready']:
                value.update(ActiveState='inactive', MainPID='0')
            return value
        with patch.object(app, 'service', observation):
            result = self.switch()
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['error']['code'], 'application-restoration-failed')
        self.assertTrue(self.system.inhibited())


if __name__ == '__main__': unittest.main()
