#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import pathlib
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]


def module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec and spec.loader
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


lifecycle = module("gate_d_lifecycle", "scripts/gate_d_lifecycle.py")
instance_tool = module("gate_d_instance", "scripts/gate_d_instance.py")
platform_tool = module("gate_d_platform", "scripts/gate_d_platform.py")
instance = json.loads((ROOT / "release/gate-d-execution-instance-v1.json").read_text())
result = instance_tool.validate(instance)
assert result["valid"] and not result["executionReady"]
assert result["inputsReady"] is False
assert len(result["blockedRows"]) == 3
assert len(result["deferredRows"]) == 5
assert result["environmentalCoverageComplete"] is False
assert {row["id"] for row in instance["rows"] if row["status"] == "ready"} == {
    "current-supported-kernel", "signing-not-enforced", "stale-manifest",
    "corrupted-archive-or-dtbo", "removal-inactive",
    "removal-open-or-active", "reinstall-after-removal",
}
assert set(result["deferredRows"]) == {
    "newer-unknown-kernel", "signing-enforced-enrolled-key",
    "deliberate-signature-rejection", "missing-headers",
    "overlay-or-resource-conflict",
}
try:
    instance_tool.validate(instance, require_ready=True)
except ValueError:
    pass
else:
    raise AssertionError("blocked execution instance accepted as ready")

bad = copy.deepcopy(instance)
bad["authorization"]["prohibitions"].remove("rf")
try:
    instance_tool.validate(bad)
except ValueError:
    pass
else:
    raise AssertionError("missing RF prohibition accepted")
bad = copy.deepcopy(instance)
bad["rows"][0]["routes"] = ["gpio17"]
try:
    instance_tool.validate(bad)
except ValueError:
    pass
else:
    raise AssertionError("arbitrary route accepted")
bad = copy.deepcopy(instance)
bad["rows"][0]["evidenceDirectory"] = bad["rows"][1]["evidenceDirectory"]
try:
    instance_tool.validate(bad)
except ValueError:
    pass
else:
    raise AssertionError("reused evidence directory accepted")
bad = copy.deepcopy(instance)
bad["executionReady"] = True
try:
    instance_tool.validate(bad)
except ValueError:
    pass
else:
    raise AssertionError("blocked instance marked ready")
bad = copy.deepcopy(instance)
bad["rows"][2]["status"] = "blocked-input-required"
try:
    instance_tool.validate(bad)
except ValueError:
    pass
else:
    raise AssertionError("deferred environmental row relabeled as executable")
bad = copy.deepcopy(instance)
bad["executionPolicy"]["matrixPolicySha256"] = "0" * 64
try:
    instance_tool.validate(bad)
except ValueError:
    pass
else:
    raise AssertionError("mismatched matrix-policy identity accepted")


def safety() -> dict:
    return {
        "liveOutput": False, "clockEnabled": False, "clockPrepared": False,
        "dmaActive": False, "gpioOutput": False, "transmitterActive": False,
        "sdrActive": False, "antennaConnected": False, "moduleLoaded": False,
        "platformBound": False, "endpointOpen": False, "ownerPresent": False,
        "workActive": False, "callbackPending": False, "cleanupLatched": False,
        "si5351Disconnected": True, "ownershipKnown": True, "routeSelectedInactive": True,
        "selectedPinSafe": True,
        "unselectedPinSafe": True, "unrelatedBytesPreserved": True,
    }


def ready_instance() -> dict:
    value = copy.deepcopy(instance)
    value["candidate"] = {
        "status": "frozen", "sourceCommit": "1" * 40, "release": "0.0.0-new",
        "archiveSha256": "2" * 64, "uapiSha256": "3" * 64,
        "manifestSha256": "4" * 64, "gpio4DtboSha256": "5" * 64,
        "gpio20DtboSha256": "6" * 64,
    }
    positive = ROOT / "tests/fixtures/gate-d-route-positive-decision.json"
    value["executionPolicy"]["routeDecision"] = "tests/fixtures/gate-d-route-positive-decision.json"
    value["executionPolicy"]["routeDecisionSha256"] = hashlib.sha256(positive.read_bytes()).hexdigest()
    for row in value["rows"]:
        if row["status"] != "deferred-environmental":
            row["status"] = "ready"
            row["systemId"] = "wspr5-stock"
            row["kernel"] = "6.18.34+rpt-rpi-2712"
            row["blockers"] = []
    value["executionReady"] = True
    value["inputsReady"] = True
    value["authorization"]["targetExecutionApproved"] = True
    value["authorization"]["approvalScope"] = "unit-test execution release"
    instance_tool.validate(value, require_ready=True)
    return value


