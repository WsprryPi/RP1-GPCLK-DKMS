#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Hardware-free installer-facing readiness and ensure-contract tests."""
import copy
import json
from pathlib import Path
import stat
import sys
import unittest
from unittest.mock import patch
import contextlib
import io

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import runtime_binding as binding
import build_runtime_binding as build_binding
import build_runtime_bundle as bundle_builder
import runtime_provider as provider
from runtime_layout import INVENTORY, KERNEL


def exact_binding():
    value = {'schemaVersion': 2, 'contract': binding.CONTRACT,
        'productVersion': binding.PRODUCT_VERSION,
        'compatibilityIdentities': binding.COMPATIBILITY,
        'sourceCommit': 'a'*40, 'kernel': KERNEL,
        'files': {path: provider.admin.digest(path.encode()) for path in INVENTORY},
        'externalFiles': {name: 'b'*64 for name in binding.EXTERNAL_PATHS},
        'uapiSha256': {'consumer': provider.admin.digest(
            b'/usr/lib/rp1-gpclk-dkms/runtime-uapi/rp1_gpclk.h'),
            'controller': provider.admin.digest(
            b'/usr/lib/rp1-gpclk-dkms/runtime-uapi/rp1_route_admin.h')},
        'controllerNoteSha256': 'c'*64, 'consumerNoteSha256': 'd'*64}
    # Bind the declared UAPI hashes to the actual fixed inventory identities.
    value['uapiSha256']['consumer'] = value['files'][
        '/usr/lib/rp1-gpclk-dkms/runtime-uapi/rp1_gpclk.h']
    value['uapiSha256']['controller'] = value['files'][
        '/usr/lib/rp1-gpclk-dkms/runtime-uapi/rp1_route_admin.h']
    value['artifactSetSha256'] = binding.canonical_digest(value)
    return value


def controller(route=1, flags=6, error=0):
    return {'session': 1, 'generation': 2, 'id': 9 if route else 0,
            'error': error, 'route': route, 'flags': flags}


def manager_ready(route='gpio4'):
    number = {'gpio4': 1, 'gpio20': 2}[route]
    state = controller(number)
    transaction = {'version': 1, 'boot': 'boot', 'session': state['session'],
        'binding': 'e'*64, 'request': '00000000-0000-0000-0000-000000000001',
        'target': number, 'phase': 'complete-inhibited', 'observation': state}
    query = {'schemaVersion': 3, 'contract': 'rp1-gpclk-route-manager-runtime',
        'operation': 'query', 'status': 'ok', 'state': {'profile': 'runtime',
        'activeRoute': route, 'controller': state,
        'bootId': 'boot', 'bindingSha256': 'e'*64,
        'pendingTransaction': transaction,
        'application': {'phase': 'restored'}, 'applicationRestoration': True,
        'outputEnabled': False, 'qualification': False}}
    snapshot = {'route': number, 'compatibility': 2, 'fault': 1, 'owner': 1,
        'lease': 1, 'live': 1, 'eligible': 2, 'gpio': 2, 'clock': 2,
        'dma': 2, 'stable': 2}
    idle = {'schemaVersion': 3, 'contract': 'rp1-gpclk-route-manager-runtime',
        'operation': 'idle', 'status': 'ok', 'state': {'outputLifecycle': {
        'ready': True, 'executionAuthorized': False, 'snapshot': snapshot}}}
    return {'status': 'observed', 'query': query, 'idle': idle}


