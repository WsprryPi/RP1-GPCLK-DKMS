#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Hardware-free neutral activation, idempotency, and recovery tests."""
import contextlib
import copy
import json
from pathlib import Path
import stat
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import runtime_activation as activation
import runtime_binding
import runtime_controller_admin as admin
import runtime_deployment as deployment


def captured(active=True, masked=False):
    return {'version': 1, 'wasActive': active, 'administratorMasked': masked,
        'service': {'LoadState': 'masked' if masked else 'loaded',
            'ActiveState': 'active' if active else 'inactive',
            'UnitFileState': 'masked' if masked else 'enabled',
            'MainPID': '42' if active else '0'},
        'companion': {'contract': 'wsprrypi-route-application-v1',
            'route': 'gpio4', 'transmit': False,
            'config': '/usr/local/etc/wsprrypi.ini'}}


class System:
    def __init__(self, application=None):
        self.app = application or captured()
        self.binding_value = {'schemaVersion': 2, 'contract': runtime_binding.CONTRACT,
            'productVersion': runtime_binding.PRODUCT_VERSION,
            'compatibilityIdentities': runtime_binding.COMPATIBILITY,
            'sourceCommit': 'a' * 40, 'kernel': admin.KERNEL,
            'files': {path: admin.digest(path.encode()) for path in deployment.INVENTORY},
            'externalFiles': {path: 'b' * 64 for path in runtime_binding.EXTERNAL_PATHS},
            'uapiSha256': {}, 'controllerNoteSha256': 'c' * 64,
            'consumerNoteSha256': 'd' * 64}
        self.binding_value['uapiSha256'] = {
            'consumer': self.binding_value['files'][
                '/usr/lib/rp1-gpclk-dkms/runtime-uapi/rp1_gpclk.h'],
            'controller': self.binding_value['files'][
                '/usr/lib/rp1-gpclk-dkms/runtime-uapi/rp1_route_admin.h']}
        self.binding_value['artifactSetSha256'] = runtime_binding.canonical_digest(
            self.binding_value)
        self.raw = json.dumps(self.binding_value, sort_keys=True).encode()
        records = {path: {'before': None, 'after': deployment.encode(b'x')}
                   for path in deployment.DESTINATIONS}
        records[deployment.BINDING]['after'] = deployment.encode(self.raw)
        self.deployed = {'version': 2, 'application': copy.deepcopy(self.app),
                         'previousDeployment': None,
                         'files': records}
        self.deployment_raw = (json.dumps(self.deployed, sort_keys=True) + '\n').encode()
        self.journal = None
        self.records = {}
        self.controller = False
        self.consumer = False
        self.controller_open = False
        self.consumer_endpoint = False
        self.socket_active = False
        self.inhibited = True
        self.application_active = False
        self.boot_id = '00000000-0000-0000-0000-000000000001'
        self.state = {'session': 7, 'generation': 0, 'id': 0,
                      'error': 0, 'route': 0, 'flags': 0}
        self.events = []
        self.archives = []
        self.fail = None
        self.socket_unsafe = False
        self.unit_drift = False
        self.note_drift = False

    def read_record(self, path):
        return copy.deepcopy(self.journal if Path(path).name == 'activation.json'
                             else self.records.get(Path(path).name))
    def write_journal(self, value):
        activation.validate_journal(value)
        self.journal = copy.deepcopy(value); self.events.append('journal:' + value['phase'])
    def archive_journal(self, value): self.archives.append(copy.deepcopy(value))
    def retire_journal(self, expected):
        if self.journal != expected:
            raise ValueError('prior activation changed before retirement')
        self.events.append('retire-activation')
        self.journal = None
    def boot(self): return self.boot_id
    def binding(self): return self.raw, copy.deepcopy(self.binding_value)
    def last_deployment(self, raw):
        if raw != self.raw: raise ValueError('binding drift')
        return self.deployment_raw, copy.deepcopy(self.deployed)
    def module(self, name, note):
        loaded = self.controller if name == 'rp1_route_controller' else self.consumer
        return ({'status': 'loaded', 'buildNoteSha256': ('0' * 64 if self.note_drift else note),
                 'exact': not self.note_drift}
                if loaded else {'status': 'absent'})
    def endpoint(self, path, unused):
        if path == '/dev/rp1-route-admin' and self.controller:
            return {'status': 'owned', 'open': self.controller_open}
        if path == '/dev/rp1-gpclk' and self.consumer_endpoint:
            return {'status': 'owned', 'open': self.controller_open}
        return {'status': 'absent', 'open': False}
    def service(self, name):
        if name == activation.SOCKET_UNIT:
            return {'load': 'loaded', 'active': 'active' if self.socket_active else 'inactive',
                'enabled': 'enabled',
                'fragment': ('/tmp/foreign.socket' if self.unit_drift else
                    '/usr/lib/systemd/system/rp1-gpclk-route-manager.socket'),
                'MainPID': '0'}
        if name == activation.SERVICE_UNIT:
            return {'load': 'loaded', 'active': 'inactive', 'enabled': 'static',
                'fragment': '/usr/lib/systemd/system/rp1-gpclk-route-manager@.service',
                'MainPID': '0'}
        return {'load': 'masked' if self.app['administratorMasked'] else 'loaded',
            'active': 'active' if self.application_active else 'inactive',
            'enabled': 'masked' if self.app['administratorMasked'] else 'enabled',
            'fragment': '/usr/lib/systemd/system/wsprrypi.service',
            'MainPID': self.app['service']['MainPID'] if self.application_active else '0'}
    def manager_socket(self):
        return {'status': ('unsafe' if self.socket_unsafe else 'owned')
                if self.socket_active else 'absent'}
    def inhibitor(self): return self.inhibited
    def controller_state(self): return copy.deepcopy(self.state)
    def load_controller(self):
        self.events.append('load-controller')
        if self.fail == 'load': raise ValueError('load failed')
        self.controller = True
    def unload_controller(self): self.events.append('unload-controller'); self.controller = False
    def start_socket(self):
        self.events.append('start-socket')
        if self.fail == 'socket': raise ValueError('socket failed')
        self.socket_active = True
    def stop_socket(self): self.events.append('stop-socket'); self.socket_active = False
    def manager_query(self):
        self.events.append('manager-query')
        if self.fail == 'manager': raise ValueError('manager failed')
        return {'status': 'ok', 'state': {'activeRoute': None,
            'controller': copy.deepcopy(self.state),
            'bindingSha256': admin.digest(self.raw)}}
    def restore_application(self, record):
        self.events.append('restore-application')
        if self.fail == 'restore': raise ValueError('restore failed')
        self.inhibited = False
        self.application_active = record['wasActive']
        phase = ('restored' if record['wasActive'] else
                 'administrator-masked' if record['administratorMasked'] else 'stopped')
        return {'phase': phase, 'service': record['service'], 'companion': record['companion']}
    def inhibit_application(self):
        self.events.append('inhibit-application'); self.inhibited = True
        self.application_active = False
        if self.fail == 'inhibit-after':
            raise ValueError('inhibition interrupted after service stop')
        if self.fail == 'journal-drift-after-inhibit':
            self.journal['requestId'] = '00000000-0000-0000-0000-000000000099'
        if self.fail == 'transaction-after-inhibit':
            self.records['transaction.json'] = {'pending': True}

    def capture_application(self):
        result = copy.deepcopy(self.app)
        result['wasActive'] = self.application_active
        result['service']['ActiveState'] = ('active' if self.application_active
                                            else 'inactive')
        result['service']['MainPID'] = (self.app['service']['MainPID']
                                        if self.application_active else '0')
        return result


