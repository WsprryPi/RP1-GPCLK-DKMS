#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Installer-facing runtime-provider readiness and digest-bound ensure facade.

This tool composes the existing deployment and route-manager implementations.
It does not load modules, select a route, or authorize output except through an
explicit digest-bound operation delegated to those implementations.
"""
from __future__ import annotations

import argparse
import grp
import json
import os
from pathlib import Path
import stat
import sys
import uuid

import runtime_binding
import runtime_activation as activation
import runtime_controller_admin as admin
import runtime_deployment as deployment
import runtime_route_client as client

CONTRACT = 'rp1-gpclk-runtime-readiness-v1'
SCHEMA_VERSION = 1
EXIT = {'exact_ready': 0, 'neutral_ready': 0, 'absent': 10,
        'deployment_required': 11, 'recovery_required': 12, 'conflict': 13,
        'activation_required': 14}
ROUTES = ('gpio4', 'gpio20')
ENDPOINTS = {'consumer': '/dev/rp1-gpclk', 'controller': '/dev/rp1-route-admin'}
SOCKET = '/run/rp1-gpclk-dkms/route-manager.sock'


def record_error(error):
    return {'status': 'error', 'detail': str(error)}


def canonical_digest(value):
    return admin.digest(json.dumps(value, sort_keys=True,
        separators=(',', ':')).encode())


class Host:
    """Fixed production observations. Tests replace the complete adapter."""
    def __init__(self):
        self.files = deployment.Files()

    def binding(self):
        try:
            raw = admin.read_regular(admin.BINDING)
            value = runtime_binding.validate(admin.strict_json(raw))
            return {'status': 'valid', 'sha256': admin.digest(raw), 'value': value}
        except FileNotFoundError:
            return {'status': 'absent'}
        except (OSError, ValueError, TypeError, KeyError) as error:
            return record_error(error)

    def artifacts(self, binding):
        result = {}
        expected = {}
        if binding.get('status') == 'valid':
            expected.update(binding['value']['files'])
            expected.update(binding['value']['externalFiles'])
        for path, wanted in sorted(expected.items()):
            try:
                limit = 32*1024*1024 if path.endswith('.ko') else 4*1024*1024
                data = admin.read_regular(path, limit)
                actual = admin.digest(data)
                result[path] = {'status': 'exact' if actual == wanted else 'changed',
                                'expectedSha256': wanted, 'actualSha256': actual}
            except FileNotFoundError:
                result[path] = {'status': 'absent', 'expectedSha256': wanted}
            except (OSError, ValueError) as error:
                result[path] = record_error(error)
        return result

    def journal(self, name):
        path = admin.STATE / name
        try:
            return {'status': 'present', 'value': admin.strict_json(admin.read_regular(path, deployment.MAX_JOURNAL_BYTES))}
        except FileNotFoundError:
            return {'status': 'absent'}
        except (OSError, ValueError, TypeError) as error:
            return record_error(error)

    def module(self, name):
        root = Path('/sys/module') / name
        if not root.exists():
            return {'status': 'absent'}
        result = {'status': 'loaded'}
        for field, path in (('version', root/'version'), ('buildNoteSha256', root/'notes/.note.gnu.build-id')):
            try:
                data = admin.read_regular(path)
                result[field] = data.decode().strip() if field == 'version' else admin.digest(data)
            except (OSError, ValueError, UnicodeError) as error:
                result[field] = record_error(error)
        if name == 'rp1_gpclk_dkms':
            try:
                gate = admin.read_regular(root/'parameters/live_output').decode().strip()
                result['liveOutput'] = gate in ('Y', '1') if gate in ('Y', 'N', '0', '1') else 'unknown'
            except (OSError, ValueError, UnicodeError) as error:
                result['liveOutput'] = record_error(error)
        return result

    def endpoint(self, path):
        try:
            info = os.lstat(path)
            if (not stat.S_ISCHR(info.st_mode) or info.st_uid != 0 or
                    info.st_gid != 0 or stat.S_IMODE(info.st_mode) != 0o600):
                return {'status': 'unsafe', 'ownerUid': info.st_uid,
                        'ownerGid': info.st_gid, 'mode': stat.S_IMODE(info.st_mode)}
            identity = {'/dev/rp1-gpclk': '/sys/class/misc/rp1-gpclk/dev',
                        '/dev/rp1-route-admin': '/sys/class/misc/rp1-route-admin/dev'}[path]
            major, minor = admin.read_regular(identity).decode().strip().split(':')
            if info.st_rdev != os.makedev(int(major), int(minor)):
                return {'status': 'unsafe', 'reason': 'device-identity-mismatch'}
            opened = False
            scanned = 0
            for process in Path('/proc').glob('[0-9]*'):
                try:
                    descriptors = process.joinpath('fd').iterdir()
                except OSError:
                    continue
                for descriptor in descriptors:
                    scanned += 1
                    if scanned > 65536:
                        return {'status': 'owned', 'open': 'unknown', 'reason': 'fd-scan-limit'}
                    try:
                        candidate = descriptor.stat()
                    except OSError:
                        continue
                    if (candidate.st_dev, candidate.st_ino) == (info.st_dev, info.st_ino):
                        opened = True
                        break
                if opened:
                    break
            return {'status': 'owned', 'open': opened, 'ownerUid': info.st_uid,
                    'ownerGid': info.st_gid, 'mode': stat.S_IMODE(info.st_mode)}
        except FileNotFoundError:
            return {'status': 'absent', 'open': False}
        except (OSError, ValueError, UnicodeError) as error:
            return record_error(error)

    def socket(self):
        try:
            info = os.lstat(SOCKET)
            group = grp.getgrnam('rp1-gpclk-route').gr_gid
            return {'status': 'owned' if stat.S_ISSOCK(info.st_mode) and
                    info.st_uid == 0 and info.st_gid == group and
                    stat.S_IMODE(info.st_mode) == 0o660 else 'unsafe',
                    'ownerUid': info.st_uid, 'ownerGid': info.st_gid,
                    'mode': stat.S_IMODE(info.st_mode)}
        except FileNotFoundError:
            return {'status': 'absent'}
        except (OSError, KeyError) as error:
            return record_error(error)

    def services(self):
        result = {}
        for name in ('rp1-gpclk-route-manager.socket',
                     'rp1-gpclk-route-manager@.service', 'wsprrypi.service'):
            try:
                text = admin.run(('/usr/bin/systemctl', 'show', name,
                    '--property=LoadState,ActiveState,UnitFileState,FragmentPath', '--value'))
                lines = text.splitlines()
                if len(lines) != 4:
                    raise ValueError('service observation schema')
                result[name] = dict(zip(('load', 'active', 'enabled', 'fragment'), lines))
            except (OSError, ValueError) as error:
                result[name] = record_error(error)
        return result

    def manager(self):
        try:
            query = client.exchange({'schemaVersion': 3, 'operation': 'query'})
            if (query.get('operation') != 'query' or query.get('status') != 'ok' or
                    not isinstance(query.get('state'), dict)):
                raise ValueError('runtime query response schema')
            result = {'status': 'observed', 'query': query}
            route = query.get('state', {}).get('activeRoute')
            if route in ROUTES:
                result['idle'] = client.exchange({'schemaVersion': 3,
                    'operation': 'idle', 'route': route})
            return result
        except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
            return record_error(error)

    def deployment_plan(self, bundle):
        values = deployment.payloads(bundle)
        value = deployment.plan(self.files, values)
        return value

    def expected_external(self, expected):
        observed = self.artifacts({'status': 'valid', 'value': expected})
        return {path: observed[path] for path in expected['externalFiles']}

    def activation_observation(self):
        try:
            return {'status': 'observed', 'value': activation.observe(activation.Linux())}
        except FileNotFoundError:
            return ({'status': 'absent'} if self.binding().get('status') == 'absent'
                    else record_error('activation provenance or prerequisite is absent'))
        except (OSError, ValueError, TypeError, KeyError) as error:
            return record_error(error)

    def activation_plan(self):
        return activation.activation_plan(activation.Linux())

    def activation_ensure(self, value, approved):
        return activation.ensure(activation.Linux(), value, approved)

    def activation_recovery_plan(self):
        return activation.recovery_plan(activation.Linux())

    def activation_recover(self, value, approved):
        return activation.ensure_recovery(activation.Linux(), value, approved)


def inspect(host, bundle=None, requested=None, configured=None, persisted=None):
    binding = host.binding()
    expected = None
    plan = None
    if bundle is not None:
        try:
            plan = host.deployment_plan(Path(bundle))
            expected = runtime_binding.validate(admin.strict_json(
                deployment.decode(plan['files'][deployment.BINDING]['after'])))
        except (OSError, ValueError, TypeError, KeyError) as error:
            expected = record_error(error)
    artifacts = host.artifacts(binding)
    expected_external = (host.expected_external(expected)
                         if isinstance(expected, dict) and 'externalFiles' in expected else {})
    journals = {name: host.journal(name) for name in
        ('deployment-pending.json', 'transaction.json', 'manager.json',
         'application.json', 'activation.json')}
    modules = {name: host.module(name) for name in ('rp1_route_controller', 'rp1_gpclk_dkms')}
    endpoints = {name: host.endpoint(path) for name, path in ENDPOINTS.items()}
    socket = host.socket()
    services = host.services()
    manager = host.manager() if socket.get('status') == 'owned' else {'status': 'absent'}
    activation_observation = (host.activation_observation()
        if hasattr(host, 'activation_observation') else {'status': 'absent'})
    result = {'schemaVersion': SCHEMA_VERSION, 'contract': CONTRACT,
        'profile': 'runtime', 'result': None, 'state': None,
        'compatible': False, 'eligible': False,
        'administrationCompatible': False, 'administrationEligible': False,
        'routeSelected': False, 'transmissionEligible': False,
        'identities': {'installedBinding': binding, 'expectedBinding': expected,
            'expectedExternal': expected_external},
        'artifacts': artifacts, 'deployment': {'journal': journals['deployment-pending.json'],
            'planSha256': canonical_digest(plan) if plan is not None else None},
        'routes': {'requested': requested, 'configured': configured,
            'persisted': persisted, 'active': None},
        'endpoints': endpoints, 'managerSocket': socket, 'services': services,
        'modules': modules, 'journals': journals, 'manager': manager,
        'activation': activation_observation,
        'reboot': {'occurred': 'unknown', 'required': False},
        'safety': {'liveOutput': 'unknown', 'owner': 'unknown', 'lease': 'unknown',
            'authorization': False, 'clock': 'unknown', 'gpio': 'unknown',
            'dma': 'unknown', 'endpointOpen': endpoints['consumer'].get('open', 'unknown')},
        'conflicts': [], 'remediation': []}
    classify(result)
    return result, plan


def classify(result):
    conflicts = result['conflicts']
    binding = result['identities']['installedBinding']
    expected = result['identities']['expectedBinding']
    journals = result['journals']
    artifacts = result['artifacts']
    modules = result['modules']
    manager = result['manager']
    activation_observation = result['activation']

    if binding.get('status') == 'error':
        conflicts.append('installed-binding-invalid')
    if isinstance(expected, dict) and expected.get('status') == 'error':
        conflicts.append('bundle-invalid')
    for path, value in result['identities']['expectedExternal'].items():
        if value.get('status') != 'exact':
            conflicts.append('external-prerequisite-conflict:'+path)
    if binding.get('status') == 'valid' and isinstance(expected, dict) and 'artifactSetSha256' in expected:
        if binding['value']['artifactSetSha256'] != expected['artifactSetSha256']:
            conflicts.append('installed-binding-differs-from-requested-bundle')
    for path, value in artifacts.items():
        if value.get('status') in ('changed', 'error'):
            conflicts.append('artifact-conflict:'+path)
    for name, value in result['endpoints'].items():
        if value.get('status') in ('unsafe', 'error'):
            conflicts.append(name+'-endpoint-unsafe')
    for name, value in result['endpoints'].items():
        if value.get('open') is not False and value.get('status') != 'absent':
            conflicts.append(name+'-endpoint-open-or-unknown')
    if result['managerSocket'].get('status') in ('unsafe', 'error'):
        conflicts.append('manager-socket-unsafe')
    if any(value.get('status') == 'error' for value in journals.values()):
        conflicts.append('deployment-or-runtime-journal-invalid')
    if activation_observation.get('status') == 'error':
        conflicts.append('activation-evidence-invalid')
    for name, value in modules.items():
        if value.get('status') == 'loaded' and value.get('version') != runtime_binding.PRODUCT_VERSION:
            conflicts.append('mixed-module-version:'+name)
        if value.get('status') == 'loaded' and binding.get('status') == 'valid':
            field = 'controllerNoteSha256' if name == 'rp1_route_controller' else 'consumerNoteSha256'
            if value.get('buildNoteSha256') != binding['value'][field]:
                conflicts.append('loaded-module-identity-mismatch:'+name)
    if modules['rp1_gpclk_dkms'].get('liveOutput') not in (False, None):
        conflicts.append('live-output-not-disabled')

    pending = journals['deployment-pending.json'].get('status') == 'present'
    activation_journal = journals['activation.json']
    query = manager.get('query', {}) if manager.get('status') == 'observed' else {}
    state = query.get('state', {}) if isinstance(query, dict) else {}
    controller = state.get('controller', {}) if isinstance(state, dict) else {}
    active = state.get('activeRoute') if isinstance(state, dict) else None
    result['routes']['active'] = active
    application = state.get('application') if isinstance(state, dict) else None
    phase = application.get('phase') if isinstance(application, dict) else None
    route_journal = state.get('pendingTransaction') if isinstance(state, dict) else None
    fault = bool(controller.get('flags', 0) & admin.FAULT) if isinstance(controller, dict) else False
    route_values = [value for value in result['routes'].values() if value is not None]
    consumer_routes = [result['routes'][name] for name in
        ('requested', 'configured', 'persisted') if result['routes'][name] is not None]
    if len(set(consumer_routes)) > 1:
        conflicts.append('route-selection-mismatch')
    if active is not None and active not in ROUTES:
        conflicts.append('ambiguous-active-route')
    transaction_valid = (isinstance(route_journal, dict) and
        set(route_journal) == {'version', 'boot', 'session', 'binding', 'request',
                               'target', 'phase', 'observation'} and
        route_journal.get('version') == 1 and
        route_journal.get('phase') in ('complete-inhibited', 'recovered-inhibited') and
        route_journal.get('observation') == controller and
        route_journal.get('session') == controller.get('session') and
        route_journal.get('binding') == state.get('bindingSha256') and
        route_journal.get('boot') == state.get('bootId'))
    if active in ROUTES and not transaction_valid:
        conflicts.append('runtime-transaction-identity-invalid')
    partial = (binding.get('status') == 'valid' and
               any(value.get('status') == 'absent' for value in artifacts.values()))
    activation_pending = (activation_journal.get('status') == 'present' and
        activation_journal.get('value', {}).get('phase') not in activation.TERMINAL)
    unresolved = (pending or activation_pending or partial or fault or query.get('status') == 'error' or
        (binding.get('status') == 'valid' and manager.get('status') == 'error' and
         modules['rp1_route_controller'].get('status') == 'loaded') or
        (isinstance(route_journal, dict) and route_journal.get('phase') not in
         ('complete-inhibited', 'recovered-inhibited')) or
        phase in ('restoration-failed', 'route-failed') or
        (active in ROUTES and phase is not None and phase not in
         ('restored', 'stopped', 'administrator-masked')))

    idle = manager.get('idle', {}) if manager.get('status') == 'observed' else {}
    output = idle.get('state', {}).get('outputLifecycle', {}) if isinstance(idle, dict) else {}
    snapshot = output.get('snapshot', {}) if isinstance(output, dict) else {}
    if snapshot:
        result['safety'].update({'liveOutput': snapshot.get('live') != 1,
            'owner': snapshot.get('owner') != 1, 'lease': snapshot.get('lease') != 1,
            'clock': 'quiescent' if snapshot.get('clock') == 2 else 'unknown',
            'gpio': 'quiescent' if snapshot.get('gpio') == 2 else 'unknown',
            'dma': 'quiescent' if snapshot.get('dma') == 2 else 'unknown'})
        if (any(snapshot.get(key) != 1 for key in ('fault', 'owner', 'lease', 'live')) or
                any(snapshot.get(key) != 2 for key in ('eligible', 'gpio', 'clock', 'dma', 'stable'))):
            conflicts.append('consumer-not-closed-disabled-and-quiescent')
    aligned = bool(active in ROUTES and all(value == active for value in route_values))
    endpoints_ready = all(value.get('status') == 'owned' for value in result['endpoints'].values())
    closed = result['endpoints']['consumer'].get('open') is False
    socket_ready = result['managerSocket'].get('status') == 'owned'
    services_ready = (result['services'].get('rp1-gpclk-route-manager.socket', {}).get('load') == 'loaded' and
        result['services'].get('rp1-gpclk-route-manager.socket', {}).get('active') == 'active' and
        result['services'].get('rp1-gpclk-route-manager.socket', {}).get('fragment') ==
        '/usr/lib/systemd/system/rp1-gpclk-route-manager.socket')
    artifacts_ready = (binding.get('status') == 'valid' and artifacts and
                       all(value.get('status') == 'exact' for value in artifacts.values()))
    modules_ready = all(value.get('status') == 'loaded' for value in modules.values())
    application_ready = phase in ('restored', 'stopped', 'administrator-masked')
    output_ready = (output.get('ready') is True and output.get('executionAuthorized') is False and
        snapshot and snapshot.get('route') in (1, 2) and
        all(snapshot.get(key) == 1 for key in ('fault', 'owner', 'lease', 'live')) and
        all(snapshot.get(key) == 2 for key in ('eligible', 'gpio', 'clock', 'dma', 'stable')))
    controller_ready = (controller.get('flags') == admin.CONSUMER | admin.PINNED and
                        controller.get('error') == 0 and controller.get('route') in (1, 2))
    neutral = (activation_observation.get('status') == 'observed' and
        activation.neutral_ready(activation_observation['value']))
    if neutral:
        result['safety'].update({'liveOutput': False, 'owner': False,
            'lease': False, 'authorization': False, 'clock': 'quiescent',
            'gpio': 'quiescent', 'dma': 'quiescent', 'endpointOpen': False})
        result['reboot']['occurred'] = False
    if (modules['rp1_route_controller'].get('status') == 'loaded' and
            modules['rp1_gpclk_dkms'].get('status') == 'absent' and not neutral and
            not activation_pending):
        conflicts.append('loaded-controller-without-completed-activation')

    residue = (binding.get('status') != 'absent' or artifacts or
        any(value.get('status') == 'loaded' for value in modules.values()) or
        any(value.get('status') != 'absent' for value in result['endpoints'].values()) or
        result['managerSocket'].get('status') != 'absent' or
        any(value.get('status') != 'absent' for value in journals.values()))
    if conflicts:
        classification = 'conflict'
        result['remediation'].append('Preserve the conflicting state and use its owning migration or removal workflow.')
    elif unresolved:
        classification = 'recovery_required'
        result['remediation'].append('Use the existing deployment recover, route recover, or application restore verb indicated by the retained journal.')
    elif (artifacts_ready and modules_ready and endpoints_ready and closed and socket_ready and services_ready and
          controller_ready and application_ready and aligned and output_ready):
        classification = 'exact_ready'
    elif neutral:
        classification = 'neutral_ready'
    elif not residue:
        classification = 'absent'
        result['remediation'].append('Build and review an exact runtime bundle, then approve its deployment plan digest.')
    elif artifacts_ready and modules['rp1_route_controller'].get('status') == 'absent' and modules['rp1_gpclk_dkms'].get('status') == 'absent':
        classification = 'activation_required'
        result['remediation'].append('Review and execute neutral activation before any explicit route selection.')
    else:
        classification = 'deployment_required'
        result['remediation'].append('Complete the explicit deployment step; installation alone does not activate administration or select a route.')
    result['result'] = classification
    result['state'] = classification
    result['compatible'] = classification == 'exact_ready'
    result['eligible'] = classification == 'exact_ready'
    result['administrationCompatible'] = classification in ('neutral_ready', 'exact_ready')
    result['administrationEligible'] = classification in ('neutral_ready', 'exact_ready')
    result['routeSelected'] = classification == 'exact_ready'
    result['transmissionEligible'] = classification == 'exact_ready'


def route_plan(result, route):
    if result['result'] in ('conflict', 'recovery_required', 'absent',
                            'activation_required'):
        raise ValueError('runtime state is not eligible for route planning')
    manager = result['manager']
    binding = result['identities']['installedBinding']
    if (binding.get('status') != 'valid' or not result['artifacts'] or
            any(value.get('status') != 'exact' for value in result['artifacts'].values())):
        raise ValueError('exact deployed runtime artifacts are required')
    if manager.get('status') != 'observed':
        raise ValueError('runtime manager is unavailable')
    if result['routes']['active'] == route and result['result'] == 'exact_ready':
        return {'version': 1, 'operation': 'select', 'route': route,
                'alreadyReady': True, 'bindingSha256': binding['sha256'],
                'requestedRoute': result['routes']['requested'],
                'configuredRoute': result['routes']['configured'],
                'persistedRoute': result['routes']['persisted']}
    checked = client.exchange({'schemaVersion': 3, 'operation': 'preflight', 'route': route})
    if checked.get('status') != 'ok':
        raise ValueError('route preflight failed')
    return {'version': 1, 'operation': 'select', 'route': route, 'alreadyReady': False,
        'bindingSha256': binding['sha256'],
        'requestedRoute': result['routes']['requested'],
        'configuredRoute': result['routes']['configured'],
        'persistedRoute': result['routes']['persisted'],
        'preflightToken': checked['state']['preflightToken'],
        'controller': checked['state']['controller']}


def emit(value):
    print(json.dumps(value, sort_keys=True, indent=2))


def main(host=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('inspect', 'plan', 'ensure',
        'activation-plan', 'activation-ensure', 'activation-recover-plan',
        'activation-recover', 'route-plan', 'route-ensure'))
    parser.add_argument('--bundle', type=Path)
    parser.add_argument('--plan-sha256')
    parser.add_argument('--route', choices=ROUTES)
    parser.add_argument('--requested-route', choices=ROUTES)
    parser.add_argument('--configured-route', choices=ROUTES)
    parser.add_argument('--persisted-route', choices=ROUTES)
    args = parser.parse_args()
    host = host or Host()
    if args.operation in ('plan', 'ensure') and args.bundle is None:
        raise ValueError('--bundle is required')
    if args.operation in ('route-plan', 'route-ensure') and args.route is None:
        raise ValueError('--route is required')
    if args.operation.startswith('activation-') and any(
            value is not None for value in
            (args.route, args.requested_route, args.configured_route,
             args.persisted_route)):
        raise ValueError('neutral activation accepts no GPIO route')
    result, plan = inspect(host, args.bundle, args.requested_route,
        args.configured_route, args.persisted_route)
    if args.operation == 'inspect':
        emit(result)
        return EXIT[result['result']]
    if args.operation == 'plan':
        result['deployment']['plan'] = {'planSha256': canonical_digest(plan),
            'destinations': {path: {side: None if data is None else admin.digest(deployment.decode(data))
            for side, data in record.items()} for path, record in plan['files'].items()}}
        emit(result)
        return EXIT[result['result']]
    if args.operation == 'ensure':
        if result['result'] in ('conflict', 'recovery_required'):
            emit(result)
            return EXIT[result['result']]
        with deployment.mutation_lock():
            # Recreate the complete plan while holding the shared deployment/
            # route lock. Only the originally reviewed digest is accepted.
            plan = host.deployment_plan(args.bundle)
            digest = canonical_digest(plan)
            if args.plan_sha256 != digest:
                raise ValueError('reviewed deployment plan digest required')
            attributable = [record for path, record in plan['files'].items()
                if path not in deployment.JOURNALS]
            if all(deployment.decode(record['before']) == deployment.decode(record['after'])
                   for record in attributable):
                result['deployment']['execution'] = 'idempotent-no-change'
            else:
                deployment.apply(host.files, plan, digest)
                result['deployment']['execution'] = 'deployed-inhibited'
        emit(result)
        return 0
    if args.operation in ('activation-plan', 'activation-ensure'):
        if result['result'] not in ('activation_required', 'neutral_ready'):
            emit(result)
            return EXIT[result['result']]
        selected = host.activation_plan()
        digest = activation.plan_digest(selected)
        if args.operation == 'activation-plan':
            result['activationPlan'] = {'planSha256': digest, **selected}
            emit(result)
            return EXIT[result['result']]
        if args.plan_sha256 != digest:
            raise ValueError('reviewed neutral activation plan digest required')
        reply = host.activation_ensure(selected, digest)
        emit({'schemaVersion': SCHEMA_VERSION, 'contract': CONTRACT,
              'operation': 'activation-ensure', 'planSha256': digest,
              'response': reply})
        return 0
    if args.operation in ('activation-recover-plan', 'activation-recover'):
        selected = host.activation_recovery_plan()
        digest = activation.plan_digest(selected)
        if args.operation == 'activation-recover-plan':
            emit({'schemaVersion': SCHEMA_VERSION, 'contract': CONTRACT,
                  'operation': args.operation, 'planSha256': digest,
                  'plan': selected})
            return 0
        if args.plan_sha256 != digest:
            raise ValueError('reviewed neutral recovery plan digest required')
        reply = host.activation_recover(selected, digest)
        emit({'schemaVersion': SCHEMA_VERSION, 'contract': CONTRACT,
              'operation': args.operation, 'planSha256': digest,
              'response': reply})
        return 0
    selected = route_plan(result, args.route)
    route_digest = canonical_digest(selected)
    if args.operation == 'route-plan':
        result['routePlan'] = {'planSha256': route_digest, **selected}
        emit(result)
        return EXIT[result['result']]
    if args.plan_sha256 != route_digest:
        raise ValueError('reviewed route plan digest required')
    if selected['alreadyReady']:
        reply = {'status': 'idempotent-ready'}
    else:
        reply = client.exchange({'schemaVersion': 3, 'operation': 'switch',
            'route': args.route, 'execute': True, 'requestId': str(uuid.uuid4()),
            'actor': 'runtime-provider-installer',
            'preflightToken': selected['preflightToken']})
    emit({'schemaVersion': SCHEMA_VERSION, 'contract': CONTRACT,
          'operation': 'route-ensure', 'planSha256': route_digest, 'response': reply})
    return 0 if reply.get('status') != 'error' else 12


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
        print('STOP: '+str(error), file=sys.stderr)
        emit({'schemaVersion': SCHEMA_VERSION, 'contract': CONTRACT,
              'result': 'conflict', 'state': 'conflict', 'compatible': False,
              'eligible': False, 'error': {'code': 'fail-closed', 'detail': str(error)}})
        raise SystemExit(EXIT['conflict'])
