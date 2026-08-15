#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
module_spec = importlib.util.spec_from_file_location("gate_d_boot", ROOT / "scripts/gate_d_boot.py")
assert module_spec and module_spec.loader
boot = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(boot)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


with tempfile.TemporaryDirectory() as temporary:
    root = pathlib.Path(temporary)
    firmware = root / "boot/firmware"
    evidence = root / "var/lib/rp1-gpclk-dkms/gate-d/boot"
    firmware.mkdir(parents=True)
    evidence.mkdir(parents=True)
    config_bytes = b"arm_64bit=1\n[all]\n"
    tryboot_bytes = b"kernel=unrelated-historical.img\n"
    kernel_bytes = b"stock-kernel-6.12"
    initramfs_bytes = b"stock-initramfs-6.12"
    (firmware / "config.txt").write_bytes(config_bytes)
    (firmware / "tryboot.txt").write_bytes(tryboot_bytes)
    (root / "boot/vmlinuz-6.12").write_bytes(kernel_bytes)
    (root / "boot/initrd.img-6.12").write_bytes(initramfs_bytes)
    operation = {
        "schemaVersion": 1, "operationId": "prior-stock-test", "targetKernel": "6.12",
        "sourceKernel": "/boot/vmlinuz-6.12", "sourceKernelSha256": sha(kernel_bytes),
        "sourceInitramfs": "/boot/initrd.img-6.12", "sourceInitramfsSha256": sha(initramfs_bytes),
        "config": "/boot/firmware/config.txt", "configSha256": sha(config_bytes),
        "tryboot": "/boot/firmware/tryboot.txt", "trybootSha256": sha(tryboot_bytes),
        "stagedKernel": "/boot/firmware/gate-d-stock-6.12.img",
        "stagedInitramfs": "/boot/firmware/gate-d-stock-6.12-initramfs",
        "backupConfig": "/var/lib/rp1-gpclk-dkms/gate-d/boot/config.txt.original",
        "state": "/var/lib/rp1-gpclk-dkms/gate-d/boot/state.json",
    }
    operation_path = root / "operation.json"
    operation_path.write_text(json.dumps(operation))
    loaded = boot.load(operation_path)
    planned = boot.plan(loaded)
    assert planned["trybootMutation"] is False and planned["historicalArtifactMutation"] is False
    selected = boot.select(loaded, root)
    assert selected["status"] == "selected-reboot-required" and selected["liveOutput"] is False
    selected_config = (firmware / "config.txt").read_text()
    assert boot.MARKER_BEGIN in selected_config and "kernel=gate-d-stock-6.12.img" in selected_config
    assert (firmware / "tryboot.txt").read_bytes() == tryboot_bytes
    restored = boot.restore(loaded, root)
    assert restored["status"] == "restored-reboot-required"
    assert (firmware / "config.txt").read_bytes() == config_bytes
    assert (firmware / "tryboot.txt").read_bytes() == tryboot_bytes
    assert not (firmware / "gate-d-stock-6.12.img").exists()
    assert not (firmware / "gate-d-stock-6.12-initramfs").exists()

    # Recovery is idempotent after a partial stage: original config and
    # unrelated tryboot bytes remain exact, while a digest-bound staged file
    # is removed.
    partial = dict(operation)
    partial["operationId"] = "partial-stage"
    partial["stagedKernel"] = "/boot/firmware/gate-d-stock-partial.img"
    partial["stagedInitramfs"] = "/boot/firmware/gate-d-stock-partial-initramfs"
    partial["backupConfig"] = "/var/lib/rp1-gpclk-dkms/gate-d/boot/config.partial"
    partial["state"] = "/var/lib/rp1-gpclk-dkms/gate-d/boot/partial.json"
    partial_backup = root / partial["backupConfig"].lstrip("/")
    partial_backup.write_bytes(config_bytes)
    partial_kernel = root / partial["stagedKernel"].lstrip("/")
    partial_kernel.write_bytes(kernel_bytes)
    partial_state = {
        "schemaVersion": 1, "operationId": "partial-stage", "status": "staging-recovery-required",
        "checkpoint": "stage-kernel", "targetKernel": "6.12",
        "originalConfigSha256": sha(config_bytes), "backupConfigSha256": sha(config_bytes),
        "stagedKernelSha256": sha(kernel_bytes), "stagedInitramfsSha256": sha(initramfs_bytes),
        "trybootSha256": sha(tryboot_bytes), "liveOutput": False,
    }
    (root / partial["state"].lstrip("/")).write_text(json.dumps(partial_state))
    recovered = boot.restore(partial, root)
    assert recovered["status"] == "restored-reboot-required" and not partial_kernel.exists()
    assert (firmware / "tryboot.txt").read_bytes() == tryboot_bytes

    journal_only = dict(partial)
    journal_only["operationId"] = "journal-only"
    journal_only["backupConfig"] = "/var/lib/rp1-gpclk-dkms/gate-d/boot/config.journal-only"
    journal_only["state"] = "/var/lib/rp1-gpclk-dkms/gate-d/boot/journal-only.json"
    journal_only["stagedKernel"] = "/boot/firmware/gate-d-stock-journal-only.img"
    journal_only["stagedInitramfs"] = "/boot/firmware/gate-d-stock-journal-only-initramfs"
    journal_state = dict(partial_state, operationId="journal-only", checkpoint="journal-created")
    (root / journal_only["state"].lstrip("/")).write_text(json.dumps(journal_state))
    recovered = boot.restore(journal_only, root)
    assert recovered["status"] == "restored-reboot-required"

with tempfile.TemporaryDirectory() as temporary:
    root = pathlib.Path(temporary)
    firmware = root / "boot/firmware"
    evidence = root / "evidence"
    firmware.mkdir(parents=True)
    evidence.mkdir()
    values = {"config": b"normal\n", "tryboot": b"foreign\n", "kernel": b"k", "initramfs": b"i"}
    for name, data in (("config.txt", values["config"]), ("tryboot.txt", values["tryboot"])):
        (firmware / name).write_bytes(data)
    (root / "boot/kernel").write_bytes(values["kernel"])
    (root / "boot/initramfs").write_bytes(values["initramfs"])
    operation = {
        "schemaVersion": 1, "operationId": "tamper", "targetKernel": "prior",
        "sourceKernel": "/boot/kernel", "sourceKernelSha256": sha(values["kernel"]),
        "sourceInitramfs": "/boot/initramfs", "sourceInitramfsSha256": sha(values["initramfs"]),
        "config": "/boot/firmware/config.txt", "configSha256": sha(values["config"]),
        "tryboot": "/boot/firmware/tryboot.txt", "trybootSha256": sha(values["tryboot"]),
        "stagedKernel": "/boot/firmware/gate-d-stock-prior.img",
        "stagedInitramfs": "/boot/firmware/gate-d-stock-prior-initramfs",
        "backupConfig": "/evidence/config.backup", "state": "/evidence/state.json",
    }
    (firmware / "tryboot.txt").write_bytes(b"changed\n")
    try:
        boot.select(operation, root)
    except ValueError as error:
        assert "tryboot identity differs" in str(error)
    else:
        raise AssertionError("changed unrelated tryboot file was accepted")
    assert (firmware / "config.txt").read_bytes() == values["config"]

print("Gate D stock-kernel boot selector: PASS")
