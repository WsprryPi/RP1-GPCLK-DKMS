#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Offline tests for runtime reconciliation; no target effects."""
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import runtime_output as output
import runtime_manager as manager
import runtime_controller_admin as admin
from check_runtime_manager import System

class Machine(System):
    def __init__(self):
        super().__init__()
        admin.execute(self, 2)
        self.snapshot = dict(route=2, compatibility=2, fault=1, owner=1,
            lease=1, live=1, eligible=2, gpio=2, clock=2, dma=2, stable=2)
    def output_snapshot(self): return self.snapshot.copy()
    def output_resume(self): self.check_inhibit(); self.mask = False

class Tests(unittest.TestCase):
    def request(self, machine, operation='idle', **extra):
        return manager._dispatch(dict(schemaVersion=3, operation=operation, route='gpio20', **extra), lambda:machine)
    def test_idle_and_operation_reconcile_do_not_authorize_or_change_route(self):
        machine = Machine()
        before = copy.deepcopy(machine.value)
        for operation in ('idle','reconcile-output'):
            result = self.request(machine, operation)['state']['outputLifecycle']
            self.assertTrue(result['ready'])
            self.assertFalse(result['executionAuthorized'])
            self.assertEqual(machine.value, before)
            self.assertTrue(machine.mask)
    def test_busy_fault_unknown_and_route_mismatch(self):
        for key in ('fault','owner','lease','live','eligible','gpio','clock','dma','stable','route','compatibility'):
            machine = Machine(); machine.snapshot[key] = 0
            with self.assertRaises(ValueError, msg=key): self.request(machine)
    def test_journal_identity_and_pending_effects(self):
        for key, value in [('boot','stale'),('session',0),('binding','stale'),('phase','remove-intent'),('observation',{})]:
            machine = Machine(); machine.journal[key] = value
            with self.assertRaises(ValueError, msg=key): self.request(machine)
    def test_explicit_resume_only_releases_mask(self):
        machine = Machine(); before = machine.value.copy()
        with self.assertRaises(ValueError): self.request(machine, 'resume')
        result = self.request(machine, 'resume', execute=True)
        self.assertFalse(result['state']['applicationInhibited'])
        self.assertFalse(result['state']['outputLifecycle']['executionAuthorized'])
        self.assertEqual(machine.value, before)
    def test_no_legacy_mutation_translation_or_extra_fields(self):
        for value in (dict(schemaVersion=1,operation='idle',route='gpio20'),
                      dict(schemaVersion=3,operation='idle',route='gpio20',execute=True)):
            with self.assertRaises(ValueError): manager._dispatch(value, Machine)

if __name__ == '__main__': unittest.main()
