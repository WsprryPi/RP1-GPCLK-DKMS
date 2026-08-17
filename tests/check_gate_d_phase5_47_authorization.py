#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the exact Phase 5.47 authorized control state."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


instance_path = ROOT / "release/gate-d-execution-instance-phase5.47-v1.json"
envelope_path = ROOT / "release/gate-d-pre-root-bootstrap-envelope-phase5.47-v1.json"
index_path = ROOT / "release/gate-d-attempts-phase5.47-v1/index.json"
attestation_path = ROOT / "docs/evidence/gate-d-phase5.47-authorization-attestation.json"
prompt = (ROOT / "docs/contracts/gate-d-phase5.47-authorized-execution-prompt.md").read_text()

instance = json.loads(instance_path.read_text())
attestation = json.loads(attestation_path.read_text())
expected_instance = "9e0a1c74f2810670b8fb212b694dca2f9cc36f85259000afcf8d2b852c09fee8"
expected_envelope = "bf81b5e9085f40722ee45a6ced3a12e2052f8a238a8441b52eeb520dba409e5f"
expected_index = "dc68030fa86386659f92a93f56a96d05979af2c541d1be7bfc3e3b33c2e4651d"

assert sha256(instance_path) == expected_instance
assert sha256(envelope_path) == expected_envelope
assert sha256(index_path) == expected_index
assert instance["authorization"]["targetExecutionApproved"] is True
assert instance["executionReady"] is True
assert "f307eac68aeee19abd096a7e3ea975c58e9ad457" in instance["authorization"]["approvalScope"]
assert attestation["authorizedControls"]["executionInstanceSha256"] == expected_instance
assert attestation["authorizedControls"]["envelopeSha256"] == expected_envelope
assert attestation["authorizedControls"]["attemptIndexSha256"] == expected_index
assert attestation["result"] == {
    "authorizationRecorded": True,
    "targetStaged": False,
    "lifecycleExecuted": False,
    "outputDisabled": True,
}
for identity in (expected_instance, expected_envelope, expected_index):
    assert identity in prompt
print("Phase 5.47 authorization state: PASS")
