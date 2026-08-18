#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Independently validate the complete Phase 5.53 Gate D control set."""
from __future__ import annotations

import copy
import hashlib
import importlib.machinery
import importlib.util
import json
import os
import pathlib
import shutil
import tempfile
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import gate_d_attempts
import gate_d_bootstrap
import gate_d_instance
import gate_d_preroot
import gate_d_root
import gate_d_service_contract
import gate_d_target_plan


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text())


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frozen_payload(relative: str, expected: str) -> bytes:
    path = ROOT / relative
    if path.is_file() and sha(path) == expected:
        return path.read_bytes()
    payload = subprocess.check_output([
        "git", "show", f"834d05c5c5da0c383c4a229eaeff9dae07a4359b:{relative}"
    ], cwd=ROOT)
    assert hashlib.sha256(payload).hexdigest() == expected
    return payload


def runtime_paths(value: object) -> set[str]:
    if isinstance(value, dict):
        return set().union(*(runtime_paths(item) for item in value.values()))
    if isinstance(value, list):
        return set().union(*(runtime_paths(item) for item in value))
    if isinstance(value, str) and value.startswith("/var/lib/rp1-gpclk-dkms/gate-d/"):
        return {value}
    return set()


snapshot_path = ROOT / "docs/evidence/gate-d-live-target-snapshot-wspr5-phase5.53-v1.json"
snapshot = load("docs/evidence/gate-d-live-target-snapshot-wspr5-phase5.53-v1.json")
build = load("release/gate-c-representative-build-manifest-phase5.53-v1.json")
route = load("release/gate-d-route-compatibility-decision-phase5.53-v1.json")
plan = load("release/gate-d-target-operation-plan-phase5.53-v1.json")
bootstrap = load("release/gate-d-qualification-bootstrap-plan-phase5.53-v1.json")
instance = load("release/gate-d-execution-instance-phase5.53-v1.json")
envelope = load("release/gate-d-pre-root-bootstrap-envelope-phase5.53-v1.json")
identity = load("docs/evidence/gate-d-phase5.53-qualification-install-identity.json")
inventory = load("docs/evidence/gate-d-phase5.53-predecessor-package-inventory.json")
index = load("release/gate-d-attempts-phase5.53-v1/index.json")
construction = load("docs/evidence/gate-d-phase5.53-control-set-construction.json")

assert sha(snapshot_path) == "df8e80bc4b3382d9213d52cbc273b398e85124a2d2f58169c3a6f6aa339dbcf7"
assert route["candidate"]["sourceCommit"] == build["candidate"]["sourceCommit"] == \
    "1884c0f1c53c661495576bf10ce08d8bf7a90bc3"
assert route["candidate"]["archiveSha256"] == build["candidate"]["productArchiveSha256"] == \
    "ae6df3a66a9a26a6fb8474e5896c9053b9f69580d8c45383a5556fc397ebb549"
assert route["evidence"]["moduleSha256"] == build["result"]["moduleSha256"]
assert snapshot["kernel"]["release"] == build["target"]["kernelRelease"]
assert snapshot["kernel"]["configSha256"] == build["target"]["kernelConfigSha256"]
assert snapshot["kernel"]["moduleSymversSha256"] == build["target"]["moduleSymversSha256"]
assert snapshot["administratorLedger"]["release"] == "0.0.0-phase5.52"
assert snapshot["administratorLedger"]["sha256"] == \
    "0261c25f785458a0ee3cd270e4a7afcb606f5a86fdb99fc019aae231388c78f1"
assert snapshot["terminalRecovery"]["sha256"] == \
    "fbc9657f9d3f825a8893a8449f112b4f25b0029c27f411d2bbc64db383ca6f98"
assert envelope["liveTargetSnapshotSha256"] == sha(snapshot_path)
assert envelope["predecessorPackagePaths"] == inventory["paths"] == snapshot["packagePaths"]
assert envelope["predecessorPackagePathsSha256"] == snapshot["packagePathsSha256"]
assert envelope["priorTerminalState"]["sha256"] == snapshot["administratorLedger"]["sha256"]
assert identity["packageTransitions"] and len(identity["packageTransitions"]) == 28
assert instance["schemaVersion"] == 6
assert instance["executionPolicy"]["attemptPathNamespace"] == "phase5.53-1884c0f1c53c"
assert instance["executionPolicy"]["attemptSchemaVersion"] == 2
assert instance["authorization"]["approved"] is True
assert instance["authorization"]["targetExecutionApproved"] is True
assert instance["inputsReady"] is True and instance["executionReady"] is True
assert envelope["schemaVersion"] == 6
roles = {item["role"]: item for item in envelope["releaseInputs"]}
assert set(roles) == {"archive", "qualificationArchive", "gpio4Dtbo", "gpio20Dtbo",
                      "compatibilityManifest", "provenance", "releaseMetadata", "checksums"}
