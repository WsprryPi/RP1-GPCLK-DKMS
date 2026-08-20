#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Independently exercise the final unauthorized Phase 5.53 controls."""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import gate_d_attempts
import gate_d_bootstrap
import gate_d_instance
import gate_d_preroot
import gate_d_root
import gate_d_same_version
import gate_d_target_plan

TAG = "phase5.53-final-v1"
PRODUCT = "032a0ca214427ebb6115b933042e7135f03c2ed6ce4f5c399686b2cf61395a76"
QUALIFICATION = "916a5522e3998ae43f203c217fedce90ad8d4c2d52ae0bd4491407e3cf17211d"


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text())


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


route = load(f"release/gate-d-route-compatibility-decision-{TAG}.json")
plan = load(f"release/gate-d-target-operation-plan-{TAG}.json")
bootstrap = load(f"release/gate-d-qualification-bootstrap-plan-{TAG}.json")
instance = load(f"release/gate-d-execution-instance-{TAG}.json")
envelope = load(f"release/gate-d-pre-root-bootstrap-envelope-{TAG}.json")
same = load(f"release/gate-d-same-version-transition-{TAG}.json")
identity = load("docs/evidence/gate-d-phase5.53-final-qualification-install-identity.json")

assert route["candidate"]["archiveSha256"] == PRODUCT
assert envelope["releaseInputs"][0]["sha256"] == PRODUCT
roles = {item["role"]: item for item in envelope["releaseInputs"]}
assert roles["qualificationArchive"]["sha256"] == QUALIFICATION
assert identity["schemaVersion"] == 4 and envelope["schemaVersion"] == 7
assert identity["preRemovalLedgerSha256"] == envelope["priorTerminalState"]["sha256"]
assert envelope["priorTerminalState"]["status"] == "removed"
assert instance["authorization"]["approved"] is False
assert instance["authorization"]["targetExecutionApproved"] is False
assert instance["executionReady"] is False
assert same["authorization"] == {
    "approved": False, "targetExecutionApproved": False, "executionReady": False}
gate_d_same_version.validate(same)

for checkpoint in gate_d_same_version.CHECKPOINTS[1:]:
    state = dict(same["preState"])
    journal = {}
    def run(argv: list[str]) -> None:
        if argv == same["removeArgv"]:
            state.update(same["absentState"])
        elif argv == same["qualificationInstallArgv"]:
            state.update(same["qualifiedState"])
        elif argv in (same["qualificationRemoveArgv"], same["qualificationRecoveryArgv"]):
            state.update(same["absentState"])
        elif argv in (same["productRollbackArgv"], same["removeRecoveryArgv"]):
            state.update(same["preState"])
        else:
            raise AssertionError("unknown same-version command")
    try:
        gate_d_same_version.execute(
            same, run=run, probe=lambda: dict(state),
            record=lambda value: journal.update(value), stop_after=checkpoint)
    except InterruptedError:
        pass
    else:
        raise AssertionError("same-version interruption was not injected")
    recovered = gate_d_same_version.recover(
        same, journal, run=run, probe=lambda: dict(state),
        record=lambda value: journal.update(value))
    assert recovered["status"] == "recovered" and state == same["preState"]

attempt_dir = ROOT / f"release/gate-d-attempts-{TAG}"
index_path = attempt_dir / "index.json"
index = json.loads(index_path.read_text())
documents = []
for record in index["attempts"]:
    path = attempt_dir / record["file"]
    assert digest(path) == record["sha256"]
    document = json.loads(path.read_text())
    gate_d_attempts.validate_document(document)
    result = gate_d_attempts.execute_fake(document)
    assert result["status"] == "complete" and result["evidenceSealed"] is True
    documents.append(document)
assert len(documents) == index["attemptCount"] == 38

with tempfile.TemporaryDirectory() as temporary:
    frozen = pathlib.Path(temporary) / "root"
    frozen.mkdir(mode=0o700)
    marker = frozen / instance["qualificationRoot"]["identityFile"]
    marker.write_text(json.dumps(envelope["proposedRoot"]["marker"], sort_keys=True,
                                 separators=(",", ":")) + "\n")
    marker.chmod(0o400)
    assert digest(marker) == instance["qualificationRoot"]["identitySha256"]
    for item in envelope["transitionFiles"]:
        source = ROOT / item["destination"]
        assert source.is_file() and not source.is_symlink() and digest(source) == item["sha256"]
        target = frozen / item["destination"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
        target.chmod(int(item["mode"], 8))
    old = gate_d_root.validate
    gate_d_root.validate = lambda reference, verify=True: frozen
    try:
        assert gate_d_target_plan.validate(plan, verify_tools=False)["attemptCount"] == 38
        assert gate_d_bootstrap.validate(bootstrap)["outputDisabled"] is True
        validated = gate_d_instance.validate(instance)
        assert validated["executionReady"] is False
        assert gate_d_preroot.validate(envelope)["outputDisabled"] is True
    finally:
        gate_d_root.validate = old

print("Phase 5.53 final unauthorized control set: PASS")
