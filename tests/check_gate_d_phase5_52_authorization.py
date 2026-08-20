#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the exact Phase 5.52 authorized control state."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


instance_path = ROOT / "release/gate-d-execution-instance-phase5.52-v1.json"
envelope_path = ROOT / "release/gate-d-pre-root-bootstrap-envelope-phase5.52-v1.json"
index_path = ROOT / "release/gate-d-attempts-phase5.52-v1/index.json"
attestation_path = ROOT / "docs/evidence/gate-d-phase5.52-authorization-attestation.json"
prompt = (ROOT / "docs/contracts/gate-d-phase5.52-authorized-execution-prompt.md").read_text()

instance = json.loads(instance_path.read_text())
attestation = json.loads(attestation_path.read_text())
expected_instance = "8f53fa6c41153965d49f11a4da7b139c3aa0e17cd1e9a2a77f8157c21cf43bd2"
expected_envelope = "8ae40ffc6f85ec0e34119aaa1cb08a221e9d94b3f08993caa33c4bd394a8ecf8"
expected_index = "744427cc21988c73558dd7a2c89fdbf97915288bf539941e67a8cf080c0e90d8"

assert sha256(instance_path) == expected_instance
assert sha256(envelope_path) == expected_envelope
assert sha256(index_path) == expected_index
assert instance["authorization"]["approved"] is True
assert instance["authorization"]["targetExecutionApproved"] is True
assert instance["executionReady"] is True
assert "eb22b2f3d6e4bdc266bd160942e91771ed689ddc" in \
    instance["authorization"]["approvalScope"]
assert attestation["authorizedControls"]["executionInstanceSha256"] == expected_instance
assert attestation["authorizedControls"]["envelopeSha256"] == expected_envelope
assert attestation["authorizedControls"]["attemptIndexSha256"] == expected_index
assert attestation["authorizedControls"]["attemptSchemaVersion"] == 2
assert attestation["result"] == {
    "authorizationRecorded": True,
    "targetStaged": False,
    "lifecycleExecuted": False,
    "outputDisabled": True,
}
for identity in (expected_instance, expected_envelope, expected_index):
    assert identity in prompt
print("Phase 5.52 authorization state: PASS")
