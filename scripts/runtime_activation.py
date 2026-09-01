#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Digest-bound neutral runtime-controller activation and explicit recovery."""
from __future__ import annotations

import fcntl
import grp
import json
import os
from pathlib import Path
import re
import stat
import tempfile
import uuid

import runtime_application as application
import runtime_binding
import runtime_controller_admin as admin
import runtime_deployment as deployment
import runtime_route_client as client

JOURNAL = admin.STATE / 'activation.json'
LAST_DEPLOYMENT = admin.STATE / 'last-deployment.json'
CONTROLLER = f'/lib/modules/{admin.KERNEL}/updates/dkms/rp1_route_controller.ko'
SOCKET_UNIT = 'rp1-gpclk-route-manager.socket'
SERVICE_UNIT = 'rp1-gpclk-route-manager@.service'
APPLICATION_UNIT = 'wsprrypi.service'
SOCKET_PATH = Path('/run/rp1-gpclk-dkms/route-manager.sock')
MAX_RECORD = 4 * 1024 * 1024
PENDING = ('activation-intent', 'controller-load-intent', 'socket-start-intent',
           'manager-query-intent', 'application-restore-intent', 'rollback-intent',
           'activation-failed', 'rollback-failed')
TERMINAL = ('complete-neutral', 'recovered-inhibited')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def plan_digest(value):
    return admin.digest(canonical(value))


def validate_plan(value):
    required = {'version', 'operation', 'bindingSha256', 'artifactSetSha256',
                'bootId', 'lastDeploymentSha256', 'application',
                'socketWasActive', 'alreadyReady', 'previousActivationSha256'}
    if (not isinstance(value, dict) or set(value) != required or
            type(value.get('version')) is not int or value['version'] != 1 or
            value.get('operation') != 'neutral-activation' or
            any(not isinstance(value.get(name), str) or
                not re.fullmatch('[0-9a-f]{64}', value[name])
                for name in ('bindingSha256', 'artifactSetSha256',
                             'lastDeploymentSha256')) or
            not isinstance(value.get('bootId'), str) or
            type(value.get('socketWasActive')) is not bool or
            type(value.get('alreadyReady')) is not bool or
            (value.get('previousActivationSha256') is not None and
             (not isinstance(value['previousActivationSha256'], str) or
              not re.fullmatch('[0-9a-f]{64}', value['previousActivationSha256'])))):
        raise ValueError('neutral activation plan schema')
    uuid.UUID(value['bootId'])
    application.validate_neutral_capture(value['application'])
    return value


def validate_journal(value):
    required = {'version', 'plan', 'planSha256', 'requestId', 'phase',
                'controller', 'manager', 'application', 'error'}
    if (not isinstance(value, dict) or set(value) != required or
            type(value.get('version')) is not int or value['version'] != 1 or
            value.get('phase') not in (*PENDING, *TERMINAL) or
            not isinstance(value.get('requestId'), str) or
            not isinstance(value.get('planSha256'), str) or
            not re.fullmatch('[0-9a-f]{64}', value['planSha256'])):
        raise ValueError('neutral activation journal schema')
    uuid.UUID(value['requestId'])
    validate_plan(value['plan'])
    if plan_digest(value['plan']) != value['planSha256']:
        raise ValueError('neutral activation journal plan mismatch')
    if value['controller'] is not None:
        admin.validate_observation(value['controller'])
    if value['manager'] is not None and not isinstance(value['manager'], dict):
        raise ValueError('neutral activation manager evidence')
    if value['application'] is not None and not isinstance(value['application'], dict):
        raise ValueError('neutral activation application evidence')
    if value['error'] is not None and not isinstance(value['error'], str):
        raise ValueError('neutral activation error evidence')
    return value


