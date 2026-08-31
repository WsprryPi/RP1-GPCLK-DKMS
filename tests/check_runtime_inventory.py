#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Real read-only collector tests with fake filesystem and bounded child processes."""
import json
import lzma
from pathlib import Path
import struct
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import runtime_inventory as inv


def elf():
    names = b"\0.shstrtab\0.note.gnu.build-id\0"
    note = b"fixture-build-note"
    blob = bytearray(256)
    blob[:6] = b"\x7fELF\x02\x01"
    struct.pack_into("<Q", blob, 40, 64)
    struct.pack_into("<HHH", blob, 58, 64, 3, 1)
    struct.pack_into("<IIQQQQIIQQ", blob, 128, 1, 3, 0, 0, 256, len(names), 0, 0, 0, 0)
    struct.pack_into("<IIQQQQIIQQ", blob, 192, 11, 7, 0, 0, 256 + len(names), len(note), 0, 0, 0, 0)
    return bytes(blob) + names + note


class FakeReader:
    def __init__(self):
        self.reads = []
        self.boots = 0
        self.reboot = False
        self.unknown_note = False
        self.config = b"[all]\ndtoverlay=rp1-gpclk-gpio20\n"
        self.packed = lzma.compress(elf())

    def read(self, name, limit=inv.LIMIT):
        self.reads.append(name)
        if name == inv.FILES["bootId"]:
            self.boots += 1
            if self.reboot and self.boots > 1:
                return b"aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee\n"
            return b"11111111-2222-3333-4444-555555555555\n"
        if name == inv.FILES["bootConfig"]:
            return self.config
        if name == inv.FILES["loadOutputGate"]:
            return b"N\n"
        if name.endswith(".ko.xz"):
            return self.packed
        if name == inv.FILES["loadedBuildNote"]:
            if self.unknown_note:
                raise PermissionError("unknown")
            return b"fixture-build-note"
        return b"fixture\n"

    def entries(self, name):
        return []

    def endpoints(self):
        return [{"path": "fixture/gpio20", "status": "6f6b617900",
                 "wsprrypi,route": "00000002", "wsprrypi,pin": "00000014"}]


def run(argv):
    assert argv in inv.COMMANDS.values()
    if argv == inv.COMMANDS["kernel"]:
        return {"status": "observed", "text": "fixture-kernel\n"}
    if argv == inv.COMMANDS["installedModule"]:
        return {"status": "observed", "text": "filename: /lib/modules/fixture-kernel/updates/dkms/rp1_gpclk_dkms.ko.xz\n"}
    return {"status": "observed", "text": "fixture\n"}


