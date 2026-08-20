#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the exact Phase 5.50 authorized control state."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


instance_path = ROOT / "release/gate-d-execution-instance-phase5.50-v1.json"
envelope_path = ROOT / "release/gate-d-pre-root-bootstrap-envelope-phase5.50-v1.json"
index_path = ROOT / "release/gate-d-attempts-phase5.50-v1/index.json"
attestation_path = ROOT / "docs/evidence/gate-d-phase5.50-authorization-attestation.json"
prompt = (ROOT / "docs/contracts/gate-d-phase5.50-authorized-execution-prompt.md").read_text()

instance = json.loads(instance_path.read_text())
attestation = json.loads(attestation_path.read_text())
expected_instance = "90291e87686ef9771ff7ced3390465852371fdcc19775915ec90436063e65ac8"
expected_envelope = "f5b10feaf56524e8251386b3e6c65f13bb2616cc43e3b4a4ec08e9cc42b7e435"
expected_index = "44c7bdb65e71970f1f15ef2c9d36bb6b1172ddb33350e19c0a2e3874ea3dc66f"

assert sha256(instance_path) == expected_instance
assert sha256(envelope_path) == expected_envelope
assert sha256(index_path) == expected_index
assert instance["authorization"]["approved"] is True
assert instance["authorization"]["targetExecutionApproved"] is True
assert instance["executionReady"] is True
assert "579910954a9f495e877cdc2c74b752f9e7005937" in instance["authorization"]["approvalScope"]
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
print("Phase 5.50 authorization state: PASS")
