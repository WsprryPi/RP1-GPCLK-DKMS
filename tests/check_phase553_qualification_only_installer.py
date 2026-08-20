#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Exercise qualification-only installation without DKMS product mutation."""
from __future__ import annotations

import importlib.util
import json
import pathlib
import shutil
import subprocess
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
    include = root / "usr/src/rp1-gpclk-dkms-0.0.0-phase5.53/include/uapi/linux"
    include.mkdir(parents=True)
    shutil.copyfile(ROOT / "include/uapi/linux/rp1_gpclk.h", include / "rp1_gpclk.h")
    product = root / "usr/src/rp1-gpclk-dkms-0.0.0-phase5.53"
    product.mkdir(parents=True, exist_ok=True)
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

with tempfile.TemporaryDirectory() as temporary:
    root = pathlib.Path(temporary)
    source = root / "qualification-source"
    shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    include = root / "usr/src/rp1-gpclk-dkms-0.0.0-phase5.53/include/uapi/linux"
    include.mkdir(parents=True)
    shutil.copyfile(ROOT / "include/uapi/linux/rp1_gpclk.h", include / "rp1_gpclk.h")

    def interrupted_cc(argv, **kwargs):
        pathlib.Path(argv[argv.index("-o") + 1]).write_bytes(b"partial-output")
        raise subprocess.CalledProcessError(1, argv)

    try:
        installer.install(source, root, runner=interrupted_cc)
        raise AssertionError("interrupted qualification build unexpectedly passed")
    except subprocess.CalledProcessError:
        pass
    ledger = root / "var/lib/rp1-gpclk-dkms/qualification.json"
    interrupted = json.loads(ledger.read_text())
    assert interrupted["status"] == "recovery-required"
    assert interrupted["pendingBuild"]["temporary"].endswith(".installing")
    installer.remove(root)
    assert not pathlib.Path(interrupted["pendingBuild"]["temporary"]).exists()
    assert not pathlib.Path(interrupted["pendingBuild"]["destination"]).exists()

with tempfile.TemporaryDirectory() as temporary:
    root = pathlib.Path(temporary)
    ledger = root / "var/lib/rp1-gpclk-dkms/qualification.json"
    ledger.parent.mkdir(parents=True)
    ledger.write_text(json.dumps({"status": "recovery-required", "pendingBuild": {
        "temporary": "/tmp/outside-root", "destination": "/tmp/outside-final"},
        "ownedFiles": [], "ownedDirectories": []}))
    try:
        installer.remove(root)
        raise AssertionError("escaping qualification ledger unexpectedly removed")
    except ValueError as error:
        assert "escapes root" in str(error)

with tempfile.TemporaryDirectory() as temporary:
    root = pathlib.Path(temporary)
    source = root / "qualification-source"
    shutil.copytree(ROOT, source, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    try:
        installer.install(source, root, runner=lambda argv, **kwargs: None)
        raise AssertionError("qualification install without product UAPI unexpectedly passed")
    except ValueError as error:
        assert "installed product UAPI is absent" in str(error)
    installer.remove(root)

source = (ROOT / "scripts/install_qualification.py").read_text()
for prohibited in ('["dkms"', '["modprobe"', '["dtoverlay"', '["reboot"'):
    assert prohibited not in source
print("Phase 5.53 qualification-only installer: PASS")
