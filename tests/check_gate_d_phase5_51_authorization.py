#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the exact Phase 5.51 authorized control state."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


instance_path = ROOT / "release/gate-d-execution-instance-phase5.51-v1.json"
envelope_path = ROOT / "release/gate-d-pre-root-bootstrap-envelope-phase5.51-v1.json"
index_path = ROOT / "release/gate-d-attempts-phase5.51-v1/index.json"
attestation_path = ROOT / "docs/evidence/gate-d-phase5.51-authorization-attestation.json"
prompt = (ROOT / "docs/contracts/gate-d-phase5.51-authorized-execution-prompt.md").read_text()

instance = json.loads(instance_path.read_text())
attestation = json.loads(attestation_path.read_text())
expected_instance = "3e3dadb4a553b2e9f083e05301a711b28d3b1e287082080d3f5437109607c532"
expected_envelope = "1acccb9e8c0e8aa9bd215e088bcb761ccaf449f15208fbb23000c0c6ac4271f6"
expected_index = "a1d547226090dbcb58375774983ebe7a0fa3cd05e30963b58d7dc2e5524f2960"

assert sha256(instance_path) == expected_instance
assert sha256(envelope_path) == expected_envelope
assert sha256(index_path) == expected_index
assert instance["authorization"]["approved"] is True
assert instance["authorization"]["targetExecutionApproved"] is True
assert instance["executionReady"] is True
assert "291be1d75a583b314173d54a4401a7ff559ae421" in instance["authorization"]["approvalScope"]
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
print("Phase 5.51 authorization state: PASS")
