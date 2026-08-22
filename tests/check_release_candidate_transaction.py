#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Exercise the exact route transaction executor with failure injection."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "transaction", ROOT / "scripts/release_candidate_transaction.py")
assert SPEC and SPEC.loader
tx = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tx)


def rejected(callable_) -> None:
    try:
        callable_()
    except (OSError, ValueError, RuntimeError):
        return
    raise AssertionError("unsafe transaction input accepted")


def place(root: Path) -> None:
    config = tx.rooted(root, tx.CONFIG)
    config.parent.mkdir(parents=True)
    config.write_bytes(b"base=1" + tx.LEGACY_BLOCK.encode())
    boot = tx.rooted(root, tx.BOOT_ID)
    boot.parent.mkdir(parents=True)
    boot.write_text("01234567-89ab-cdef-0123-456789abcdef\n")


def runner(calls: list[list[str]]):
    def run(argv: list[str]) -> str:
        calls.append(argv)
        if argv == ["/bin/hostname"]:
            return "wspr5\n"
        if argv == ["/usr/bin/uname", "-m"]:
            return "aarch64\n"
        if argv == ["/usr/bin/uname", "-r"]:
            return "6.18.34+rpt-rpi-2712\n"
        if argv == ["/usr/sbin/reboot"]:
            return ""
        raise AssertionError(argv)
    return run


def plan(operation: str) -> dict:
    return {
        "schemaVersion": 1, "kind": "rp1-gpclk-1.1.1-route-transaction",
        "operationId": f"wspr5-1-1-1-{operation}", "host": tx.HOST,
        "architecture": tx.ARCH, "kernel": tx.KERNEL, "firmware": tx.FIRMWARE,
        "baseDtbSha256": tx.BASE_DTB_SHA256,
        "kernelConfigSha256": tx.KERNEL_CONFIG_SHA256,
        "sourceCommit": "1" * 40,
        "package": f"{tx.PACKAGE}_{tx.DEBIAN_VERSION}_all.deb",
        "packageSha256": tx.PACKAGE_SHA256,
        "qualificationArchiveSha256": "2" * 64,
        "uapiSha256": tx.UAPI_SHA256,
        "gpio4DtboSha256": tx.GPIO4_DTBO_SHA256,
        "gpio20DtboSha256": tx.GPIO20_DTBO_SHA256,
        "compatibilitySha256": "3" * 64,
        "productInventorySha256": "4" * 64,
        "predecessorVersion": tx.PREDECESSOR_VERSION,
        "predecessorPackage": tx.PREDECESSOR_PACKAGE,
        "predecessorPackageSha256": tx.PREDECESSOR_PACKAGE_SHA256,
        "predecessorConfigSha256": tx.PREDECESSOR_CONFIG_SHA256,
        "signingPolicy": "CONFIG_MODULE_SIG=n; unsigned candidate",
        "physicalTopology": "fresh-operator-confirmation-required",
        "servicePolicy": {"wsprrypi.service": "inactive",
                          "soapyremote-server.service": "inactive"},
    }