class Linux:
    """Fixed production effects; tests inject a complete fake."""
    def read_record(self, path):
        try:
            self.trusted_file(Path(path), 0o600)
            return admin.strict_json(admin.read_regular(path, MAX_RECORD))
        except FileNotFoundError:
            return None

    def write_journal(self, value):
        validate_journal(value)
        shell = admin.Linux.__new__(admin.Linux)
        shell.write_record('activation.json', value)

    def archive_journal(self, value):
        validate_journal(value)
        identity = admin.digest(canonical(value))
        path = admin.STATE / ('prior-activation-' + identity + '.json')
        data = canonical(value) + b'\n'
        try:
            self.trusted_file(path, 0o600)
            if admin.read_regular(path, MAX_RECORD) != data:
                raise ValueError('prior activation archive identity conflict')
            return
        except FileNotFoundError:
            pass
        fd, temporary = tempfile.mkstemp(prefix='activation-archive-', dir=admin.STATE)
        try:
            with os.fdopen(fd, 'wb') as stream:
                os.fchmod(stream.fileno(), 0o600)
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            try:
                os.link(temporary, path, follow_symlinks=False)
            except FileExistsError:
                self.trusted_file(path, 0o600)
                if admin.read_regular(path, MAX_RECORD) != data:
                    raise ValueError('prior activation archive appeared with different bytes')
            admin.fsync_dir(admin.STATE)
        finally:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass

    def boot(self):
        value = admin.read_regular('/proc/sys/kernel/random/boot_id').decode().strip()
        uuid.UUID(value)
        return value

    def binding(self):
        self.trusted_file(admin.BINDING, 0o644)
        raw = admin.read_regular(admin.BINDING)
        value = runtime_binding.validate(admin.strict_json(raw))
        for path, expected in {**value['files'], **value['externalFiles']}.items():
            mode = 0o755 if path == runtime_binding.APPLICATION else 0o644
            self.trusted_file(Path(path), mode)
            limit = 32 * 1024 * 1024 if path.endswith('.ko') else 4 * 1024 * 1024
            if admin.digest(admin.read_regular(path, limit)) != expected:
                raise ValueError('activation artifact mismatch: ' + path)
        return raw, value

    def trusted_file(self, path, mode):
        info = Path(path).lstat()
        if (not stat.S_ISREG(info.st_mode) or info.st_uid or info.st_gid or
                stat.S_IMODE(info.st_mode) != mode or info.st_nlink != 1):
            raise ValueError('activation file ownership/mode/link mismatch: ' + str(path))

    def last_deployment(self, binding_raw):
        self.trusted_file(LAST_DEPLOYMENT, 0o600)
        raw = admin.read_regular(LAST_DEPLOYMENT, deployment.MAX_JOURNAL_BYTES)
        value = admin.strict_json(raw)
        deployment.journal_bytes(value)
        installed = deployment.decode(value['files'][deployment.BINDING]['after'])
        if installed != binding_raw:
            raise ValueError('last deployment binding differs')
        return raw, value

    def module(self, name, note):
        root = Path('/sys/module') / name
        if not root.exists():
            return {'status': 'absent'}
        actual = admin.digest(admin.read_regular(root / 'notes/.note.gnu.build-id'))
        return {'status': 'loaded', 'buildNoteSha256': actual,
                'exact': actual == note}

    def endpoint(self, path, identity):
        try:
            info = os.lstat(path)
        except FileNotFoundError:
            return {'status': 'absent', 'open': False}
        if (not stat.S_ISCHR(info.st_mode) or info.st_uid or info.st_gid or
                stat.S_IMODE(info.st_mode) != 0o600):
            return {'status': 'unsafe'}
        major, minor = admin.read_regular(identity).decode().strip().split(':')
        if info.st_rdev != os.makedev(int(major), int(minor)):
            return {'status': 'unsafe'}
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
                    return {'status': 'owned', 'open': 'unknown'}
                try:
                    candidate = descriptor.stat()
                except OSError:
                    continue
                if (candidate.st_dev, candidate.st_ino) == (info.st_dev, info.st_ino):
                    opened = True
                    break
            if opened:
                break
        return {'status': 'owned', 'open': opened}

    def service(self, name):
        if name not in {SOCKET_UNIT, SERVICE_UNIT, APPLICATION_UNIT}:
            raise ValueError('unsupported activation service: ' + name)
        return admin.systemd_unit(
            name, include_main_pid=(name == APPLICATION_UNIT))

    def manager_socket(self):
        try:
            info = os.lstat(SOCKET_PATH)
        except FileNotFoundError:
            return {'status': 'absent'}
        group = grp.getgrnam('rp1-gpclk-route').gr_gid
        if (not stat.S_ISSOCK(info.st_mode) or info.st_uid or info.st_gid != group or
                stat.S_IMODE(info.st_mode) != 0o660):
            return {'status': 'unsafe', 'ownerUid': info.st_uid,
                    'ownerGid': info.st_gid, 'mode': stat.S_IMODE(info.st_mode)}
        return {'status': 'owned', 'ownerUid': info.st_uid,
                'ownerGid': info.st_gid, 'mode': stat.S_IMODE(info.st_mode)}

    def inhibitor(self):
        try:
            return admin.read_regular(application.unit_file(application.DROPIN)) == application.INHIBIT
        except FileNotFoundError:
            return False

    def controller_state(self):
        fd = os.open(admin.ENDPOINT, os.O_RDWR | os.O_NOFOLLOW)
        try:
            info = os.fstat(fd)
            if not stat.S_ISCHR(info.st_mode) or info.st_uid or info.st_gid or info.st_mode & 0o077:
                raise ValueError('controller endpoint ownership')
            data = bytearray(admin.FORMAT.pack(1, admin.STATUS, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
            fcntl.ioctl(fd, admin.IOCTL, data, True)
            abi, op, route, reserved, session, generation, oid, error, active, flags, r1, r2 = admin.FORMAT.unpack(data)
            if abi != 1 or op or route or reserved or r1 or r2:
                raise ValueError('controller response schema')
            value = {'session': session, 'generation': generation, 'id': oid,
                     'error': error, 'route': active, 'flags': flags}
            admin.validate_observation(value)
            return value
        finally:
            os.close(fd)

    def load_controller(self):
        admin.run(('/usr/sbin/insmod', CONTROLLER))

    def unload_controller(self):
        admin.run(('/usr/sbin/rmmod', 'rp1_route_controller'))

    def start_socket(self):
        admin.run(('/usr/bin/systemctl', 'start', SOCKET_UNIT))

    def stop_socket(self):
        admin.run(('/usr/bin/systemctl', 'stop', SOCKET_UNIT))

    def manager_query(self):
        return client.exchange({'schemaVersion': 3, 'operation': 'query'})

    def restore_application(self, record):
        return application.neutral_restore(record)

    def inhibit_application(self):
        application.neutral_inhibit()


def observe(system):
    raw, binding = system.binding()
    deployment_raw, deployed = system.last_deployment(raw)
    activation = system.read_record(JOURNAL)
    if activation is not None:
        validate_journal(activation)
    controller = system.module('rp1_route_controller', binding['controllerNoteSha256'])
    consumer = system.module('rp1_gpclk_dkms', binding['consumerNoteSha256'])
    controller_endpoint = system.endpoint('/dev/rp1-route-admin',
        '/sys/class/misc/rp1-route-admin/dev')
    consumer_endpoint = system.endpoint('/dev/rp1-gpclk',
        '/sys/class/misc/rp1-gpclk/dev')
    socket_service = system.service(SOCKET_UNIT)
    manager_service = system.service(SERVICE_UNIT)
    application_service = system.service(APPLICATION_UNIT)
    manager_socket = system.manager_socket()
    controller_state = system.controller_state() if controller['status'] == 'loaded' else None
    transactions = {}
    for name in ('deployment-pending.json', 'transaction.json', 'manager.json',
                 'application.json'):
        value = system.read_record(admin.STATE / name)
        transactions[name] = value
    return {'bindingSha256': admin.digest(raw),
        'artifactSetSha256': binding['artifactSetSha256'], 'bootId': system.boot(),
        'lastDeploymentSha256': admin.digest(deployment_raw),
        'application': deployed['application'], 'activationJournal': activation,
        'controller': controller, 'consumer': consumer,
        'controllerEndpoint': controller_endpoint, 'consumerEndpoint': consumer_endpoint,
        'controllerState': controller_state, 'socket': socket_service,
        'managerSocket': manager_socket, 'managerService': manager_service,
        'applicationService': application_service,
        'transactions': transactions, 'inhibited': system.inhibitor()}


def application_matches(capture, observed):
    masked = observed.get('load') == 'masked' or observed.get('enabled') in (
        'masked', 'masked-runtime')
    if masked != capture['administratorMasked']:
        return False
    return (observed.get('active') == 'active' if capture['wasActive'] else
            observed.get('active') in ('inactive', 'failed'))


def restored_application_matches(journal, observed):
    if not application_matches(journal['plan']['application'], observed):
        return False
    outcome = journal.get('application')
    service = outcome.get('service') if isinstance(outcome, dict) else None
    if not isinstance(service, dict):
        return False
    if journal['plan']['application']['wasActive']:
        return observed.get('MainPID') == service.get('MainPID') != '0'
    return observed.get('MainPID') == '0'


def neutral_ready(observation):
    journal = observation['activationJournal']
    return bool(journal and journal['phase'] == 'complete-neutral' and
        journal['plan']['bindingSha256'] == observation['bindingSha256'] and
        journal['plan']['artifactSetSha256'] == observation['artifactSetSha256'] and
        journal['plan']['bootId'] == observation['bootId'] and
        observation['controller'] == {'status': 'loaded',
            'buildNoteSha256': observation['controller']['buildNoteSha256'], 'exact': True} and
        observation['consumer']['status'] == 'absent' and
        observation['controllerEndpoint'].get('status') == 'owned' and
        observation['controllerEndpoint'].get('open') is False and
        observation['consumerEndpoint'].get('status') == 'absent' and
        observation['controllerState'] and
        journal.get('controller') == observation['controllerState'] and
        not any(observation['controllerState'][name] for name in
                ('generation', 'id', 'error', 'route', 'flags')) and
        observation['socket'].get('active') == 'active' and
        observation['managerSocket'].get('status') == 'owned' and
        observation['socket'].get('fragment') ==
            '/usr/lib/systemd/system/rp1-gpclk-route-manager.socket' and
        observation['managerService'].get('load') == 'loaded' and
        observation['managerService'].get('fragment') ==
            '/usr/lib/systemd/system/rp1-gpclk-route-manager@.service' and
        not observation['inhibited'] and
        restored_application_matches(journal, observation['applicationService']) and
        isinstance(journal.get('application'), dict) and
        journal['application'].get('phase') in application.TERMINAL)


def activation_plan(system):
    observed = observe(system)
    already = neutral_ready(observed)
    journal = observed['activationJournal']
    if journal is not None and not already and journal['phase'] != 'recovered-inhibited':
        raise ValueError('neutral activation journal requires explicit recovery')
    if any(value is not None for value in observed['transactions'].values()):
        raise ValueError('deployment, route, manager, or application transaction is pending')
    if observed['consumer']['status'] != 'absent' or observed['consumerEndpoint']['status'] != 'absent':
        raise ValueError('transmission consumer must remain absent')
    if observed['controller']['status'] == 'loaded' and not already:
        raise ValueError('loaded controller has no completed activation ownership')
    if observed['controller']['status'] not in ('absent', 'loaded') or not observed['controller'].get('exact', True):
        raise ValueError('controller identity conflict')
    if observed['controllerEndpoint'].get('open') not in (False, None):
        raise ValueError('controller endpoint is open or unknown')
    if observed['consumerEndpoint'].get('open') not in (False, None):
        raise ValueError('consumer endpoint is open or unknown')
    if (observed['socket'].get('load') != 'loaded' or
            observed['socket'].get('fragment') !=
                '/usr/lib/systemd/system/rp1-gpclk-route-manager.socket' or
            observed['managerService'].get('load') != 'loaded' or
            observed['managerService'].get('fragment') !=
                '/usr/lib/systemd/system/rp1-gpclk-route-manager@.service'):
        raise ValueError('systemd runtime unit identity conflict')
    if observed['managerSocket'].get('status') == 'unsafe' or (
            observed['socket'].get('active') == 'active' and
            observed['managerSocket'].get('status') != 'owned') or (
            observed['socket'].get('active') != 'active' and
            observed['managerSocket'].get('status') != 'absent'):
        raise ValueError('manager socket identity conflict')
    if not already and not observed['inhibited']:
        raise ValueError('reviewed deployment inhibition is absent')
    if not already and observed['applicationService'].get('active') not in ('inactive', 'failed'):
        raise ValueError('application is not stopped behind deployment inhibition')
    return {'version': 1, 'operation': 'neutral-activation',
        'bindingSha256': observed['bindingSha256'],
        'artifactSetSha256': observed['artifactSetSha256'],
        'bootId': observed['bootId'],
        'lastDeploymentSha256': observed['lastDeploymentSha256'],
        'application': observed['application'],
        'socketWasActive': observed['socket'].get('active') == 'active',
        'alreadyReady': already,
        'previousActivationSha256': (admin.digest(canonical(journal))
                                     if journal is not None else None)}


def _save(system, record, phase, **values):
    record.update(phase=phase, **values)
    system.write_journal(record)


def ensure(system, reviewed, approved, lock=deployment.mutation_lock):
    validate_plan(reviewed)
    if plan_digest(reviewed) != approved:
        raise ValueError('reviewed neutral activation plan digest required')
    record = None
    try:
        with lock():
            current = activation_plan(system)
            if current != reviewed:
                raise ValueError('neutral activation plan changed since review')
            if current['alreadyReady']:
                return {'status': 'idempotent-no-change', 'journal': system.read_record(JOURNAL)}
            previous = system.read_record(JOURNAL)
            if previous is not None:
                if previous['phase'] != 'recovered-inhibited':
                    raise ValueError('activation journal is not restartable')
                system.archive_journal(previous)
            record = {'version': 1, 'plan': current, 'planSha256': approved,
                'requestId': str(uuid.uuid4()), 'phase': 'activation-intent',
                'controller': None, 'manager': None, 'application': None, 'error': None}
            system.write_journal(record)
            _save(system, record, 'controller-load-intent')
            system.load_controller()
            observed = observe(system)
            state = observed['controllerState']
            if (observed['controller'].get('exact') is not True or
                    observed['consumer']['status'] != 'absent' or
                    observed['consumerEndpoint']['status'] != 'absent' or
                    not state or any(state[name] for name in ('generation', 'id', 'error', 'route', 'flags'))):
                raise ValueError('controller did not establish exact neutral state')
            _save(system, record, 'socket-start-intent', controller=state)
            if not current['socketWasActive']:
                system.start_socket()
            observed = observe(system)
            if (observed['socket'].get('active') != 'active' or
                    observed['managerSocket'].get('status') != 'owned' or
                    observed['socket'].get('fragment') !=
                        '/usr/lib/systemd/system/rp1-gpclk-route-manager.socket' or
                    observed['managerService'].get('load') != 'loaded' or
                    observed['managerService'].get('fragment') !=
                        '/usr/lib/systemd/system/rp1-gpclk-route-manager@.service'):
                raise ValueError('exact manager socket/service infrastructure is unavailable')
            _save(system, record, 'manager-query-intent')
        reply = system.manager_query()
        state = reply.get('state', {}) if isinstance(reply, dict) else {}
        if (reply.get('status') != 'ok' or state.get('activeRoute') is not None or
                state.get('controller') != record['controller'] or
                state.get('bindingSha256') != reviewed['bindingSha256']):
            raise ValueError('manager did not confirm exact neutral controller state')
        with lock():
            current_record = system.read_record(JOURNAL)
            validate_journal(current_record)
            if current_record['requestId'] != record['requestId'] or current_record['phase'] != 'manager-query-intent':
                raise ValueError('activation journal changed during manager query')
            observed = observe(system)
            if (observed['bindingSha256'] != reviewed['bindingSha256'] or
                    observed['artifactSetSha256'] != reviewed['artifactSetSha256'] or
                    observed['lastDeploymentSha256'] != reviewed['lastDeploymentSha256'] or
                    observed['bootId'] != reviewed['bootId'] or
                    observed['controllerState'] != record['controller'] or
                    observed['consumer']['status'] != 'absent' or
                    observed['consumerEndpoint']['status'] != 'absent' or
                    observed['socket'].get('active') != 'active' or
                    observed['managerSocket'].get('status') != 'owned'):
                raise ValueError('activation identity changed before application restoration')
            _save(system, record, 'application-restore-intent', manager=reply)
            outcome = system.restore_application(reviewed['application'])
            observed = observe(system)
            if (observed['consumer']['status'] != 'absent' or
                    observed['consumerEndpoint']['status'] != 'absent' or
                    observed['controllerState'] != record['controller'] or observed['inhibited'] or
                    not application_matches(reviewed['application'],
                                            observed['applicationService'])):
                raise ValueError('neutral state changed during application restoration')
            _save(system, record, 'complete-neutral', application=outcome)
            return {'status': 'activated-neutral', 'journal': record}
    except BaseException as error:
        if record is not None:
            try:
                with lock():
                    try:
                        system.inhibit_application()
                    except BaseException as inhibition_error:
                        error = ValueError(str(error) + '; inhibition failure: ' + str(inhibition_error))
                    _save(system, record, 'activation-failed', error=str(error))
            except BaseException:
                pass
        raise


def recovery_plan(system):
    observed = observe(system)
    journal = observed['activationJournal']
    if journal is None:
        raise ValueError('no neutral activation journal to recover')
    validate_journal(journal)
    if journal['plan']['bootId'] != observed['bootId']:
        raise ValueError('cross-boot neutral activation requires investigation')
    if (journal['plan']['bindingSha256'] != observed['bindingSha256'] or
            journal['plan']['artifactSetSha256'] != observed['artifactSetSha256'] or
            journal['plan']['lastDeploymentSha256'] != observed['lastDeploymentSha256']):
        raise ValueError('activation provenance changed; preserve for investigation')
    if (observed['controller']['status'] == 'loaded' and
            observed['controller'].get('exact') is not True):
        raise ValueError('foreign or mismatched controller blocks neutral recovery')
    return {'version': 1, 'operation': 'neutral-activation-recovery',
        'activationJournalSha256': admin.digest(canonical(journal)),
        'bindingSha256': observed['bindingSha256'], 'bootId': observed['bootId'],
        'controllerLoaded': observed['controller']['status'] == 'loaded',
        'socketWasActive': journal['plan']['socketWasActive'],
        'alreadyRecovered': journal['phase'] == 'recovered-inhibited'}


def ensure_recovery(system, reviewed, approved, lock=deployment.mutation_lock):
    if plan_digest(reviewed) != approved:
        raise ValueError('reviewed neutral recovery plan digest required')
    with lock():
        if recovery_plan(system) != reviewed:
            raise ValueError('neutral recovery plan changed since review')
        if reviewed['alreadyRecovered']:
            return {'status': 'idempotent-no-change'}
        journal = system.read_record(JOURNAL)
        _save(system, journal, 'rollback-intent')
        try:
            system.inhibit_application()
            observed = observe(system)
            if observed['consumer']['status'] != 'absent' or observed['consumerEndpoint']['status'] != 'absent':
                raise ValueError('consumer state blocks neutral recovery')
            if observed['controller']['status'] == 'loaded':
                state = observed['controllerState']
                if not state or any(state[name] for name in ('generation', 'id', 'error', 'route', 'flags')):
                    raise ValueError('non-neutral controller blocks unload')
                system.unload_controller()
            if not reviewed['socketWasActive']:
                system.stop_socket()
            observed = observe(system)
            if (observed['controller']['status'] != 'absent' or
                    observed['controllerEndpoint']['status'] != 'absent' or
                    (not reviewed['socketWasActive'] and
                     (observed['socket'].get('active') == 'active' or
                      observed['managerSocket'].get('status') != 'absent')) or
                    (reviewed['socketWasActive'] and
                     (observed['socket'].get('active') != 'active' or
                      observed['managerSocket'].get('status') != 'owned' or
                      observed['socket'].get('fragment') !=
                        '/usr/lib/systemd/system/rp1-gpclk-route-manager.socket' or
                      observed['managerService'].get('load') != 'loaded' or
                      observed['managerService'].get('fragment') !=
                        '/usr/lib/systemd/system/rp1-gpclk-route-manager@.service'))):
                raise ValueError('controller remains after neutral recovery')
            _save(system, journal, 'recovered-inhibited', controller=None,
                  manager=None, application=None, error=None)
            return {'status': 'recovered-inhibited', 'journal': journal}
        except BaseException as error:
            _save(system, journal, 'rollback-failed', error=str(error))
            raise