def operation(name: str, *, op_id: str | None = None, owned=None) -> dict:
    predecessor = "0.0.0-old"
    successor = "0.0.0-new"
    if name in {"output-disabled-cycle", "uninstall-version", "remove-all-test-versions",
                "complete-removal", "repeated-removal", "reinstall-after-removal",
                "refuse-removal"}:
        predecessor = None
    snapshot = safety()
    if name == "refuse-removal":
        snapshot["endpointOpen"] = True
        if owned is None:
            owned = [{"path": "/retained", "kind": "file", "sha256": "0" * 64}]
    return {
        "schemaVersion": 1, "operationId": op_id or f"test-{name}", "operation": name,
        "matrixRow": "current-supported-kernel", "hostId": "wspr5-stock",
        "kernelRelease": "6.18.34+rpt-rpi-2712", "route": "gpio4",
        "deadlineSeconds": 30, "evidenceDirectory": f"gate-d/current-supported-kernel/{name}",
        "predecessorVersion": predecessor, "successorVersion": successor,
        "testVersions": ["0.0.0-new"], "ownedPaths": owned or [],
        "safety": snapshot,
        "expectedFinalState": ("predecessor-inactive" if name in {"rollback", "recover"} else
                               "package-absent" if name in {"uninstall-version", "remove-all-test-versions", "complete-removal", "repeated-removal", "reinstall-after-removal"} else
                               "installation-retained" if name == "refuse-removal" else
                               "successor-inactive"),
        "rollbackOnFailure": name in {"upgrade", "downgrade"},
        "priorOperationId": "failed-operation" if name == "recover" else None,
    }


awaiting_authorization = ready_instance()
awaiting_authorization["authorization"]["targetExecutionApproved"] = False
awaiting_authorization["authorization"]["approvalScope"] = "inputs complete; fresh execution release absent"
awaiting_authorization["executionReady"] = False
authorization_result = instance_tool.validate(awaiting_authorization)
assert authorization_result["inputsReady"] is True
assert authorization_result["executionReady"] is False
try:
    instance_tool.validate(awaiting_authorization, require_ready=True)
except ValueError:
    pass
else:
    raise AssertionError("input-ready instance executed without fresh target authority")


for name in lifecycle.OPERATIONS:
    spec = operation(name)
    lifecycle.validate_operation(spec)
    commands = lifecycle.operation_commands(spec)
    flat = " ".join(token for _, command in commands for token in command)
    assert "live_output=0" in flat or name in {"uninstall-version", "remove-all-test-versions", "complete-removal", "repeated-removal", "refuse-removal"}
    for prohibited in ("live_output=1", "dtoverlay", "/dev/mem", "reboot", "rpi-update"):
        assert prohibited not in flat
    if name in {"rollback", "recover"}:
        assert sum(command[0].endswith("gate-d-uapi-probe") for _, command in commands) == 2

for field, value in (("liveOutput", True), ("clockEnabled", True), ("dmaActive", True),
                     ("si5351Disconnected", False), ("ownershipKnown", False)):
    bad = operation("upgrade")
    bad["safety"][field] = value
    try:
        lifecycle.validate_operation(bad)
    except ValueError:
        pass
    else:
        raise AssertionError(f"unsafe snapshot accepted: {field}")

