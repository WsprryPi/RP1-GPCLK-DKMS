#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Exercise qualification-only installation without DKMS product mutation."""
from __future__ import annotations

import importlib.util
import json
import pathlib
import shutil
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "qualification_installer", ROOT / "scripts/install_qualification.py")
assert spec and spec.loader
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)

with tempfile.TemporaryDirectory() as temporary:
    root = pathlib.Path(temporary)
    source = root / "qualification-source"
    shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    include = root / "usr/include/linux"
    include.mkdir(parents=True)
    shutil.copyfile(ROOT / "include/uapi/linux/rp1_gpclk.h", include / "rp1_gpclk.h")
    product = root / "usr/src/rp1-gpclk-dkms-0.0.0-phase5.53"
    product.mkdir(parents=True)
    sentinel = product / "dkms.conf"
    sentinel.write_text('PACKAGE_NAME="rp1-gpclk-dkms"\n')
    before = sentinel.read_bytes()

    def fake_cc(argv, **kwargs):
        assert argv[0] == "cc" and kwargs["check"] is True
        pathlib.Path(argv[argv.index("-o") + 1]).write_bytes(b"qualified-test-binary")
        return None

    state = installer.install(source, root, runner=fake_cc)
    assert state["status"] == "complete" and state["productMutation"] is False
    assert state["commands"] and all(command[0] == "cc" for command in state["commands"])
    assert all(pathlib.Path(command[0]).name not in {"dkms", "modprobe", "dtoverlay", "reboot"}
               for command in state["commands"])
    assert sentinel.read_bytes() == before
    assert (root / "usr/libexec/rp1-gpclk-dkms/gate-d-executor").is_file()
    assert (root / "usr/libexec/rp1-gpclk-dkms/gate-d-uapi-probe").is_file()
    ledger = root / "var/lib/rp1-gpclk-dkms/qualification.json"
    assert json.loads(ledger.read_text())["status"] == "complete"

    removed = installer.remove(root)
    assert removed["status"] == "removed"
    assert sentinel.read_bytes() == before
    assert not (root / "usr/libexec/rp1-gpclk-dkms/gate-d-executor").exists()

source = (ROOT / "scripts/install_qualification.py").read_text()
for prohibited in ('["dkms"', '["modprobe"', '["dtoverlay"', '["reboot"'):
    assert prohibited not in source
print("Phase 5.53 qualification-only installer: PASS")
