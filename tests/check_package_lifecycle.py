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
    source = root/'usr/src/rp1-gpclk-dkms-1.0.0'
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
        for version in ('1.0.0', '0.9.0', '9.9.9'):
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
        metadata.symlink_to('1.0.0/6.18.50+rpt-rpi-2712/aarch64')
        with self.assertRaisesRegex(ValueError, 'orphan'):
            guard.check(root, 'remove')
        metadata.unlink()
        version = base/'1.0.0'
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
        base = root/'var/lib/dkms/rp1-gpclk-dkms/1.0.0'
        base.mkdir(parents=True)
        (base/'source').symlink_to(source)
        kernel = '6.18.50+rpt-rpi-2712'
        (base.parent/('kernel-'+kernel+'-aarch64')).symlink_to('1.0.0/'+kernel+'/aarch64')
        put(root, 'lib/modules/'+kernel+'/build/.config', b'# unsigned header fixture\n')
        # Compact bytes test identity mechanics, not ELF/signature validity.
        elf = b'\x7fELF\x02\x01\0version=1.0.0\0signed-fixture-trailer'
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


if __name__ == '__main__':
    unittest.main()
