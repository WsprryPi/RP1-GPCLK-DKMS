#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Offline ownership/fault regressions; these are not dpkg lifecycle evidence."""
import gzip
import hashlib
import lzma
import os
import json
import runpy
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
sys.path.insert(0, str(ROOT/'tools'))
import lifecycle_results as results
import package_preflight as guard
import package_stage as stage
import package_indices as indices
import package_signatures as signatures


def put(root, name, data=b'fixture'):
    path = root/name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def owned_source(root):
    source = root/'usr/src/rp1-gpclk-dkms-1.0.2'
    path = put(root, str(source.relative_to(root))+'/dkms.conf')
    database = root/'var/lib/dpkg/info'
    database.mkdir(parents=True, exist_ok=True)
    (database/'rp1-gpclk-dkms.list').write_text(
        '/'+str(source.relative_to(root))+'\n/'+str(path.relative_to(root))+'\n')
    (database/'rp1-gpclk-dkms.md5sums').write_text(
        hashlib.md5(path.read_bytes()).hexdigest()+'  '+str(path.relative_to(root))+'\n')
    return source


class Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.patch = patch.object(guard, 'OWNER_UID', os.getuid())
        self.patch.start()
        self.features = patch.object(guard, 'native_features', return_value={'+XZ', '+ZLIB', '+ZSTD'})
        self.features.start()

    def tearDown(self):
        self.features.stop()
        self.patch.stop()
        self.temp.cleanup()

    def test_foreign_unbuilt_registration_and_different_version(self):
        root = self.root
        base = root/'var/lib/dkms/rp1-gpclk-dkms'
        for version in ('1.0.2', '0.9.0', '9.9.9'):
            path = base/version
            path.mkdir(parents=True)
            for operation in ('unpack', 'configure', 'remove'):
                with self.subTest(version=version, operation=operation), self.assertRaises(ValueError):
                    guard.check(root, operation)
                self.assertTrue(path.is_dir())
            path.rmdir()

    def test_orphan_kernel_link_and_foreign_cache_file_are_preserved(self):
        root = self.root
        source = owned_source(root)
        base = root/'var/lib/dkms/rp1-gpclk-dkms'
        base.mkdir(parents=True)
        metadata = base/'kernel-6.18.50+rpt-rpi-2712-aarch64'
        metadata.symlink_to('1.0.2/6.18.50+rpt-rpi-2712/aarch64')
        with self.assertRaisesRegex(ValueError, 'orphan'):
            guard.check(root, 'remove')
        metadata.unlink()
        version = base/'1.0.2'
        version.mkdir()
        (version/'source').symlink_to(source)
        foreign = put(root, str(version.relative_to(root))+'/foreign.txt', b'preserve')
        with self.assertRaises(ValueError):
            guard.check(root, 'remove')
        self.assertEqual(foreign.read_bytes(), b'preserve')
        foreign.unlink()
        copied = put(root, str(version.relative_to(root))+'/build/dkms.conf', b'changed source copy')
        with self.assertRaisesRegex(ValueError, 'modified DKMS source copy'):
            guard.check(root, 'remove')
        copied.write_bytes((source/'dkms.conf').read_bytes())
        guard.check(root, 'remove')
        copied.with_name('foreign').write_bytes(b'preserve cache evidence')
        with self.assertRaisesRegex(ValueError, 'foreign DKMS build file'):
            guard.check(root, 'remove')

    def test_drift_and_unlisted_files_are_preserved_before_removal(self):
        root = self.root
        source = owned_source(root)
        guard.check(root)
        config = source/'dkms.conf'
        config.write_bytes(b'administrator changes')
        for operation in ('unpack', 'configure', 'remove'):
            with self.assertRaisesRegex(ValueError, 'modified package'):
                guard.check(root, operation)
        self.assertEqual(config.read_bytes(), b'administrator changes')
        config.write_bytes(b'fixture')
        config.chmod(0o755)
        with self.assertRaisesRegex(ValueError, 'modified package mode'):
            guard.check(root, 'remove')
        config.chmod(0o644)
        foreign = source/'foreign'
        foreign.write_bytes(b'retain')
        with self.assertRaisesRegex(ValueError, 'foreign package descendant'):
            guard.check(root, 'remove')
        self.assertEqual(foreign.read_bytes(), b'retain')
        foreign.unlink()
        config.unlink()
        with self.assertRaisesRegex(ValueError, 'missing package'):
            guard.check(root)
        # dpkg may restore missing bytes on reinstall, or finish removal.
        guard.check(root, 'unpack')
        guard.check(root, 'remove')

    def test_runtime_development_and_application_ownership_refusal(self):
        root = self.root
        for name in (
            'var/lib/wsprrypi/rp1-gpclk-dkms-installation.json',
            'etc/rp1-gpclk-dkms/development/record.json',
            'usr/lib/rp1-gpclk-dkms/runtime_activation.py',
            'usr/lib/rp1-gpclk-dkms/package_preflight.py',
            'usr/lib/rp1-gpclk-dkms/runtime-uapi/rp1_gpclk.h',
            'usr/lib/rp1-gpclk-dkms/runtime-overlays/gpio20.dtbo',
            'etc/systemd/system/rp1-gpclk-route-manager@.service.d/95-runtime-controller.conf'):
            path = put(root, name, b'foreign or owning workflow evidence')
            for operation in ('unpack', 'configure', 'remove'):
                with self.subTest(name=name, operation=operation), self.assertRaises(ValueError):
                    guard.check(root, operation)
                self.assertEqual(path.read_bytes(), b'foreign or owning workflow evidence')
            path.unlink()
            # Empty directories remain residue too; remove only fixture parents.
            parent = path.parent
            while parent != root:
                try:
                    parent.rmdir()
                except OSError:
                    break
                parent = parent.parent

    def test_removal_refuses_overrides_without_executing_them(self):
        path = put(self.root, 'etc/dkms/rp1-gpclk-dkms.conf', b'PRE_REMOVE="foreign"\n')
        with patch('subprocess.run') as command:
            with self.assertRaisesRegex(ValueError, 'module override'):
                guard.check(self.root, 'remove')
            command.assert_not_called()
        self.assertEqual(path.read_bytes(), b'PRE_REMOVE="foreign"\n')

    def test_compressed_signed_identity_and_duplicate_refusal(self):
        root = self.root
        source = owned_source(root)
        base = root/'var/lib/dkms/rp1-gpclk-dkms/1.0.2'
        base.mkdir(parents=True)
        (base/'source').symlink_to(source)
        kernel = '6.18.50+rpt-rpi-2712'
        (base.parent/('kernel-'+kernel+'-aarch64')).symlink_to('1.0.2/'+kernel+'/aarch64')
        put(root, 'lib/modules/'+kernel+'/build/.config', b'# unsigned header fixture\n')
        # Compact bytes test identity mechanics, not ELF/signature validity.
        elf = b'\x7fELF\x02\x01\0version=1.0.2\0signed-fixture-trailer'
        cache = put(root, str(base.relative_to(root))+'/'+kernel+'/aarch64/module/rp1_gpclk_dkms.ko', elf)
        stem = 'lib/modules/'+kernel+'/updates/dkms/rp1_gpclk_dkms.ko'
        for suffix, encode in (('', lambda x:x), ('.gz', gzip.compress), ('.xz', lzma.compress)):
            module = put(root, stem+suffix, encode(elf))
            guard.check(root, 'remove')
            cache.write_bytes(elf+b'drift')
            with self.assertRaisesRegex(ValueError, 'modified provider module'):
                guard.check(root, 'remove')
            cache.write_bytes(elf)
            module.unlink()
        first = put(root, stem, elf)
        second = put(root, stem+'.xz', lzma.compress(elf))
        with self.assertRaisesRegex(ValueError, 'duplicate compressed'):
            guard.check(root, 'remove')
        self.assertEqual(first.read_bytes(), elf)
        self.assertEqual(lzma.decompress(second.read_bytes()), elf)

    def test_incoming_guard_is_exact_source_and_before_debhelper(self):
        destination = self.root/'package'
        control = destination/'DEBIAN'
        control.mkdir(parents=True)
        path = control/'preinst'
        path.write_bytes((ROOT/'debian/rp1-gpclk-dkms.preinst').read_bytes())
        stage.preinst(destination)
        text = path.read_text()
        self.assertIn((ROOT/'scripts/package_preflight.py').read_text(), text)
        self.assertLess(text.index("python3 -I - unpack"), text.index('#DEBHELPER#'))
        for name in ('postinst', 'prerm'):
            self.assertIn('python3 -I /usr/libexec/rp1-gpclk-dkms/package_preflight.py',
                          (ROOT/('debian/rp1-gpclk-dkms.'+name)).read_text())
        with self.assertRaises(ValueError):
            stage.preinst(destination)

    def test_authoritative_predecessor_and_transformation_scope(self):
        builder = runpy.run_path(str(ROOT/'scripts/build-lifecycle-predecessor'))
        record = json.loads((ROOT/'release/lifecycle-predecessor-v1.json').read_text())
        builder['select'](record['sourceCommit'], record)
        for name in ('devel', record['sourceCommit'][:12], 'f825e5f4b7b1c64b31f663088869b790598c8b8c'):
            with self.assertRaisesRegex(ValueError, 'predecessor'):
                builder['select'](name, record)
        files = {name: (0o644, data) for name, data in {
            'debian/rules': b'# fixture historical rules\n',
            'include/rp1_gpclk/version.h': b'#define RP1_GPCLK_MODULE_VERSION "0.9.0"\n',
            'include/uapi/linux/rp1_gpclk.h': b'fixture consumer UAPI',
            'include/uapi/linux/rp1_route_admin.h': b'fixture controller UAPI',
            'debian/rp1-gpclk-dkms.postinst': b'fixture unchanged historical install',
            'debian/rp1-gpclk-dkms.prerm': b'fixture unchanged historical removal',
            'src/rp1_gpclk_main.c': b'fixture exact runtime bytes'}.items()}
        record = dict(record)
        for name, key in (('debian/rules', 'rulesSha256'),
                          ('include/uapi/linux/rp1_gpclk.h', 'consumerUapiSha256'),
                          ('include/uapi/linux/rp1_route_admin.h', 'controllerUapiSha256')):
            record[key] = hashlib.sha256(files[name][1]).hexdigest()
        rendered, changes = builder['render'](files, record)
        self.assertEqual([n for n in files if files[n] != rendered[n]], ['debian/rules'])
        self.assertEqual(changes[0]['appendedBytes'], builder['TRANSFORM'])
        for name in ('debian/rp1-gpclk-dkms.postinst', 'debian/rp1-gpclk-dkms.prerm',
                     'src/rp1_gpclk_main.c', 'include/uapi/linux/rp1_gpclk.h'):
            self.assertEqual(files[name], rendered[name])
        changed = dict(files)
        mode, data = files['debian/rules']
        changed['debian/rules'] = mode, data+b'# unrecorded\n'
        with self.assertRaises(ValueError):
            builder['render'](changed, record)

    def test_removal_framework_cannot_redirect_compression_or_hooks(self):
        path = put(self.root, 'etc/dkms/framework.conf')
        for text in ('compress_zstd_opts="-o /boot/config.txt"',
                     'autoinstall_all_kernels=""', 'tmp_location="/foreign"',
                     'sign_tool="/foreign"'):
            path.write_text(text+'\n')
            with self.assertRaises(ValueError):
                guard.check(self.root, 'remove')

    def test_missing_native_compression_is_refused_before_mutation(self):
        path = put(self.root, 'lib/modules/6.18.50+rpt-rpi-2712/kernel/foreign.ko.gz', gzip.compress(b'fixture'))
        with patch.object(guard, 'native_features', return_value={'+XZ', '+ZSTD'}):
            with self.assertRaisesRegex(ValueError, 'compression support'):
                guard.check(self.root, 'remove')
        self.assertEqual(gzip.decompress(path.read_bytes()), b'fixture')

    def test_explicit_depmod_failure_and_retry_are_not_masked(self):
        import subprocess
        kernel = '6.18.50+rpt-rpi-2712'
        for name in ('rp1_gpclk_dkms', 'rp1_route_controller'):
            put(self.root, 'lib/modules/'+kernel+'/updates/dkms/'+name+'.ko')
        put(self.root, 'lib/modules/'+kernel+'/build/.config', b'# unsigned fixture\n')
        command = ['/usr/sbin/depmod', '-b', str(self.root), '-a', kernel]
        with patch.object(indices, 'check'), patch.object(indices.subprocess, 'run') as run:
            run.return_value = subprocess.CompletedProcess(command, 64, '', 'underlying depmod failure')
            with self.assertRaises(indices.IndexFailure) as caught:
                indices.update(self.root)
            self.assertEqual(caught.exception.result['exitStatus'], 64)
            self.assertEqual(caught.exception.result['command'], command)
            self.assertIn('underlying depmod failure', caught.exception.result['diagnostic'])
            run.return_value = subprocess.CompletedProcess(command, 0, '', '')
            self.assertEqual(indices.update(self.root)['status'], 'complete')
            for path in (self.root/'lib/modules'/kernel/'updates/dkms').iterdir():
                path.unlink()
            self.assertEqual(indices.update(self.root, 'remove')['status'], 'complete')
            self.assertEqual(run.call_count, 3)

    def test_package_helper_never_creates_unowned_bytecode(self):
        import shutil
        import subprocess
        directory = self.root/'installed-helpers'
        directory.mkdir()
        for name in ('package_indices.py', 'package_preflight.py', 'package_signatures.py'):
            shutil.copyfile(ROOT/'scripts'/name, directory/name)
        subprocess.run([sys.executable, '-I', '-c',
                        'import runpy,sys; runpy.run_path(sys.argv[1])',
                        str(directory/'package_indices.py')], check=True)
        self.assertFalse((directory/'__pycache__').exists())

    def test_missing_malformed_and_unverifiable_signature_are_fail_closed(self):
        import struct
        import subprocess
        elf = b'\x7fELF\x02\x01fixture'
        cms = b'fixture CMS bytes'
        trailer = b'\0\0\x02\0\0\0\0\0'+struct.pack('>I', len(cms))
        signed = elf+cms+trailer+signatures.MAGIC
        self.assertEqual(signatures.split_signature(signed), (elf, cms))
        for data in (elf, signed[:-1], elf+cms+trailer[:8]+struct.pack('>I', 999999)+signatures.MAGIC):
            with self.assertRaises(ValueError):
                signatures.split_signature(data)
        certificate = put(self.root, 'public-certificate', b'fixture DER')
        with patch.object(signatures.subprocess, 'run') as command:
            command.return_value = subprocess.CompletedProcess(['openssl'], 7, '', 'bad certificate')
            with self.assertRaises(signatures.SignatureFailure) as caught:
                signatures.verify(signed, certificate, '/fixture/module.ko')
            self.assertEqual(caught.exception.result['exitStatus'], 7)
            self.assertEqual(caught.exception.result['stage'], 'signature')
            self.assertIn('bad certificate', caught.exception.result['diagnostic'])
            for error, status in ((FileNotFoundError('openssl missing'), 127),
                                  (subprocess.TimeoutExpired(['openssl'], 15), 124)):
                command.side_effect = error
                with self.assertRaises(signatures.SignatureFailure) as caught:
                    signatures.verify(signed, certificate, '/fixture/module.ko')
                self.assertEqual(caught.exception.result['exitStatus'], status)

    def test_lifecycle_matrix_resolves_complete_expected_states(self):
        matrix = json.loads((ROOT/'release/package-lifecycle-matrix-v1.json').read_text())
        fields = {'packageManager', 'dkms', 'modulesByKernel', 'sourceTree', 'overlays',
                  'routeRuntime', 'services', 'bootConfiguration', 'ownershipRecords',
                  'rollbackAvailability', 'operatorAction', 'machineResult', 'executionAuthorization'}
        for state in matrix['states'].values():
            self.assertEqual(set(state), fields)
            self.assertIs(state['executionAuthorization'], False)
        ids = set()
        for case in matrix['cases']:
            self.assertNotIn(case['id'], ids)
            ids.add(case['id'])
            self.assertIn(case['expectedState'], matrix['states'])
            expected = 2 if case['operation'] == 'concurrent-same-version-request' else (0 if case['disposition'] == 'permitted' else 1)
            self.assertEqual(case['exitStatus'], expected)
        self.assertEqual({case['disposition'] for case in matrix['cases']}, {'permitted', 'refused'})
        for case in matrix['cases']:
            if case['startingState'] in ('partly-configured-or-interrupted-remove',
                                          'partly-configured-or-interrupted-purge',
                                          'partly-configured-or-interrupted-remove-depmod'):
                self.assertEqual(case['expectedState'], 'absent')

    def test_lifecycle_outputs_refuse_another_git_checkout_before_docker(self):
        import subprocess
        import contextlib
        import io
        repository = self.root/'another-repository'
        repository.mkdir()
        subprocess.run(['git', 'init', '-q', str(repository)], check=True)
        driver = runpy.run_path(str(ROOT/'tools/run-package-lifecycle.py'))
        arguments = ['run-package-lifecycle', '--image', 'unused', '--candidate', str(self.root),
                     '--predecessor', str(self.root), '--output', str(repository/'results')]
        with patch.object(sys, 'argv', arguments), patch('subprocess.check_output') as docker:
            with contextlib.redirect_stderr(io.StringIO()) as diagnostic:
                with self.assertRaises(SystemExit) as error:
                    driver['main']()
            self.assertEqual(error.exception.code, 2)
            self.assertIn('outside every Git checkout', diagnostic.getvalue())
            docker.assert_not_called()
        self.assertFalse((repository/'results').exists())

    def test_results_are_private_with_a_shared_container_directory(self):
        import subprocess
        import contextlib
        import io
        import stat
        driver = runpy.run_path(str(ROOT/'tools/run-package-lifecycle.py'))
        output = self.root/'results'
        candidate, predecessor = result_inputs(self.root)
        arguments = ['run-package-lifecycle', '--image', 'unused', '--candidate', str(candidate),
                     '--predecessor', str(predecessor), '--output', str(output),
                     '--scenario', 'missing-headers']
        native = subprocess.run

        def command(argv, **kwargs):
            if argv[0] == 'docker':
                supplied = json.loads(next(a.split('=', 1)[1] for a in argv
                    if a.startswith('RP1_LIFECYCLE_CONTEXT=')))
                (output/'missing-headers/result.json').write_text(json.dumps(result_value(supplied)))
                return subprocess.CompletedProcess(argv, 0)
            return native(argv, **kwargs)

        with patch.object(sys, 'argv', arguments), patch('subprocess.run', side_effect=command), \
                patch('subprocess.check_output', return_value=json.dumps([{'Id': IMAGE}])), \
                patch.dict(driver['main'].__globals__, {'source_identity': lambda root: COMMIT}):
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as result:
                driver['main']()
        self.assertEqual(result.exception.code, 0)
        self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o700)
        self.assertEqual(stat.S_IMODE((output/'missing-headers').stat().st_mode), 0o777)
        report = json.loads((output/'result.json').read_text())
        self.assertTrue(report['scenarios'][0]['accepted'])