class Tests(unittest.TestCase):
    def test_real_collector_flow(self):
        reader = FakeReader()
        value = inv.collect(reader, run)
        self.assertTrue(value["sameBoot"])
        self.assertFalse(value["atomic"])
        self.assertFalse(value["assessment"]["mutationAvailable"])
        self.assertEqual(value["assessment"]["bootRouteCandidates"], ["gpio20"])
        self.assertEqual(value["assessment"]["runtimeOwnership"], "not-established")
        self.assertEqual(value["assessment"]["operationLive"], "unknown")
        self.assertIn("boot-route-migration-review-required", value["assessment"]["blockers"])
        self.assertTrue(value["files"]["installedModuleBytes"]["buildNoteMatchesLoaded"])
        self.assertEqual(value["files"]["installedModuleBytes"]["decompressedSha256"], inv.sha(elf()))
        self.assertNotIn("/dev/rp1-gpclk", reader.reads)

    def test_reboot_and_unknown_observations(self):
        reader = FakeReader()
        reader.reboot = True
        reader.unknown_note = True
        value = inv.collect(reader, run)
        self.assertFalse(value["sameBoot"])
        self.assertIsNone(value["files"]["installedModuleBytes"]["buildNoteMatchesLoaded"])
        def failed(argv):
            return inv.unknown("timeout")
        value = inv.collect(reader, failed)
        self.assertEqual(value["files"]["installedModuleBytes"]["status"], "unknown")

    def test_configuration_is_not_treated_as_effective_state(self):
        reader = FakeReader()
        for config, candidates in [(b"include other.txt\n", []),
                                   (b"[none]\ndtoverlay=rp1-gpclk-gpio4\n", ["gpio4"]),
                                   (b"dtoverlay=rp1-gpclk-gpio4,param=1\n", ["gpio4"]),
                                   (b"#dtoverlay=rp1-gpclk-gpio4\n", [])]:
            reader.config = config
            value = inv.collect(reader, run)
            self.assertEqual(value["assessment"]["bootRouteCandidates"], candidates)
            self.assertEqual(value["assessment"]["bootSelectionInterpretation"], "candidates-only")
            self.assertFalse(value["assessment"]["mutationAvailable"])

    def test_modinfo_cannot_choose_an_arbitrary_path(self):
        for text in ("filename: /dev/rp1-gpclk\n", "filename: /tmp/module.ko.xz\n",
                     "filename: /lib/modules/other/updates/dkms/rp1_gpclk_dkms.ko.xz\n"):
            reader = FakeReader()
            def alternate(argv):
                return {"status": "observed", "text": text} if argv == inv.COMMANDS["installedModule"] else run(argv)
            value = inv.collect(reader, alternate)
            self.assertEqual(value["files"]["installedModuleBytes"]["status"], "unknown")
            self.assertFalse(any(p.endswith(".ko.xz") for p in reader.reads))
        reader = FakeReader()
        def traversal(argv):
            if argv == inv.COMMANDS["kernel"]:
                return {"status": "observed", "text": "../../foreign"}
            if argv == inv.COMMANDS["installedModule"]:
                return {"status": "observed", "text": "filename: /lib/modules/../../foreign/updates/dkms/rp1_gpclk_dkms.ko.xz\n"}
            return run(argv)
        inv.collect(reader, traversal)
        self.assertFalse(any("../" in p for p in reader.reads))

    def test_inventory_failures_remain_unknown(self):
        reader = FakeReader()
        reader.entries = lambda name: (_ for _ in ()).throw(PermissionError())
        reader.endpoints = lambda: (_ for _ in ()).throw(OSError())
        value = inv.collect(reader, run)
        self.assertEqual(value["endpoints"]["status"], "unknown")
        self.assertEqual(value["files"]["runtimeOverlays"]["status"], "unknown")
        self.assertIn("route-observation-incomplete", value["assessment"]["blockers"])

    def test_invalid_boot_id_never_reports_same_boot(self):
        reader = FakeReader()
        read = reader.read
        reader.read = lambda name, limit=inv.LIMIT: b"" if name == inv.FILES["bootId"] else read(name, limit)
        self.assertFalse(inv.collect(reader, run)["sameBoot"])

    def test_elf_and_compression_bounds(self):
        self.assertEqual(inv.module_note(elf()), b"fixture-build-note")
        for blob in (b"bad", elf()[:64], elf()[:-1]):
            with self.assertRaises(ValueError):
                inv.module_note(blob)
        for packed in (b"bad", lzma.compress(elf())[:-1], lzma.compress(elf()) + b"extra"):
            reader = FakeReader()
            reader.packed = packed
            self.assertEqual(inv.collect(reader, run)["files"]["installedModuleBytes"]["status"], "unknown")

    def test_regular_files_only_and_size_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "record"
            path.write_bytes(b"12345")
            self.assertEqual(inv.Reader().read(str(path), 5), b"12345")
            with self.assertRaises(ValueError):
                inv.Reader().read(str(path), 4)
            link = Path(tmp) / "link"
            link.symlink_to(path)
            with self.assertRaises(ValueError):
                inv.Reader().read(str(link))
            with self.assertRaises(ValueError):
                inv.Reader().read(tmp)

    def test_command_bounds_and_errors(self):
        self.assertEqual(inv.bounded_command((sys.executable, "-c", "print('ok')"))["text"], "ok\n")
        self.assertEqual(inv.bounded_command((sys.executable, "-c", "print('x'*1000)"), limit=50)["reason"], "command-output-limit")
        start = time.monotonic()
        self.assertEqual(inv.bounded_command((sys.executable, "-c", "import time; time.sleep(10)"), timeout=0.1)["reason"], "command-timeout")
        self.assertLess(time.monotonic() - start, 2)
        self.assertEqual(inv.bounded_command((sys.executable, "-c", "raise SystemExit(3)"))["exitCode"], 3)

    def test_effect_commands_are_not_available(self):
        self.assertEqual(set(inv.COMMANDS), {"kernel", "architecture", "packages", "services", "managerUnit", "installedModule"})
        for argv in inv.COMMANDS.values():
            self.assertNotIn("/usr/bin/dtoverlay", argv)
            self.assertNotIn("/usr/sbin/modprobe", argv)
            self.assertFalse(set(argv) & {"start", "stop", "restart", "reboot", "mask", "unmask"})
        self.assertFalse(any(path.startswith("/dev/") for path in inv.FILES.values()))


if __name__ == "__main__":
    unittest.main()
