#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Verify passive package payload and fail-before-DKMS administration guards."""
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import package_stage as stage
import package_preflight as guard

ROOT = Path(__file__).resolve().parents[1]


class Tests(unittest.TestCase):
    def test_package_build_and_module_closure(self):
        sources = stage.payload_sources()
        self.assertIn('usr/src/rp1-gpclk-dkms-1.0.0/controller/main.c', sources)
        for name in ('rp1_gpclk.h', 'rp1_route_admin.h'):
            self.assertIn('usr/src/rp1-gpclk-dkms-1.0.0/include/uapi/linux/'+name, sources)
        rendered = stage.render_dkms((ROOT/'dkms.conf').read_text())
        for value in ('PACKAGE_VERSION="1.0.0"', 'RP1_RUNTIME_CONTROLLER=1',
                      'BUILT_MODULE_NAME[1]="rp1_route_controller"'):
            self.assertIn(value, rendered)
        self.assertNotIn('#MODULE_VERSION#', rendered)
        self.assertEqual((ROOT/'debian/rp1-gpclk-dkms.dkms').read_text(), 'debian/build/dkms.conf\n')
        self.assertIn('dh_installsystemd --no-scripts --no-enable --no-start', (ROOT/'debian/rules').read_text())
        self.assertIn('dh_builddeb -- -Zgzip -z9 --threads-max=1', (ROOT/'debian/rules').read_text())
        self.assertFalse(any(p.startswith(('boot/', 'etc/', 'dev/', 'lib/modules/')) for p in sources))

    def test_passive_scripts(self):
        for name in ('preinst', 'postinst', 'prerm'):
            text = (ROOT/f'debian/rp1-gpclk-dkms.{name}').read_text()
            for token in ('systemctl', 'deb-systemd', 'modprobe', 'insmod', 'rmmod',
                          'dtoverlay', '/boot/', 'gpioset'):
                self.assertNotIn(token, text)
        self.assertIn('package_preflight.py configure', (ROOT/'debian/rp1-gpclk-dkms.postinst').read_text())
        self.assertIn('package_preflight.py remove', (ROOT/'debian/rp1-gpclk-dkms.prerm').read_text())

    def test_guard_preserves_inactive_and_foreign_state(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(guard, 'OWNER_UID', os.getuid()):
            root = Path(directory).resolve()
            guard.check(root)
            for name in ('sys/module/rp1_gpclk_dkms', 'sys/module/rp1_route_controller',
                         'dev/rp1-gpclk', 'etc/rp1-gpclk-dkms/runtime-controller.json',
                         'var/lib/rp1-gpclk-dkms/runtime-admin',
                         'etc/systemd/system/wsprrypi.service.d/90-rp1-route-inhibit.conf'):
                path = root/name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'foreign')
                with self.assertRaises(ValueError):
                    guard.check(root)
                self.assertEqual(path.read_bytes(), b'foreign')
                path.unlink()
            path.symlink_to(root/'missing')
            with self.assertRaises(ValueError):
                guard.check(root)

    def test_framework_actions_and_dynamic_inputs_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(guard, 'OWNER_UID', os.getuid()):
            root = Path(directory).resolve()
            path = root/'etc/dkms/framework.conf'
            path.parent.mkdir(parents=True)
            for value in ('modprobe_on_install="false"', 'post_transaction="echo unsafe"',
                          'symlink_modules="yes"', 'source_tree="/foreign"',
                          'mok_signing_key="$(touch /foreign)"', '. /foreign'):
                path.write_text(value+'\n')
                with self.assertRaises(ValueError):
                    guard.check(root)
            path.write_text('# administrator configuration\nmodprobe_on_install=""\n')
            guard.check(root)

    def test_generated_module_ownership_and_compression(self):
        import gzip
        import lzma
        with tempfile.TemporaryDirectory() as directory, patch.object(guard, 'OWNER_UID', os.getuid()):
            root = Path(directory).resolve()
            kernel = '6.18.50+rpt-rpi-2712'
            module = root/'lib/modules'/kernel/'updates/dkms/rp1_gpclk_dkms.ko.xz'
            module.parent.mkdir(parents=True)
            elf = b'\x7fELF\x02\x01\x00version=1.0.0\x00fixture'
            module.write_bytes(lzma.compress(elf))
            with self.assertRaises(ValueError):
                guard.check(root)
            base = root/'var/lib/dkms/rp1-gpclk-dkms/1.0.0'
            cache = base/kernel/'aarch64/module/rp1_gpclk_dkms.ko'
            cache.parent.mkdir(parents=True)
            cache.write_bytes(elf)
            source = root/'usr/src/rp1-gpclk-dkms-1.0.0'
            source.mkdir(parents=True)
            (base/'source').symlink_to(source)
            guard.check(root)
            guard.check(root, 'remove')
            cache.write_bytes(elf+b'substitution')
            with self.assertRaises(ValueError):
                guard.check(root, 'remove')
            self.assertEqual(lzma.decompress(module.read_bytes()), elf)
            cache.write_bytes(elf)
            module.unlink()
            module = module.with_suffix('.gz')
            module.write_bytes(gzip.compress(elf))
            guard.check(root, 'remove')
            import bz2
            module.unlink()
            module = module.with_suffix('.bz2')
            module.write_bytes(bz2.compress(elf))
            guard.check(root, 'remove')
            if sys.platform == 'linux':
                import subprocess
                module.unlink()
                module = module.with_suffix('.zst')
                module.write_bytes(subprocess.check_output(['/usr/bin/zstd', '-q', '-c'], input=elf))
                guard.check(root, 'remove')
            backup = base.parent/'original_module'
            backup.mkdir()
            with self.assertRaises(ValueError):
                guard.check(root, 'remove')

    def test_pre_unpack_rejects_foreign_or_modified_files(self):
        import subprocess
        text = (ROOT/'debian/rp1-gpclk-dkms.preinst').read_text()
        program = text.split("<<'GUARD'\n", 1)[1].split('\nGUARD', 1)[0]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            target = root/'usr/sbin/rp1-gpclk-route-manager'
            target.parent.mkdir(parents=True)
            target.write_bytes(b'foreign administrator bytes')
            # Execute the actual embedded read-only guard against a mapped fixture.
            def mapped(value):
                return root/str(value).lstrip('/')
            with patch('pathlib.Path', mapped), patch('subprocess.run') as command:
                command.return_value = subprocess.CompletedProcess([], 1, '', '')
                with self.assertRaises(SystemExit):
                    exec(compile(program, 'preinst-fixture', 'exec'), {})
            self.assertEqual(target.read_bytes(), b'foreign administrator bytes')
            def owner_then_modified(argv, **unused):
                if argv[0] == 'dpkg-query':
                    return subprocess.CompletedProcess(argv, 0, 'rp1-gpclk-dkms: '+str(target)+'\n', '')
                return subprocess.CompletedProcess(argv, 0, b'??5?????? modified\n', b'')
            with patch('pathlib.Path', mapped), patch('subprocess.run', side_effect=owner_then_modified):
                with self.assertRaises(SystemExit):
                    exec(compile(program, 'preinst-fixture', 'exec'), {})
            self.assertEqual(target.read_bytes(), b'foreign administrator bytes')
            target.unlink()
            target.symlink_to(root/'missing')
            with patch('pathlib.Path', mapped), self.assertRaises(SystemExit):
                exec(compile(program, 'preinst-fixture', 'exec'), {})
            self.assertTrue(target.is_symlink())

    def test_signing_and_multiple_kernel_headers(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(guard, 'OWNER_UID', os.getuid()):
            root = Path(directory).resolve()
            for kernel in ('6.12.75+rpt-rpi-v8', '6.18.34+rpt-rpi-2712'):
                config = root/'lib/modules'/kernel/'build/.config'
                config.parent.mkdir(parents=True)
                config.write_text('CONFIG_MODULE_SIG_HASH="sha256"\n')
            with self.assertRaises(FileNotFoundError):
                guard.check(root)
            key = root/'var/lib/dkms/mok.key'
            key.parent.mkdir(parents=True)
            key.write_bytes(b'fixture existing key, never distributed')
            key.chmod(0o600)
            cert = key.with_name('mok.pub')
            cert.write_bytes(b'\xff\x00public certificate')
            guard.check(root)
            configuration = root/'etc/dkms/framework.conf'
            configuration.parent.mkdir(parents=True)
            configuration.write_text('sign_file="/foreign-signing-tool"\n')
            with self.assertRaises(OSError):
                guard.check(root)
            configuration.unlink()
            key.chmod(0o644)
            with self.assertRaises(ValueError):
                guard.check(root)
            self.assertEqual(cert.read_bytes(), b'\xff\x00public certificate')
            (root/'lib/modules/6.18.34+rpt-rpi-2712/build/.config').unlink()
            with self.assertRaises(ValueError):
                guard.check(root)
            guard.check(root, 'remove')


if __name__ == '__main__':
    unittest.main()