class Host:
    def __init__(self, ready=True):
        self.value = exact_binding()
        self._binding = {'status': 'valid', 'sha256': 'e'*64, 'value': self.value}
        self._artifacts = {path: {'status': 'exact', 'expectedSha256': sha,
            'actualSha256': sha} for path, sha in
            {**self.value['files'], **self.value['externalFiles']}.items()}
        self._journals = {name: {'status': 'absent'} for name in
            ('deployment-pending.json', 'transaction.json', 'manager.json',
             'application.json', 'activation.json')}
        self._modules = {
            'rp1_route_controller': {'status': 'loaded', 'version': '0.9.0',
                'buildNoteSha256': self.value['controllerNoteSha256']},
            'rp1_gpclk_dkms': {'status': 'loaded', 'version': '0.9.0',
                'buildNoteSha256': self.value['consumerNoteSha256']}}
        self._modules['rp1_gpclk_dkms']['liveOutput'] = False
        self._endpoints = {name: {'status': 'owned', 'open': False}
                           for name in ('/dev/rp1-gpclk', '/dev/rp1-route-admin')}
        self._socket = {'status': 'owned'}
        self._manager = manager_ready()
        self._activation = {'status': 'absent'}
        self.files = None
        if not ready:
            self.make_absent()

    def make_absent(self):
        self._binding = {'status': 'absent'}
        self._artifacts = {}
        self._journals = {name: {'status': 'absent'} for name in self._journals}
        self._modules = {name: {'status': 'absent'} for name in self._modules}
        self._endpoints = {name: {'status': 'absent', 'open': False} for name in self._endpoints}
        self._socket = {'status': 'absent'}
        self._manager = {'status': 'absent'}

    def binding(self): return copy.deepcopy(self._binding)
    def artifacts(self, unused): return copy.deepcopy(self._artifacts)
    def journal(self, name): return copy.deepcopy(self._journals[name])
    def module(self, name): return copy.deepcopy(self._modules[name])
    def endpoint(self, path): return copy.deepcopy(self._endpoints[path])
    def socket(self): return copy.deepcopy(self._socket)
    def services(self): return {'rp1-gpclk-route-manager.socket': {
        'load': 'loaded', 'active': 'active', 'enabled': 'enabled',
        'fragment': '/usr/lib/systemd/system/rp1-gpclk-route-manager.socket'},
        'rp1-gpclk-route-manager@.service': {'load': 'loaded', 'active': 'inactive',
        'enabled': 'static',
        'fragment': '/usr/lib/systemd/system/rp1-gpclk-route-manager@.service'}}
    def manager(self): return copy.deepcopy(self._manager)
    def activation_observation(self): return copy.deepcopy(self._activation)
    def deployment_plan(self, unused):
        return {'version': 1, 'files': {provider.deployment.BINDING: {
            'before': None, 'after': provider.deployment.encode(
                json.dumps(self.value).encode())}}}
    def expected_external(self, expected):
        return {path: {'status': 'exact', 'expectedSha256': sha,
            'actualSha256': sha} for path, sha in expected['externalFiles'].items()}