COMMIT = 'a' * 40
IMAGE = 'sha256:' + 'b' * 64


def result_inputs(root):
    candidate, predecessor = root/'candidate', root/'predecessor'
    candidate.mkdir(); predecessor.mkdir()
    for directory in (candidate, predecessor):
        (directory/'package.deb').write_bytes(b'package fixture, never installed')
    digest = hashlib.sha256((candidate/'package.deb').read_bytes()).hexdigest()
    (candidate/'rp1-gpclk-dkms-installation-manifest-v1.json').write_text(json.dumps({
        'sourceCommit': COMMIT, 'package': {'filename': 'package.deb', 'sha256': digest}}))
    (predecessor/'predecessor.json').write_text(json.dumps({
        'package': 'package.deb', 'packageSha256': digest}))
    return candidate, predecessor


def result_value(expected):
    # Independent wire fixture: do not derive its contract/keys from the producer.
    observed = {'endpointsAbsent': True, 'modulesUnloaded': True}
    return {'contract': 'rp1-gpclk-package-lifecycle-v2', 'schemaVersion': 2,
        **expected, 'status': 'PASS', 'error': None,
        'steps': [{'stage': 'checked-boundary', 'command': ['fixture'], 'exitStatus': 0,
                   'before': observed.copy(), 'after': observed.copy(), 'diagnosticTail': ''}],
        'realPackageManager': True, 'hardwareQualification': False, 'rfQualification': False}


class ResultTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.identity = {'sourceCommit': COMMIT, 'imageId': IMAGE,
            'candidatePackageSha256': 'c'*64, 'predecessorPackageSha256': 'd'*64}
        self.expected = results.context('e'*32, 'clean-cycle', self.identity)
        self.path = self.root/'result.json'

    def accept(self, value, code=0):
        self.path.write_text(json.dumps(value))
        return results.accept(self.path, self.expected, code)

    def test_positive_wire_and_producer_contract(self):
        value = result_value(self.expected)
        self.assertEqual(self.accept(value), value)
        self.assertEqual(results.envelope(self.expected, 'PASS', None, value['steps']), value)

    def test_attribution_types_safety_and_completed_work(self):
        import copy
        base = result_value(self.expected)
        mutations = [lambda v: v.update(schemaVersion=True),
            lambda v: v.update(schemaVersion=1), lambda v: v.update(contract='old'),
            lambda v: v.update(runId='f'*32), lambda v: v.update(scenario='foreign-state'),
            lambda v: v['identity'].update(sourceCommit='f'*40),
            lambda v: v['identity'].update(imageId='sha256:'+'f'*64),
            lambda v: v['identity'].update(candidatePackageSha256='f'*64),
            lambda v: v['identity'].update(predecessorPackageSha256='f'*64),
            lambda v: v.update(status='FAIL'), lambda v: v.update(error='failed'),
            lambda v: v.update(steps=[]), lambda v: v.update(realPackageManager=1),
            lambda v: v.update(hardwareQualification=True),
            lambda v: v.update(rfQualification=True), lambda v: v.update(extra=True),
            lambda v: v['steps'][0].update(exitStatus=True),
            lambda v: v['steps'][0]['after'].update(modulesUnloaded=1),
            lambda v: v['steps'][0]['before'].update(endpointsAbsent=False)]
        for change in mutations:
            value = copy.deepcopy(base); change(value)
            with self.subTest(change=change), self.assertRaises(ValueError): self.accept(value)
        for code in (1, -15, True):
            with self.subTest(code=code), self.assertRaises(ValueError): self.accept(base, code)

    def test_missing_unsafe_and_malformed_results(self):
        with self.assertRaises(OSError): results.accept(self.path, self.expected, 0)
        for data in ('{}', '{', '{"x":1,"x":2}', 'NaN'):
            self.path.write_text(data)
            with self.subTest(data=data), self.assertRaises(ValueError):
                results.accept(self.path, self.expected, 0)
        self.path.unlink(); self.path.symlink_to(self.root/'missing')
        with self.assertRaises(OSError): results.accept(self.path, self.expected, 0)
        self.path.unlink(); self.path.write_bytes(b'x'*(results.LIMIT+1))
        with self.assertRaises(ValueError): results.accept(self.path, self.expected, 0)

    def test_changed_result_during_read(self):
        self.path.write_text(json.dumps(result_value(self.expected)))
        real = results.os.fstat
        count = 0
        def observation(fd):
            nonlocal count
            count += 1
            if count == 2: self.path.write_bytes(b'changed')
            return real(fd)
        with patch.object(results.os, 'fstat', side_effect=observation):
            with self.assertRaisesRegex(ValueError, 'changed'): results.accept(self.path, self.expected, 0)

    def test_selection_context_and_package_substitution(self):
        for selected in ((), ('clean-cycle', 'clean-cycle'), ('unknown',)):
            with self.assertRaises(ValueError): results.selection(selected)
        self.assertEqual(results.selection(('clean-cycle',)), ('clean-cycle',))
        with self.assertRaises(ValueError): results.context('bad', 'clean-cycle', self.identity)
        candidate, predecessor = result_inputs(self.root)
        identity = results.input_identity(candidate, predecessor, IMAGE, COMMIT)
        self.assertEqual(identity['sourceCommit'], COMMIT)
        (candidate/'package.deb').write_bytes(b'changed')
        with self.assertRaises(ValueError): results.input_identity(candidate, predecessor, IMAGE, COMMIT)

    def test_source_rejects_hidden_worktree_changes(self):
        import subprocess
        source = self.root/'source'; source.mkdir()
        (source/'input').write_text('reviewed')
        def git(*args):
            return subprocess.run(['git', '-C', str(source), *args], check=True,
                                  capture_output=True, text=True).stdout.strip()
        git('init', '-q'); git('add', 'input')
        git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
            'commit', '-qm', 'fixture')
        self.assertEqual(results.source_identity(source), git('rev-parse', 'HEAD'))
        git('update-index', '--assume-unchanged', 'input')
        (source/'input').write_text('substituted')
        with self.assertRaisesRegex(ValueError, 'differs'): results.source_identity(source)

    def test_driver_rejects_false_success_and_collects_all_requested_results(self):
        import contextlib
        import io
        import subprocess
        candidate, predecessor = result_inputs(self.root)
        driver = runpy.run_path(str(ROOT/'tools/run-package-lifecycle.py'))
        native = subprocess.run
        for fault in ('none', 'missing', 'empty', 'stale', 'source', 'exit'):
            output = self.root/fault
            calls = []
            def command(argv, **kwargs):
                if argv[0] != 'docker': return native(argv, **kwargs)
                supplied = json.loads(next(a.split('=', 1)[1] for a in argv
                    if a.startswith('RP1_LIFECYCLE_CONTEXT=')))
                calls.append(supplied['scenario'])
                value = result_value(supplied)
                broken = supplied['scenario'] == results.SCENARIOS[0]
                if broken and fault == 'empty': value['steps'] = []
                if broken and fault == 'stale': value['runId'] = '0'*32
                if broken and fault == 'source': value['identity'] = dict(value['identity'], sourceCommit='0'*40)
                if not (broken and fault == 'missing'):
                    (output/supplied['scenario']/'result.json').write_text(json.dumps(value))
                return subprocess.CompletedProcess(argv, 1 if broken and fault == 'exit' else 0)
            args = ['driver', '--image', 'fixture', '--candidate', str(candidate),
                    '--predecessor', str(predecessor), '--output', str(output)]
            with self.subTest(fault=fault), patch.object(sys, 'argv', args), \
                    patch('subprocess.run', side_effect=command), \
                    patch('subprocess.check_output', return_value=json.dumps([{'Id': IMAGE}])), \
                    patch.dict(driver['main'].__globals__, {'source_identity': lambda root: COMMIT}), \
                    contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as caught:
                driver['main']()
            self.assertEqual(caught.exception.code, 0 if fault == 'none' else 1)
            self.assertEqual(tuple(calls), results.SCENARIOS)
            report = json.loads((output/'result.json').read_text())
            self.assertEqual(len(report['scenarios']), len(results.SCENARIOS))


if __name__ == '__main__':
    unittest.main()
