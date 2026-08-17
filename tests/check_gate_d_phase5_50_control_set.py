#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Independently validate the complete Phase 5.50 Gate D control set."""
from __future__ import annotations

import hashlib
import json
import pathlib
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
        "git", "show", f"c24160517b10900bf61243d4988f38247eeed58e:{relative}"
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


snapshot_path = ROOT / "docs/evidence/gate-d-live-target-snapshot-wspr5-phase5.50-v1.json"
snapshot = load("docs/evidence/gate-d-live-target-snapshot-wspr5-phase5.50-v1.json")
build = load("release/gate-c-representative-build-manifest-phase5.50-v1.json")
route = load("release/gate-d-route-compatibility-decision-phase5.50-v1.json")
plan = load("release/gate-d-target-operation-plan-phase5.50-v1.json")
bootstrap = load("release/gate-d-qualification-bootstrap-plan-phase5.50-v1.json")
instance = load("release/gate-d-execution-instance-phase5.50-v1.json")
envelope = load("release/gate-d-pre-root-bootstrap-envelope-phase5.50-v1.json")
identity = load("docs/evidence/gate-d-phase5.50-qualification-install-identity.json")
inventory = load("docs/evidence/gate-d-phase5.50-predecessor-package-inventory.json")
index = load("release/gate-d-attempts-phase5.50-v1/index.json")

assert sha(snapshot_path) == "3db85e0ada2427c997cdca878d0f2d53fc0c61d5aab68761e65a2a6cf349a6d5"
assert route["candidate"]["sourceCommit"] == build["candidate"]["sourceCommit"] == \
    "c24160517b10900bf61243d4988f38247eeed58e"
assert route["candidate"]["archiveSha256"] == build["candidate"]["archiveSha256"]
assert route["evidence"]["moduleSha256"] == build["result"]["moduleSha256"]
assert envelope["liveTargetSnapshotSha256"] == sha(snapshot_path)
assert envelope["predecessorPackagePaths"] == inventory["paths"] == snapshot["packagePaths"]
assert envelope["predecessorPackagePathsSha256"] == snapshot["packagePathsSha256"]
assert envelope["priorTerminalState"]["sha256"] == snapshot["administratorLedger"]["sha256"]
assert identity["packageTransitions"] and len(identity["packageTransitions"]) == 28
assert instance["schemaVersion"] == 6
assert instance["executionPolicy"]["attemptPathNamespace"] == "phase5.50-c24160517b10"
assert instance["executionPolicy"]["attemptSchemaVersion"] == 2
assert instance["authorization"]["approved"] is True
assert instance["authorization"]["targetExecutionApproved"] is True
assert instance["inputsReady"] is True and instance["executionReady"] is True
assert sum(row["status"] == "ready" for row in instance["rows"]) == 10
assert sum(row["status"] == "deferred-environmental" for row in instance["rows"]) == 5

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

attempt_dir = ROOT / "release/gate-d-attempts-phase5.50-v1"
assert index["attemptCount"] == len(index["attempts"]) == 38
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
    namespace = "/gate-d/runs/phase5.50-c24160517b10/"
    paths = runtime_paths(document)
    assert all(namespace in value for value in paths)
    assert not all_paths.intersection(paths)
    all_paths.update(paths)
    documents.append(document)
assert documents == gate_d_attempts.generate(instance, plan, schema_version=2)
assert gate_d_service_contract.validate(snapshot, documents) == {
    "attemptCount": 38, "readOnly": True, "serviceCount": 4, "valid": True}
historical_paths: set[str] = set()
for phase in ("phase5.42", "phase5.43", "phase5.45", "phase5.46", "phase5.47", "phase5.48"):
    directory = ROOT / f"release/gate-d-attempts-{phase}-v1"
    historical_index = json.loads((directory / "index.json").read_text())
    for record in historical_index["attempts"]:
        historical_paths.update(runtime_paths(json.loads((directory / record["file"]).read_text())))
assert not all_paths.intersection(historical_paths)
for item in envelope["transitionFiles"]:
    assert hashlib.sha256(frozen_payload(
        item["destination"], item["sha256"])).hexdigest() == item["sha256"]

subprocess.run([sys.executable, str(ROOT / "scripts/gate_d_live_snapshot_validate.py"),
                str(snapshot_path), "--envelope",
                str(ROOT / "release/gate-d-pre-root-bootstrap-envelope-phase5.50-v1.json"),
                "--inventory", str(ROOT / "docs/evidence/gate-d-phase5.50-predecessor-package-inventory.json"),
                "--route", str(ROOT / "release/gate-d-route-compatibility-decision-phase5.50-v1.json"),
                "--build", str(ROOT / "release/gate-c-representative-build-manifest-phase5.50-v1.json")],
               check=True)
subprocess.run([sys.executable, str(ROOT / "scripts/generate_phase5_50_control_set.py"),
                "--check"], check=True)
print("Gate D Phase 5.50 offline control set: PASS")