def lock():
    return contextlib.nullcontext()


class Tests(unittest.TestCase):
    def test_linux_controller_status_uses_and_requires_reserved0_zero(self):
        system = activation.Linux()
        def ioctl(fd, command, data, mutate):
            self.assertEqual((fd, command, mutate), (99, admin.IOCTL, True))
            self.assertEqual(admin.FORMAT.unpack(data),
                (0, admin.STATUS, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
            data[:] = admin.FORMAT.pack(0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0)
        device = SimpleNamespace(st_mode=stat.S_IFCHR | 0o600, st_uid=0, st_gid=0)
        with patch.object(activation.os, 'open', return_value=99), \
             patch.object(activation.os, 'fstat', return_value=device), \
             patch.object(activation.os, 'close'), \
             patch.object(activation.fcntl, 'ioctl', side_effect=ioctl):
            self.assertEqual(system.controller_state(),
                {'session': 7, 'generation': 0, 'id': 0,
                 'error': 0, 'route': 0, 'flags': 0})

    def test_linux_controller_status_rejects_nonzero_reserved0_response(self):
        system = activation.Linux()
        def ioctl(unused_fd, unused_command, data, unused_mutate):
            data[:] = admin.FORMAT.pack(1, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0)
        device = SimpleNamespace(st_mode=stat.S_IFCHR | 0o600, st_uid=0, st_gid=0)
        with patch.object(activation.os, 'open', return_value=99), \
             patch.object(activation.os, 'fstat', return_value=device), \
             patch.object(activation.os, 'close'), \
             patch.object(activation.fcntl, 'ioctl', side_effect=ioctl):
            with self.assertRaisesRegex(ValueError, 'response schema'):
                system.controller_state()

    def test_linux_observes_main_pid_only_for_application_service(self):
        outputs = {
            activation.SOCKET_UNIT:
                'LoadState=loaded\nActiveState=inactive\nUnitFileState=disabled\n'
                'FragmentPath=/usr/lib/systemd/system/'
                'rp1-gpclk-route-manager.socket\n',
            admin.ROUTE_MANAGER_TEMPLATE_PROBE:
                'LoadState=loaded\nActiveState=inactive\nUnitFileState=static\n'
                'FragmentPath=/usr/lib/systemd/system/'
                'rp1-gpclk-route-manager@.service\n',
            activation.APPLICATION_UNIT:
                'MainPID=0\nLoadState=loaded\nActiveState=inactive\n'
                'UnitFileState=enabled\n'
                'FragmentPath=/etc/systemd/system/wsprrypi.service\n',
        }
        commands = []
        def observe(argv):
            commands.append(argv)
            return outputs[argv[2]]
        system = object.__new__(activation.Linux)
        with patch.object(admin, 'run', side_effect=observe):
            socket = system.service(activation.SOCKET_UNIT)
            manager = system.service(activation.SERVICE_UNIT)
            application = system.service(activation.APPLICATION_UNIT)
        self.assertNotIn('MainPID', socket)
        self.assertNotIn('MainPID', manager)
        self.assertEqual(application['MainPID'], '0')
        self.assertNotIn('MainPID', commands[0][-1])
        self.assertNotIn('MainPID', commands[1][-1])
        self.assertIn('MainPID', commands[2][-1])
        outputs[activation.APPLICATION_UNIT] = outputs[
            activation.APPLICATION_UNIT].replace('MainPID=0\n', '')
        with patch.object(admin, 'run', side_effect=observe):
            with self.assertRaisesRegex(ValueError, 'service observation'):
                system.service(activation.APPLICATION_UNIT)
        with patch.object(admin, 'run') as command:
            with self.assertRaisesRegex(ValueError, 'unsupported activation service'):
                system.service('foreign.service')
        command.assert_not_called()

    def test_plan_and_successful_neutral_activation(self):
        system = System()
        plan = activation.activation_plan(system)
        result = activation.ensure(system, plan, activation.plan_digest(plan), lock)
        self.assertEqual(result['status'], 'activated-neutral')
        self.assertTrue(activation.neutral_ready(activation.observe(system)))
        self.assertFalse(system.consumer)
        self.assertEqual(system.state['route'], 0)
        self.assertNotIn('load-consumer', system.events)

    def test_exact_repeat_is_true_noop(self):
        system = System(); plan = activation.activation_plan(system)
        activation.ensure(system, plan, activation.plan_digest(plan), lock)
        before = copy.deepcopy(system.events)
        repeated = activation.activation_plan(system)
        result = activation.ensure(system, repeated, activation.plan_digest(repeated), lock)
        self.assertEqual(result['status'], 'idempotent-no-change')
        self.assertEqual(system.events, before)

    def test_completed_neutral_activation_can_restart_after_clean_reboot(self):
        system = System(); initial = activation.activation_plan(system)
        activation.ensure(system, initial, activation.plan_digest(initial), lock)
        prior = copy.deepcopy(system.journal)
        system.boot_id = '00000000-0000-0000-0000-000000000002'
        system.controller = False
        system.socket_active = False
        plan = activation.activation_plan(system)
        self.assertEqual(plan['version'], 2)
        self.assertEqual(plan['activationContext'], 'post-reboot')
        self.assertFalse(plan['applicationInhibited'])
        self.assertEqual(plan['previousActivationSha256'],
                         admin.digest(activation.canonical(prior)))
        result = activation.ensure(system, plan, activation.plan_digest(plan), lock)
        self.assertEqual(result['status'], 'activated-neutral')
        self.assertEqual(system.archives, [prior])
        self.assertTrue(activation.neutral_ready(activation.observe(system)))
        self.assertFalse(system.consumer)

    def test_prior_boot_terminal_activation_can_be_retired_for_migration(self):
        system = System(); initial = activation.activation_plan(system)
        activation.ensure(system, initial, activation.plan_digest(initial), lock)
        for name in ('activationContext', 'applicationInhibited'):
            system.journal['plan'].pop(name)
        system.journal['plan']['version'] = 1
        system.journal['planSha256'] = activation.plan_digest(system.journal['plan'])
        prior = copy.deepcopy(system.journal)
        system.boot_id = '00000000-0000-0000-0000-000000000002'
        system.controller = False
        system.socket_active = False
        plan = activation.retirement_plan(system)
        self.assertEqual(plan['operation'], 'retire-post-reboot-activation')
        self.assertEqual(plan['activationJournalSha256'],
                         admin.digest(activation.canonical(prior)))
        result = activation.retire(system, plan, activation.plan_digest(plan), lock)
        self.assertEqual(result['status'], 'retired-post-reboot-activation')
        self.assertEqual(system.archives, [])
        self.assertIsNone(system.journal)

    def test_post_reboot_retirement_rejects_drift_before_effects(self):
        system = System(); initial = activation.activation_plan(system)
        activation.ensure(system, initial, activation.plan_digest(initial), lock)
        system.boot_id = '00000000-0000-0000-0000-000000000002'
        system.controller = False
        system.socket_active = False
        plan = activation.retirement_plan(system)
        system.journal['requestId'] = '00000000-0000-0000-0000-000000000099'
        with self.assertRaisesRegex(ValueError, 'changed since review'):
            activation.retire(system, plan, activation.plan_digest(plan), lock)
        self.assertNotIn('retire-activation', system.events)
        self.assertEqual(system.archives, [])

    def test_same_boot_terminal_activation_cannot_be_retired(self):
        system = System(); initial = activation.activation_plan(system)
        activation.ensure(system, initial, activation.plan_digest(initial), lock)
        with self.assertRaises(ValueError):
            activation.retirement_plan(system)

    def test_post_reboot_inhibition_interruption_is_safely_retryable(self):
        system = System(); initial = activation.activation_plan(system)
        activation.ensure(system, initial, activation.plan_digest(initial), lock)
        prior = copy.deepcopy(system.journal)
        system.boot_id = '00000000-0000-0000-0000-000000000002'
        system.controller = False
        system.socket_active = False
        system.fail = 'inhibit-after'
        plan = activation.activation_plan(system)
        with self.assertRaisesRegex(ValueError, 'inhibition interrupted'):
            activation.ensure(system, plan, activation.plan_digest(plan), lock)
        self.assertTrue(system.inhibited)
        self.assertFalse(system.application_active)
        self.assertEqual(system.journal, prior)
        system.fail = None
        retry = activation.activation_plan(system)
        self.assertEqual(retry['activationContext'], 'post-reboot')
        self.assertTrue(retry['applicationInhibited'])
        activation.ensure(system, retry, activation.plan_digest(retry), lock)
        self.assertTrue(activation.neutral_ready(activation.observe(system)))

    def test_post_reboot_inhibition_rechecks_journal_and_transactions(self):
        for failure in ('journal-drift-after-inhibit', 'transaction-after-inhibit'):
            with self.subTest(failure=failure):
                system = System(); initial = activation.activation_plan(system)
                activation.ensure(system, initial, activation.plan_digest(initial), lock)
                system.boot_id = '00000000-0000-0000-0000-000000000002'
                system.controller = False
                system.socket_active = False
                plan = activation.activation_plan(system)
                system.fail = failure
                with self.assertRaisesRegex(ValueError, 'exact inactive state'):
                    activation.ensure(system, plan, activation.plan_digest(plan), lock)
                self.assertFalse(system.controller or system.socket_active)
                self.assertEqual(system.archives, [])

    def test_post_reboot_reactivation_rejects_unsafe_or_changed_state(self):
        def rebooted():
            system = System(); plan = activation.activation_plan(system)
            activation.ensure(system, plan, activation.plan_digest(plan), lock)
            system.boot_id = '00000000-0000-0000-0000-000000000002'
            system.controller = False
            system.socket_active = False
            return system

        mutations = (
            lambda value: setattr(value, 'consumer', True),
            lambda value: setattr(value, 'consumer_endpoint', True),
            lambda value: setattr(value, 'controller', True),
            lambda value: setattr(value, 'socket_active', True),
            lambda value: value.records.update({'transaction.json': {'pending': True}}),
            lambda value: value.journal['manager']['state'].update(bindingSha256='0' * 64),
            lambda value: value.journal['application'].pop('service'),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                system = rebooted(); mutate(system)
                with self.assertRaises(ValueError):
                    activation.activation_plan(system)

    def test_post_reboot_plan_preserves_current_stopped_service_intent(self):
        system = System(); initial = activation.activation_plan(system)
        activation.ensure(system, initial, activation.plan_digest(initial), lock)
        system.boot_id = '00000000-0000-0000-0000-000000000002'
        system.controller = False
        system.socket_active = False
        system.application_active = False
        plan = activation.activation_plan(system)
        self.assertFalse(plan['application']['wasActive'])
        activation.ensure(system, plan, activation.plan_digest(plan), lock)
        self.assertFalse(system.application_active)
        self.assertTrue(activation.neutral_ready(activation.observe(system)))

    def test_same_boot_terminal_activation_still_requires_recovery(self):
        system = System(); plan = activation.activation_plan(system)
        activation.ensure(system, plan, activation.plan_digest(plan), lock)
        system.controller = False
        system.socket_active = False
        system.application_active = False
        system.inhibited = True
        with self.assertRaisesRegex(ValueError, 'evidence differs'):
            activation.activation_plan(system)

    def test_version_one_activation_plan_remains_valid(self):
        plan = activation.activation_plan(System())
        legacy = {name: value for name, value in plan.items()
                  if name not in ('activationContext', 'applicationInhibited')}
        legacy['version'] = 1
        self.assertEqual(activation.validate_plan(legacy), legacy)

    def test_version_two_activation_context_must_be_consistent(self):
        plan = activation.activation_plan(System())
        for field, value in (('activationContext', 'idempotent'),
                             ('applicationInhibited', False),
                             ('previousActivationSha256', '0' * 64)):
            with self.subTest(field=field):
                changed = copy.deepcopy(plan); changed[field] = value
                with self.assertRaisesRegex(ValueError, 'context'):
                    activation.validate_plan(changed)

    def test_malformed_completed_manager_evidence_fails_closed(self):
        system = System(); initial = activation.activation_plan(system)
        activation.ensure(system, initial, activation.plan_digest(initial), lock)
        system.boot_id = '00000000-0000-0000-0000-000000000002'
        system.controller = False
        system.socket_active = False
        system.journal['manager']['state'] = []
        with self.assertRaisesRegex(ValueError, 'evidence differs'):
            activation.activation_plan(system)

    def test_digest_and_plan_drift_fail_before_effects(self):
        system = System(); plan = activation.activation_plan(system)
        with self.assertRaisesRegex(ValueError, 'digest'):
            activation.ensure(system, plan, '0' * 64, lock)
        system.socket_active = True
        with self.assertRaisesRegex(ValueError, 'changed'):
            activation.ensure(system, plan, activation.plan_digest(plan), lock)
        self.assertNotIn('load-controller', system.events)

    def test_consumer_endpoint_open_controller_and_route_conflicts(self):
        mutations = (
            lambda value: setattr(value, 'consumer', True),
            lambda value: setattr(value, 'consumer_endpoint', True),
            lambda value: (setattr(value, 'controller', True),
                           setattr(value, 'controller_open', True)),
            lambda value: (setattr(value, 'controller', True),
                           value.state.update(route=1, id=9, flags=4)),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                system = System(); mutate(system)
                with self.assertRaises(ValueError): activation.activation_plan(system)

    def test_load_socket_manager_and_restoration_failures_retain_inhibition(self):
        for failure in ('load', 'socket', 'manager', 'restore'):
            with self.subTest(failure=failure):
                system = System(); system.fail = failure
                plan = activation.activation_plan(system)
                with self.assertRaises(ValueError):
                    activation.ensure(system, plan, activation.plan_digest(plan), lock)
                self.assertTrue(system.inhibited)
                self.assertEqual(system.journal['phase'], 'activation-failed')

    def test_stopped_and_administrator_masked_state_are_preserved(self):
        for record, phase in ((captured(False, False), 'stopped'),
                              (captured(False, True), 'administrator-masked')):
            with self.subTest(phase=phase):
                system = System(record); plan = activation.activation_plan(system)
                activation.ensure(system, plan, activation.plan_digest(plan), lock)
                self.assertEqual(system.journal['application']['phase'], phase)

    def test_recovery_unloads_only_neutral_controller_and_stops_owned_socket(self):
        system = System(); system.fail = 'manager'
        plan = activation.activation_plan(system)
        with self.assertRaises(ValueError):
            activation.ensure(system, plan, activation.plan_digest(plan), lock)
        system.fail = None
        reviewed = activation.recovery_plan(system)
        result = activation.ensure_recovery(system, reviewed,
            activation.plan_digest(reviewed), lock)
        self.assertEqual(result['status'], 'recovered-inhibited')
        self.assertFalse(system.controller or system.socket_active)
        self.assertTrue(system.inhibited)

    def test_recovery_handles_loaded_controller_when_initial_status_failed(self):
        system = System()
        plan = activation.activation_plan(system)
        system.controller = True
        system.journal = {'version': 1, 'plan': plan,
            'planSha256': activation.plan_digest(plan),
            'requestId': '00000000-0000-0000-0000-000000000002',
            'phase': 'activation-failed', 'controller': None, 'manager': None,
            'application': None, 'error': '[Errno 22] Invalid argument'}
        activation.validate_journal(system.journal)
        reviewed = activation.recovery_plan(system)
        result = activation.ensure_recovery(
            system, reviewed, activation.plan_digest(reviewed), lock)
        self.assertEqual(result['status'], 'recovered-inhibited')
        self.assertFalse(system.controller)
        self.assertTrue(system.inhibited)

    def test_recovery_rejects_active_route_and_boot_change(self):
        system = System(); system.fail = 'manager'; plan = activation.activation_plan(system)
        with self.assertRaises(ValueError):
            activation.ensure(system, plan, activation.plan_digest(plan), lock)
        system.fail = None; system.state.update(route=1, id=9, flags=4)
        reviewed = activation.recovery_plan(system)
        with self.assertRaisesRegex(ValueError, 'non-neutral'):
            activation.ensure_recovery(system, reviewed, activation.plan_digest(reviewed), lock)
        system = System(); system.fail = 'load'; plan = activation.activation_plan(system)
        with self.assertRaises(ValueError):
            activation.ensure(system, plan, activation.plan_digest(plan), lock)
        system.boot_id = '00000000-0000-0000-0000-000000000002'
        with self.assertRaisesRegex(ValueError, 'cross-boot'):
            activation.recovery_plan(system)

    def test_recovery_rejects_binding_deployment_and_controller_identity_drift(self):
        mutations = (
            lambda value: setattr(value, 'raw', value.raw + b' '),
            lambda value: setattr(value, 'deployment_raw', value.deployment_raw + b' '),
            lambda value: setattr(value, 'note_drift', True),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                system = System(); system.fail = 'manager'
                plan = activation.activation_plan(system)
                with self.assertRaises(ValueError):
                    activation.ensure(system, plan, activation.plan_digest(plan), lock)
                system.fail = None; mutate(system)
                with self.assertRaises(ValueError):
                    activation.recovery_plan(system)

    def test_malformed_journal_is_rejected(self):
        system = System(); system.journal = {'phase': 'complete-neutral'}
        with self.assertRaisesRegex(ValueError, 'journal schema'):
            activation.activation_plan(system)

    def test_pending_transactions_unit_socket_and_application_races_fail_closed(self):
        for name in ('deployment-pending.json', 'transaction.json', 'manager.json',
                     'application.json'):
            with self.subTest(record=name):
                system = System(); system.records[name] = {'pending': True}
                with self.assertRaisesRegex(ValueError, 'transaction'):
                    activation.activation_plan(system)
        system = System(); system.unit_drift = True
        with self.assertRaisesRegex(ValueError, 'unit identity'):
            activation.activation_plan(system)
        system = System(); system.socket_active = True; system.socket_unsafe = True
        with self.assertRaisesRegex(ValueError, 'socket identity'):
            activation.activation_plan(system)
        system = System(); system.application_active = True
        with self.assertRaisesRegex(ValueError, 'not stopped'):
            activation.activation_plan(system)

    def test_build_note_drift_after_load_and_foreign_exact_controller_are_rejected(self):
        system = System(); system.note_drift = True
        plan = activation.activation_plan(system)
        with self.assertRaisesRegex(ValueError, 'exact neutral'):
            activation.ensure(system, plan, activation.plan_digest(plan), lock)
        self.assertTrue(system.inhibited)
        system = System(); system.controller = True
        with self.assertRaisesRegex(ValueError, 'no completed activation ownership'):
            activation.activation_plan(system)

    def test_recovered_activation_can_restart_without_losing_evidence(self):
        system = System(); system.fail = 'manager'; plan = activation.activation_plan(system)
        with self.assertRaises(ValueError):
            activation.ensure(system, plan, activation.plan_digest(plan), lock)
        system.fail = None; recovery = activation.recovery_plan(system)
        activation.ensure_recovery(system, recovery, activation.plan_digest(recovery), lock)
        restart = activation.activation_plan(system)
        activation.ensure(system, restart, activation.plan_digest(restart), lock)
        self.assertEqual(len(system.archives), 1)
        self.assertTrue(activation.neutral_ready(activation.observe(system)))

    def test_controller_session_and_application_pid_drift_break_idempotency(self):
        system = System(); plan = activation.activation_plan(system)
        activation.ensure(system, plan, activation.plan_digest(plan), lock)
        system.state['session'] += 1
        with self.assertRaisesRegex(ValueError, 'recovery'):
            activation.activation_plan(system)
        system = System(); plan = activation.activation_plan(system)
        activation.ensure(system, plan, activation.plan_digest(plan), lock)
        system.app['service']['MainPID'] = '99'
        with self.assertRaisesRegex(ValueError, 'recovery'):
            activation.activation_plan(system)


if __name__ == '__main__':
    unittest.main()