with tempfile.TemporaryDirectory() as temporary:
    root = pathlib.Path(temporary)
    owned = root / "usr/share/rp1-gpclk-dkms/owned.txt"
    owned.parent.mkdir(parents=True)
    owned.write_text("owned\n")
    owned_record = [{"path": "/usr/share/rp1-gpclk-dkms/owned.txt", "kind": "file",
                     "sha256": hashlib.sha256(owned.read_bytes()).hexdigest()}]
    commands: list[list[str]] = []

    def runner(command: list[str], deadline: int) -> str:
        assert deadline == 30
        commands.append(command)
        if command[:2] == ["cat", f"/sys/module/{lifecycle.MODULE}/parameters/live_output"]:
            return "N\n"
        if command[0].endswith("gate-d-uapi-probe"):
            return "live_eligible=0 released=1\n"
        if command[0].endswith("gate-d-platform"):
            return '{"unbindBind": true, "liveOutput": false}\n'
        return ""

    spec = operation("complete-removal", owned=owned_record)
    journal = root / "evidence/transaction.json"
    completed = lifecycle.execute(spec, ready_instance(), journal, root=root, runner=runner)
    assert completed["status"] == "complete" and completed["liveOutput"] is False
    assert not owned.exists()
    assert commands and all("live_output=1" not in item for command in commands for item in command)
    assert completed["commands"] and all(record["status"] == 0 for record in completed["commands"])
    assert all("startMonotonicNs" in record and "endMonotonicNs" in record and
               "stdoutTruncated" in record for record in completed["commands"])
    blocked_spec = operation("complete-removal")
    try:
        lifecycle.execute(blocked_spec, instance, root / "blocked-journal", root=root, runner=runner)
    except ValueError:
        pass
    else:
        raise AssertionError("blocked execution instance dispatched a lifecycle operation")
    try:
        lifecycle.execute(spec, ready_instance(), journal, root=root, runner=runner)
    except ValueError:
        pass
    else:
        raise AssertionError("immutable journal was reused")

with tempfile.TemporaryDirectory() as temporary:
    root = pathlib.Path(temporary)
    journal = root / "transaction.json"
    interrupted = operation("upgrade", op_id="recover-me")

    def runner(command: list[str], deadline: int) -> str:
        if command[0] == "cat":
            return "N\n"
        if command[0].endswith("gate-d-uapi-probe"):
            return "live_eligible=0 released=1\n"
        if command[0].endswith("gate-d-platform"):
            return '{"unbindBind": true, "liveOutput": false}\n'
        return ""

    try:
        lifecycle.execute(interrupted, ready_instance(), journal, root=root, runner=runner,
                          stop_after="dkms-build")
    except InterruptedError:
        failed = json.loads(journal.read_text())
        assert failed["status"] == "inactive-recovery-required"
        assert failed["checkpoint"] == "dkms-build" and failed["liveOutput"] is False
    else:
        raise AssertionError("checkpoint interruption did not stop")
    failed_bytes = journal.read_bytes()
    recovery = operation("recover", op_id="recovery-attempt")
    recovery["priorOperationId"] = "recover-me"
    recovery_journal = root / "recovery-transaction.json"
    recovered = lifecycle.execute(recovery, ready_instance(), recovery_journal, root=root,
                                  runner=runner, recover_from=journal)
    assert recovered["status"] == "complete" and recovered["recovers"]["checkpoint"] == "dkms-build"
    assert journal.read_bytes() == failed_bytes

with tempfile.TemporaryDirectory() as temporary:
    root = pathlib.Path(temporary)
    retained = root / "usr/share/rp1-gpclk-dkms/retained"
    retained.parent.mkdir(parents=True)
    retained.write_text("retained\n")
    retained_record = [{"path": "/usr/share/rp1-gpclk-dkms/retained", "kind": "file",
                        "sha256": hashlib.sha256(retained.read_bytes()).hexdigest()}]
    spec = operation("refuse-removal", owned=retained_record)

    def forbidden_runner(command: list[str], deadline: int) -> str:
        raise AssertionError(f"refusal dispatched a command: {command}")

    refused = lifecycle.execute(spec, ready_instance(), root / "refusal.json", root=root,
                                runner=forbidden_runner)
    assert refused["status"] == "complete" and retained.read_text() == "retained\n"

with tempfile.TemporaryDirectory() as temporary:
    root = pathlib.Path(temporary)
    spec = operation("upgrade", op_id="ordinary-failure")
    calls = []
    failed_once = False

    def rollback_runner(command: list[str], deadline: int) -> str:
        nonlocal_failed = None
        calls.append(command)
        if command[:2] == ["dkms", "build"] and command[command.index("-v") + 1] == "0.0.0-new":
            raise lifecycle.subprocess.CalledProcessError(2, command, output="build failed\n")
        if command[0] == "cat":
            return "N\n"
        if command[0].endswith("gate-d-uapi-probe"):
            return "live_eligible=0 released=1\n"
        if command[0].endswith("gate-d-platform"):
            return '{"unbindBind": true, "liveOutput": false}\n'
        return ""

    rollback_journal = root / "rollback.json"
    try:
        lifecycle.execute(spec, ready_instance(), rollback_journal, root=root,
                          runner=rollback_runner)
    except lifecycle.subprocess.CalledProcessError:
        rolled_back = json.loads(rollback_journal.read_text())
        assert rolled_back["status"] == "inactive-rolled-back"
        assert rolled_back["recoveryRequired"] is False
        assert rolled_back["rollback"]["status"] == "complete"
        assert any(command[:2] == ["dkms", "install"] and
                   command[command.index("-v") + 1] == "0.0.0-old" for command in calls)
    else:
        raise AssertionError("ordinary successor failure did not remain a failed operation")