with tempfile.TemporaryDirectory() as temporary:
    root = Path(temporary)
    place(root)
    calls: list[list[str]] = []
    run = runner(calls)
    value = plan("deactivate-predecessor")
    value["planSha256"] = tx.digest_bytes(tx.canonical(value))
    plan_path = root / "plan.json"
    plan_path.write_text(json.dumps(value))
    loaded = tx.load_plan(plan_path)
    assert tx.preflight(loaded, root, run)["route"] == "legacy-gpio4"

    original_geteuid = tx.os.geteuid
    tx.os.geteuid = lambda: 0
    try:
        state = tx.mutate_config(loaded, root, "deactivate-and-reboot", None, True, run)
        assert state["status"] == "awaiting-reboot"
        assert tx.parse_config(tx.rooted(root, tx.CONFIG).read_bytes()) is None
        assert calls[-1] == ["/usr/sbin/reboot"]
        journal = tx.journal_path(root, loaded["operationId"])
        rejected(lambda: tx.mutate_config(loaded, root, "again", None, True, run))
        rejected(lambda: tx.reconcile(loaded, root, journal, None, run))
        tx.rooted(root, tx.BOOT_ID).write_text("11111111-2222-3333-4444-555555555555\n")
        assert tx.reconcile(loaded, root, journal, None, run)["status"] == "complete"

        gpio4 = plan("select-gpio4")
        gpio4["planSha256"] = tx.digest_bytes(tx.canonical(gpio4))
        state = tx.mutate_config(gpio4, root, "apply-and-reboot", "gpio4", True, run)
        assert tx.parse_config(tx.rooted(root, tx.CONFIG).read_bytes()) == "gpio4"
        gpio4_journal = tx.journal_path(root, gpio4["operationId"])
        before_rollback = tx.rooted(root, tx.CONFIG).read_bytes()
        tx.rooted(root, tx.CONFIG).write_bytes(before_rollback + b"foreign\n")
        rejected(lambda: tx.rollback(gpio4, root, gpio4_journal, True, run))
        tx.rooted(root, tx.CONFIG).write_bytes(before_rollback)
        assert tx.rollback(gpio4, root, gpio4_journal, True, run)["status"] == "rollback-awaiting-reboot"
        tx.rooted(root, tx.BOOT_ID).write_text("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee\n")
        assert tx.reconcile(gpio4, root, gpio4_journal, None, run)["checkpoint"] == "rollback-reconciled"
    finally:
        tx.os.geteuid = original_geteuid

    failure_root = root / "failure-root"
    place(failure_root)
    failure = plan("write-failure")
    failure["planSha256"] = tx.digest_bytes(tx.canonical(failure))
    original_atomic = tx.atomic_write
    original_geteuid = tx.os.geteuid
    tx.os.geteuid = lambda: 0
    tx.atomic_write = lambda path, payload, mode: (
        (_ for _ in ()).throw(OSError("injected config write failure"))
        if path == tx.rooted(failure_root, tx.CONFIG)
        else original_atomic(path, payload, mode))
    try:
        rejected(lambda: tx.mutate_config(
            failure, failure_root, "deactivate-and-reboot", None, True, run))
    finally:
        tx.atomic_write = original_atomic
    failure_journal = tx.journal_path(failure_root, failure["operationId"])
    assert json.loads(failure_journal.read_text())["status"] == "recovery-required"
    try:
        assert tx.rollback(failure, failure_root, failure_journal, True, run)["checkpoint"] == "rollback-no-change"
    finally:
        tx.os.geteuid = original_geteuid

    for mutation in (
        lambda v: v.update(host="other"),
        lambda v: v.update(kernel="unknown"),
        lambda v: v.update(packageSha256="0" * 64),
        lambda v: v.update(physicalTopology="assumed"),
        lambda v: v.update(planSha256="0" * 64),
    ):
        bad = copy.deepcopy(value)
        mutation(bad)
        bad_path = root / "bad.json"
        bad_path.write_text(json.dumps(bad))
        rejected(lambda: tx.load_plan(bad_path))

for payload in (
    f"{tx.BEGIN}\ndtoverlay=rp1-gpclk-gpio4\n",
    "dtoverlay=rp1-gpclk-gpio4\ndtoverlay=rp1-gpclk-gpio20\n",
    "dtoverlay=rp1-gpclk-gpio20\n",
    f"{tx.BEGIN}\ndtoverlay=rp1-gpclk-gpio4\n{tx.END}\ndtoverlay=rp1-gpclk-gpio20\n",
):
    rejected(lambda payload=payload: tx.parse_config(payload.encode()))

source = (ROOT / "scripts/release_candidate_transaction.py").read_text()
for prohibited in ("live_output=1", "dtoverlay -", "/dev/mem", "open(/dev/rp1-gpclk"):
    assert prohibited not in source
for required in ("os.fsync", "os.replace", "O_DIRECTORY", "planSha256",
                 "operation journal already exists", "rollback refuses changed"):
    assert required in source

print("Release candidate owned route transaction: PASS")