assert roles["qualificationArchive"]["sha256"] == \
    "d931912d6ccc381b10a2a13d7f3a9122b0f748490ec8eefe0f86a28cb352c8d0"
release_directory = os.environ.get("PHASE5_53_RELEASE_DIRECTORY")
if release_directory:
    with tempfile.TemporaryDirectory() as temporary:
        prefix = pathlib.Path(temporary)
        for item in envelope["releaseInputs"]:
            source = pathlib.Path(release_directory) / pathlib.PurePosixPath(item["path"]).name
            assert source.is_file() and not source.is_symlink() and sha(source) == item["sha256"]
            destination = prefix / item["path"].lstrip("/")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
        gate_d_preroot.validate_release_inputs(envelope, prefix=prefix)
assert sum(row["status"] == "ready" for row in instance["rows"]) == 10
assert sum(row["status"] == "deferred-environmental" for row in instance["rows"]) == 5
assert construction["controlSet"]["treeSha256"] == \
    "f5c9012d0383ad771a184f31fccc0ea83ac41bd2c52a3715a6c6273747d6879c"
assert construction["authority"]["approved"] is True
assert construction["authority"]["targetExecutionApproved"] is True
assert construction["authority"]["executionReady"] is True
assert construction["disposition"] == \
    "authorized-offline-controls-committed; target staging remains separately unauthorized"

with tempfile.TemporaryDirectory() as temporary:
    frozen_root = pathlib.Path(temporary) / "qualification"
    frozen_root.mkdir(mode=0o700)
    marker = frozen_root / instance["qualificationRoot"]["identityFile"]
    marker.write_text(json.dumps(envelope["proposedRoot"]["marker"], sort_keys=True,
                                 separators=(",", ":")) + "\n")
    marker.chmod(0o400)
    assert sha(marker) == instance["qualificationRoot"]["identitySha256"]
    for item in envelope["transitionFiles"]:
        target = frozen_root / item["destination"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(frozen_payload(item["destination"], item["sha256"]))
    transition_destinations = {
        item["destination"]: item["sha256"] for item in envelope["transitionFiles"]}
    matrix_relative = instance["executionPolicy"]["matrixPolicy"]
    assert transition_destinations[matrix_relative] == \
        instance["executionPolicy"]["matrixPolicySha256"]
    for module_identity in plan["pythonModules"].values():
        assert transition_destinations[module_identity["sourcePath"]] == \
            module_identity["sourceSha256"]
    for executor in index["executors"].values():
        assert transition_destinations[executor["path"]] == executor["sha256"]
    expected_inputs = {
        (item["sourcePath"], item["sha256"]) for item in envelope["transitionFiles"]}
    actual_inputs = {(item["path"], item["sha256"]) for item in envelope["inputFiles"]}
    assert expected_inputs <= actual_inputs
    old_root = gate_d_root.validate
    gate_d_root.validate = lambda reference, verify=True: frozen_root
    try:
        assert gate_d_target_plan.validate(plan, verify_tools=False)["attemptCount"] == 38
        assert gate_d_bootstrap.validate(bootstrap)["outputDisabled"] is True
        assert gate_d_preroot.validate(envelope)["outputDisabled"] is True
        result = gate_d_instance.validate(instance)
        assert result["inputsReady"] is True and result["executionReady"] is True
    finally:
        gate_d_root.validate = old_root

    # Exercise the permanent executor from the exact frozen qualification-root
    # bytes against an installed-path tree populated from those same bytes.
    rehearsal_root = frozen_root.resolve()
    rehearsal_reference = copy.deepcopy(instance["qualificationRoot"])
    rehearsal_reference["path"] = str(rehearsal_root)
    rehearsal_reference["ownerUid"] = os.getuid()
    rehearsal_marker = copy.deepcopy(envelope["proposedRoot"]["marker"])
    rehearsal_marker["rootPath"] = str(rehearsal_root)
    marker_path = rehearsal_root / rehearsal_reference["identityFile"]
    marker_path.chmod(0o600)
    marker_path.write_text(json.dumps(rehearsal_marker, sort_keys=True, separators=(",", ":")) + "\n")
    marker_path.chmod(0o400); rehearsal_reference["identitySha256"] = sha(marker_path)
    rehearsal_plan = copy.deepcopy(plan); rehearsal_plan["qualificationRoot"] = rehearsal_reference
    rehearsal_plan_path = rehearsal_root / instance["executionPolicy"]["targetPlan"]
    rehearsal_plan_path.write_text(json.dumps(rehearsal_plan, indent=2, sort_keys=True) + "\n")
    rehearsal_instance = copy.deepcopy(instance); rehearsal_instance["qualificationRoot"] = rehearsal_reference
    rehearsal_instance["executionPolicy"]["targetPlanSha256"] = sha(rehearsal_plan_path)
    rehearsal_instance_path = rehearsal_root / "release/gate-d-execution-instance-phase5.53-v1.json"
    rehearsal_instance_path.write_text(json.dumps(rehearsal_instance, indent=2, sort_keys=True) + "\n")
    installed_root = pathlib.Path(temporary) / "installed"
    for module_identity in plan["pythonModules"].values():
        source = frozen_root / module_identity["sourcePath"]
        destination = installed_root / module_identity["installedPath"].lstrip("/")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination); destination.chmod(0o644)
    executor_identity = plan["tooling"]["permanentExecutor"]
    installed_executor = installed_root / executor_identity["installedPath"].lstrip("/")
    shutil.copy2(frozen_root / executor_identity["sourcePath"], installed_executor)
    installed_executor.chmod(0o755)
    loader = importlib.machinery.SourceFileLoader("phase551_frozen_executor", str(installed_executor))
    spec = importlib.util.spec_from_loader(loader.name, loader); assert spec and spec.loader
    frozen_executor = importlib.util.module_from_spec(spec); sys.modules[spec.name] = frozen_executor
    spec.loader.exec_module(frozen_executor)
    loaded, loaded_root = frozen_executor.bootstrap_root_validator(
        rehearsal_instance_path,
        installed_root=installed_root,
        current_executor_override=pathlib.Path(executor_identity["installedPath"]))
    assert loaded == rehearsal_instance and loaded_root == rehearsal_root