with tempfile.TemporaryDirectory() as temporary:
    root = pathlib.Path(temporary)
    spec = operation("repeated-removal")
    calls = []

    def absent_runner(command: list[str], deadline: int) -> str:
        calls.append(command)
        if command[:2] in (["dkms", "uninstall"], ["dkms", "remove"]):
            raise lifecycle.subprocess.CalledProcessError(3, command)
        if command[:2] == ["dkms", "status"]:
            return ""
        raise AssertionError(command)

    result = lifecycle.execute(spec, ready_instance(), root / "journal", root=root,
                               runner=absent_runner)
    assert result["status"] == "complete"
    assert any(command[:2] == ["dkms", "status"] for command in calls)

with tempfile.TemporaryDirectory() as temporary:
    root = pathlib.Path(temporary)
    changed = root / "owned"
    changed.write_text("changed")
    spec = operation("complete-removal", owned=[{"path": "/owned", "kind": "file", "sha256": "0" * 64}])
    try:
        lifecycle.execute(spec, ready_instance(), root / "journal", root=root, runner=lambda command, deadline: "")
    except ValueError:
        assert changed.exists()
        assert json.loads((root / "journal").read_text())["status"] == "inactive-recovery-required"
    else:
        raise AssertionError("changed owned file was removed")

with tempfile.TemporaryDirectory() as temporary:
    root = pathlib.Path(temporary)
    spec = operation("complete-removal")
    original_monotonic = lifecycle.time.monotonic_ns
    ticks = iter((0, 31_000_000_000))
    lifecycle.time.monotonic_ns = lambda: next(ticks)
    dispatched = []
    try:
        try:
            lifecycle.execute(spec, ready_instance(), root / "deadline.json", root=root,
                              runner=lambda command, deadline: dispatched.append(command) or "")
        except TimeoutError:
            state = json.loads((root / "deadline.json").read_text())
            assert state["status"] == "inactive-recovery-required" and not dispatched
        else:
            raise AssertionError("exhausted total deadline dispatched a command")
    finally:
        lifecycle.time.monotonic_ns = original_monotonic

with tempfile.TemporaryDirectory() as temporary:
    base = pathlib.Path(temporary)
    driver = base / "driver"
    driver.mkdir()
    parameter = base / "live_output"
    parameter.write_text("N\n")
    endpoint = base / "rp1-gpclk"
    endpoint.write_text("")
    device = "1f00000000.gpclk"
    (driver / device).symlink_to("../../devices/platform/test")
    (driver / "bind").write_text("")
    (driver / "unbind").write_text("")
    old = platform_tool.DRIVER, platform_tool.PARAMETER, platform_tool.ENDPOINT
    platform_tool.DRIVER, platform_tool.PARAMETER, platform_tool.ENDPOINT = driver, parameter, endpoint

    def control(path: pathlib.Path, value: str) -> None:
        assert value == device
        if path.name == "unbind":
            (driver / device).unlink()
            endpoint.unlink()
        else:
            (driver / device).symlink_to("../../devices/platform/test")
            endpoint.write_text("")

    try:
        result = platform_tool.cycle(control, administrator_uid=0)
        assert result == {"device": device, "unbindBind": True, "liveOutput": False}
        parameter.write_text("Y\n")
        try:
            platform_tool.cycle(control, administrator_uid=0)
        except ValueError:
            pass
        else:
            raise AssertionError("platform cycle accepted enabled output")
    finally:
        platform_tool.DRIVER, platform_tool.PARAMETER, platform_tool.ENDPOINT = old

print("Gate D lifecycle and execution instance: PASS")