class Tests(unittest.TestCase):
    def inspect(self, host, **routes):
        return provider.inspect(host, **routes)[0]

    def test_exact_ready_and_absent_are_stable(self):
        exact = self.inspect(Host())
        self.assertEqual(exact['result'], 'exact_ready')
        self.assertTrue(exact['compatible'] and exact['eligible'])
        self.assertFalse(exact['safety']['authorization'])
        self.assertFalse(exact['safety']['liveOutput'])
        self.assertFalse(exact['safety']['owner'])
        self.assertFalse(exact['safety']['lease'])
        self.assertEqual(provider.EXIT['exact_ready'], 0)
        absent = self.inspect(Host(False))
        self.assertEqual(absent['result'], 'absent')
        self.assertEqual(provider.EXIT['absent'], 10)

    def test_activation_required_after_complete_deployment(self):
        host = Host()
        host._modules['rp1_route_controller'] = {'status': 'absent'}
        host._modules['rp1_gpclk_dkms'] = {'status': 'absent'}
        host._endpoints['/dev/rp1-route-admin'] = {'status': 'absent', 'open': False}
        host._endpoints['/dev/rp1-gpclk'] = {'status': 'absent', 'open': False}
        host._socket = {'status': 'absent'}
        host._manager = {'status': 'absent'}
        self.assertEqual(self.inspect(host)['result'], 'activation_required')

    def test_neutral_ready_is_administration_only(self):
        host = Host()
        host._modules['rp1_gpclk_dkms'] = {'status': 'absent'}
        host._endpoints['/dev/rp1-gpclk'] = {'status': 'absent', 'open': False}
        host._manager['query']['state'].update(activeRoute=None,
            controller=controller(0, 0), pendingTransaction=None, application=None)
        host._manager.pop('idle')
        host._journals['activation.json'] = {'status': 'present',
            'value': {'phase': 'complete-neutral'}}
        host._activation = {'status': 'observed', 'value': {'neutral': True}}
        with patch.object(provider.activation, 'neutral_ready', return_value=True):
            result = self.inspect(host)
        self.assertEqual(result['result'], 'neutral_ready')
        self.assertTrue(result['administrationCompatible'])
        self.assertTrue(result['administrationEligible'])
        self.assertFalse(result['compatible'] or result['eligible'])
        self.assertFalse(result['routeSelected'] or result['transmissionEligible'])

    def test_partial_file_publication_requires_recovery(self):
        host = Host()
        host._artifacts[next(iter(host._artifacts))] = {'status': 'absent'}
        self.assertEqual(self.inspect(host)['result'], 'recovery_required')

    def test_changed_foreign_or_mixed_identity_conflicts(self):
        mutations = []
        def changed(host): host._artifacts[next(iter(host._artifacts))]['status'] = 'changed'
        mutations.append(changed)
        mutations.append(lambda host: host._endpoints['/dev/rp1-gpclk'].update(status='unsafe'))
        mutations.append(lambda host: host._modules['rp1_route_controller'].update(version='foreign'))
        mutations.append(lambda host: host._modules['rp1_route_controller'].update(buildNoteSha256='0'*64))
        mutations.append(lambda host: host._binding.update(status='error', detail='malformed'))
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                host = Host(); mutate(host)
                self.assertEqual(self.inspect(host)['result'], 'conflict')

    def test_open_endpoint_and_route_disagreement_conflict(self):
        host = Host(); host._endpoints['/dev/rp1-gpclk']['open'] = True
        self.assertEqual(self.inspect(host)['result'], 'conflict')
        host = Host()
        result = self.inspect(host, requested='gpio4', configured='gpio20', persisted='gpio4')
        self.assertEqual(result['result'], 'conflict')
        self.assertIn('route-selection-mismatch', result['conflicts'])

    def test_pending_fault_and_restoration_failure_require_recovery(self):
        host = Host(); host._journals['deployment-pending.json'] = {'status': 'present', 'value': {}}
        self.assertEqual(self.inspect(host)['result'], 'recovery_required')
        host = Host(); host._manager['query']['state']['controller']['flags'] = 7
        self.assertEqual(self.inspect(host)['result'], 'recovery_required')
        host = Host(); host._manager['query']['state']['application']['phase'] = 'restoration-failed'
        self.assertEqual(self.inspect(host)['result'], 'recovery_required')

    def test_service_failure_requires_completion_and_busy_output_conflicts(self):
        host = Host()
        host.services = lambda: {'rp1-gpclk-route-manager.socket': {
            'load': 'loaded', 'active': 'inactive', 'enabled': 'enabled',
            'fragment': '/usr/lib/systemd/system/rp1-gpclk-route-manager.socket'}}
        self.assertEqual(self.inspect(host)['result'], 'deployment_required')
        host = Host()
        host._manager['idle']['state']['outputLifecycle']['snapshot']['owner'] = 2
        self.assertEqual(self.inspect(host)['result'], 'conflict')

    def test_malformed_runtime_transaction_conflicts(self):
        host = Host()
        host._manager['query']['state']['pendingTransaction']['foreign'] = True
        self.assertEqual(self.inspect(host)['result'], 'conflict')

    def test_missing_application_or_unit_prerequisite_blocks_plan(self):
        host = Host(False)
        host.expected_external = lambda expected: {path: {'status': 'absent'}
            for path in expected['externalFiles']}
        result = provider.inspect(host, bundle=Path('/reviewed'))[0]
        self.assertEqual(result['result'], 'conflict')
        self.assertTrue(any(item.startswith('external-prerequisite-conflict:')
                            for item in result['conflicts']))

    def test_binding_digest_rejects_any_identity_substitution(self):
        value = exact_binding()
        binding.validate(value)
        for field in ('sourceCommit', 'productVersion'):
            altered = copy.deepcopy(value)
            altered[field] = 'f'*40 if field == 'sourceCommit' else '0.9.1'
            with self.assertRaises(ValueError): binding.validate(altered)
        altered = copy.deepcopy(value)
        altered['files'][next(iter(altered['files']))] = '0'*64
        with self.assertRaises(ValueError): binding.validate(altered)
        altered = copy.deepcopy(value)
        altered['uapiSha256']['consumer'] = '0'*64
        altered['artifactSetSha256'] = binding.canonical_digest({key: item for key, item in altered.items() if key != 'artifactSetSha256'})
        with self.assertRaises(ValueError): binding.validate(altered)

    def test_application_companion_read_is_bounded_and_nofollow(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            companion = root/'companion.py'; companion.write_bytes(b'pass\n')
            self.assertEqual(build_binding.companion_bytes(companion), b'pass\n')
            link = root/'link.py'; link.symlink_to(companion)
            with self.assertRaises(OSError): build_binding.companion_bytes(link)
            companion.write_bytes(b'x'*(4*1024*1024+1))
            with self.assertRaisesRegex(ValueError, 'bound'):
                build_binding.companion_bytes(companion)

    def test_runtime_bundle_rebuild_is_byte_deterministic(self):
        import hashlib
        import tempfile
        bundle_builder.generate(bundle_builder.ROOT/'build/runtime-controller')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); modules = root/'modules'; modules.mkdir()
            prefix = b'\x7fELF\x02\x01'
            consumer = (prefix + b'version=0.9.0\0rp1_runtime_controller=1\0' +
                b'rp1_route_controller\0vermagic=' + KERNEL.encode() + b' ')
            controller_data = prefix + b'version=0.9.0\0vermagic=' + KERNEL.encode() + b' '
            for route in ('gpio4', 'gpio20'):
                controller_data += (bundle_builder.ROOT/'build/runtime-controller'/
                                    (route+'.dtbo')).read_bytes()
            (modules/'rp1_gpclk_dkms.ko').write_bytes(consumer)
            (modules/'rp1_route_controller.ko').write_bytes(controller_data)
            value = exact_binding()
            for destination, source in INVENTORY.items():
                data = ((modules/source) if source.endswith('.ko') else
                        (bundle_builder.ROOT/source)).read_bytes()
                value['files'][destination] = hashlib.sha256(data).hexdigest()
            value['uapiSha256'] = {
                'consumer': value['files']['/usr/lib/rp1-gpclk-dkms/runtime-uapi/rp1_gpclk.h'],
                'controller': value['files']['/usr/lib/rp1-gpclk-dkms/runtime-uapi/rp1_route_admin.h']}
            value['artifactSetSha256'] = binding.canonical_digest(
                {key: item for key, item in value.items() if key != 'artifactSetSha256'})
            companion = root/'route_application.py'; companion.write_text('pass\n')
            first = root/'first'; second = root/'second'
            with patch.object(bundle_builder, 'build', return_value=value):
                bundle_builder.bundle(modules, first, companion)
                bundle_builder.bundle(modules, second, companion)
            first_files = {path.name: path.read_bytes() for path in first.iterdir()}
            second_files = {path.name: path.read_bytes() for path in second.iterdir()}
            self.assertEqual(first_files, second_files)
            self.assertEqual(stat.S_IMODE(first.stat().st_mode), 0o700)

    def test_route_plan_binds_preflight_and_is_idempotent_when_ready(self):
        result = self.inspect(Host())
        plan = provider.route_plan(result, 'gpio4')
        self.assertTrue(plan['alreadyReady'])
        result['result'] = 'deployment_required'
        result['routes']['active'] = None
        checked = {'status': 'ok', 'state': {'preflightToken': 'a'*64,
            'controller': controller(0, 0)}}
        with patch.object(provider.client, 'exchange', return_value=checked):
            plan = provider.route_plan(result, 'gpio20')
        digest = provider.canonical_digest(plan)
        altered = copy.deepcopy(plan); altered['route'] = 'gpio4'
        self.assertNotEqual(digest, provider.canonical_digest(altered))

    def test_idle_active_route_can_be_explicitly_planned_to_other_route(self):
        result = self.inspect(Host(), requested='gpio20', configured='gpio20',
                              persisted='gpio20')
        self.assertEqual(result['result'], 'deployment_required')
        checked = {'status': 'ok', 'state': {'preflightToken': 'a'*64,
            'controller': controller(1)}}
        with patch.object(provider.client, 'exchange', return_value=checked):
            plan = provider.route_plan(result, 'gpio20')
        self.assertEqual(plan['configuredRoute'], 'gpio20')
        self.assertEqual(plan['controller']['route'], 1)

    def test_installed_client_preserves_reconcile_output_verb(self):
        replies = []
        def exchange(request):
            replies.append(request)
            return {'schemaVersion': 3, 'contract': provider.client.CONTRACT,
                    'status': 'ok', 'state': {}}
        with patch.object(sys, 'argv', ['runtime_route_client.py',
                'reconcile-output', 'gpio4']), \
             patch.object(provider.client, 'exchange', exchange), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(provider.client.main(), 0)
        self.assertEqual(replies, [{'schemaVersion': 3,
            'operation': 'reconcile-output', 'route': 'gpio4'}])

    def test_schema_and_exit_status_contract(self):
        schema = json.loads((Path(__file__).resolve().parents[1] /
            'schema/rp1-gpclk-runtime-readiness-v1.schema.json').read_text())
        self.assertEqual(schema['properties']['result']['enum'],
            ['absent', 'deployment_required', 'activation_required', 'neutral_ready',
             'exact_ready', 'recovery_required', 'conflict'])
        self.assertEqual(provider.EXIT, {'exact_ready': 0, 'neutral_ready': 0,
            'absent': 10, 'deployment_required': 11, 'recovery_required': 12,
            'conflict': 13, 'activation_required': 14})


if __name__ == '__main__':
    unittest.main()