attempt_dir = ROOT / "release/gate-d-attempts-phase5.53-v1"
assert index["attemptCount"] == len(index["attempts"]) == 38
assert {path.name for path in attempt_dir.iterdir()} == \
    {"index.json", *(record["file"] for record in index["attempts"])}
assert {path.name for path in (ROOT / "release").glob("gate-d-*-phase5.53-v1.json")} == {
    "gate-d-execution-instance-phase5.53-v1.json",
    "gate-d-pre-root-bootstrap-envelope-phase5.53-v1.json",
    "gate-d-qualification-bootstrap-plan-phase5.53-v1.json",
    "gate-d-route-compatibility-decision-phase5.53-v1.json",
    "gate-d-target-operation-plan-phase5.53-v1.json",
}
documents = []
all_paths: set[str] = set()
for record in index["attempts"]:
    path = attempt_dir / record["file"]
    assert sha(path) == record["sha256"]
    document = json.loads(path.read_text())
    gate_d_attempts.validate_document(document)
    assert document["schemaVersion"] == 2
    fake = gate_d_attempts.execute_fake(document)
    assert fake["status"] == "complete" and fake["evidenceSealed"] is True
    assert fake["liveOutput"] is False and fake["servicesRestored"] is True
    namespace = "/gate-d/runs/phase5.53-1884c0f1c53c/"
    paths = runtime_paths(document)
    assert all(namespace in value for value in paths)
    assert not all_paths.intersection(paths)
    all_paths.update(paths)
    documents.append(document)
assert documents == gate_d_attempts.generate(instance, plan, schema_version=2)
assert gate_d_service_contract.validate(snapshot, documents) == {
    "attemptCount": 38, "readOnly": True, "serviceCount": 4, "valid": True}
historical_paths: set[str] = set()
for phase in ("phase5.42", "phase5.43", "phase5.45", "phase5.46", "phase5.47", "phase5.48", "phase5.50", "phase5.51", "phase5.52"):
    directory = ROOT / f"release/gate-d-attempts-{phase}-v1"
    historical_index = json.loads((directory / "index.json").read_text())
    for record in historical_index["attempts"]:
        historical_paths.update(runtime_paths(json.loads((directory / record["file"]).read_text())))
assert not all_paths.intersection(historical_paths)
for item in envelope["transitionFiles"]:
    assert hashlib.sha256(frozen_payload(
        item["destination"], item["sha256"])).hexdigest() == item["sha256"]

subprocess.run([sys.executable, str(ROOT / "scripts/gate_d_live_snapshot_validate.py"),
                str(snapshot_path)], check=True)
subprocess.run([sys.executable, str(ROOT / "scripts/generate_phase5_53_control_set.py"),
                "--check"], check=True)
if not release_directory:
    print("Phase 5.53 exact successor release-input validation: SKIP (directory not supplied)")
print("Gate D Phase 5.53 offline control set: PASS")
