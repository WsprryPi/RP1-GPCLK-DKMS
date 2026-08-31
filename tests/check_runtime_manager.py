#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Hardware-free protocol/admin and durable deployment failure tests."""
import copy
import json
from pathlib import Path
import sys
import unittest
import tempfile
import os
import stat
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import runtime_manager as manager
import runtime_deployment as deploy
import runtime_controller_admin as admin
from check_runtime_controller import Machine


class System(Machine):
    def __init__(self):
        super().__init__()
        self.record = None
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def inhibited(self): return self.mask
    def read_manager_record(self): return copy.deepcopy(self.record)
    def write_manager_record(self, value): self.record = copy.deepcopy(value)


class Files:
    def __init__(self):
        self.values = {}
        self.count = 0
        self.crash = None
        self.mask = False
    def read(self, path): return self.values.get(path)
    def write(self, path, data):
        self.values[path] = data
        self.count += 1
        if self.count == self.crash:
            raise OSError('crash after durable write')
    def quiesce(self): self.mask = True
    def refresh(self): pass


class Tests(unittest.TestCase):
    def request(self, system, route='gpio4', ident='request-0001'):
        reply = manager.dispatch({'schemaVersion':3, 'operation':'preflight', 'route':route}, lambda:system)
        return {'schemaVersion':3, 'operation':'switch', 'route':route, 'execute':True,
                'actor':'offline.test', 'requestId':ident,
                'preflightToken':reply['state']['preflightToken']}

    def test_complete_switch_replay_recovery(self):
        system = System()
        request = self.request(system)
        first = manager.dispatch(request, lambda:system)
        self.assertEqual(first['status'], 'complete-inhibited')
        count = len(system.events)
        self.assertEqual(manager.dispatch(request, lambda:system), first)
        self.assertEqual(len(system.events), count)
        request = self.request(system, 'gpio20', 'request-0002')
        self.assertEqual(manager.dispatch(request, lambda:system)['state']['activeRoute'], 'gpio20')
        result = manager.dispatch({'schemaVersion':3,'operation':'recover','execute':True,
            'requestId':'recover-0001','actor':'offline.test'}, lambda:system)
        self.assertIsNone(result['state']['activeRoute'])
        self.assertTrue(system.mask)

    def test_error_ownership_preserved(self):
        system = System()
        manager.dispatch(self.request(system), lambda:system)
        system.remove_error = -16
        result = manager.dispatch(self.request(system, 'gpio20', 'request-0002'), lambda:system)
        self.assertEqual(result['error']['kernelError'], -16)
        self.assertEqual(result['error']['overlayId'], 9)
        self.assertTrue(system.mask)
        self.assertEqual(system.value['route'], 1)

    def test_stale_boot_and_conflict_rejected(self):
        system = System()
        request = self.request(system)
        system.value['generation'] += 1
        with self.assertRaises(ValueError): manager.dispatch(request, lambda:system)
        self.assertFalse(system.events)
        request = self.request(system)
        manager.dispatch(request, lambda:system)
        system.boot = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
        with self.assertRaises(ValueError): manager.dispatch(request, lambda:system)

    def test_legacy_effect_and_extra_fields_rejected(self):
        for operation in ('switch', 'apply-and-reboot', 'reconcile', 'recover'):
            with self.assertRaises(ValueError): manager.parse({'schemaVersion':1,'operation':operation})
        with self.assertRaises(ValueError): manager.parse({'schemaVersion':3,'operation':'query','execute':True})
        self.assertEqual(manager.parse({'schemaVersion':1,'operation':'query'})['schemaVersion'], 3)

    def test_every_deployment_crash_recovers_exact_old_bytes(self):
        values = {path:(None if path in deploy.JOURNALS else b'new') for path in deploy.DESTINATIONS}
        for crash in range(1, len(values)+4):
            files = Files()
            files.values = {path:b'old' for path in values}
            plan = deploy.plan(files, values)
            files.crash = crash
            try:
                deploy.apply(files, plan, deploy.plan_hash(plan))
            except OSError:
                files.crash = None
                deploy.apply(files, plan, deploy.plan_hash(plan), recover=True)
                self.assertTrue(all(files.read(path) == b'old' for path in values))
            self.assertIsNone(files.read(str(admin.STATE/'deployment-pending.json')))

    def test_real_atomic_files_restore_and_incomplete_barrier(self):
        with tempfile.TemporaryDirectory() as directory:
            backend = deploy.Files()
            # Only privilege/ancestor checks are replaced. Actual temporary-file,
            # fsync, rename and unlink implementations run in a disposable root.
            def read(path, limit=32*1024*1024):
                return Path(path).read_bytes()
            def sync(path):
                fd = os.open(path, os.O_RDONLY)
                try: os.fsync(fd)
                finally: os.close(fd)
            with patch.object(admin, 'safe_directory', lambda path: None), \
                 patch.object(admin, 'read_regular', read), \
                 patch.object(admin, 'fsync_dir', sync):
                path = str(Path(directory) / 'nested' / 'payload')
                backend.write(path, b'old')
                self.assertEqual(backend.read(path), b'old')
                backend.write(path, b'new')
                self.assertEqual(backend.read(path), b'new')
                backend.write(path, None)
                self.assertIsNone(backend.read(path))
                self.assertEqual(list(Path(path).parent.iterdir()), [])

    def test_only_trusted_system_library_alias_is_accepted(self):
        def info(path):
            return SimpleNamespace(st_uid=0, st_mode=(stat.S_IFLNK | 0o777) if str(path)=='/lib' else stat.S_IFDIR | 0o755)
        with patch.object(Path, 'lstat', info), patch.object(os, 'readlink', return_value='usr/lib'):
            admin.safe_directory(Path('/lib/modules/example/updates/dkms'))
        with patch.object(Path, 'lstat', info), patch.object(os, 'readlink', return_value='/tmp/foreign'):
            with self.assertRaises(ValueError): admin.safe_directory(Path('/lib/modules'))

    def test_replay_does_not_claim_lost_inhibition(self):
        system = System()
        request = self.request(system)
        manager.dispatch(request, lambda:system)
        system.mask = False
        with self.assertRaises(ValueError): manager.dispatch(request, lambda:system)

    def test_foreign_change_blocks_all_recovery(self):
        files = Files()
        values = {path:b'new' for path in deploy.DESTINATIONS}
        plan = deploy.plan(files, values)
        path = sorted(values)[0]
        files.values[path] = b'foreign'
        with self.assertRaises(ValueError): deploy.apply(files, plan, deploy.plan_hash(plan), recover=True)
        self.assertEqual(files.count, 0)
        with self.assertRaises(ValueError): deploy.apply(files, plan, '0'*64)


if __name__ == '__main__':
    unittest.main()
