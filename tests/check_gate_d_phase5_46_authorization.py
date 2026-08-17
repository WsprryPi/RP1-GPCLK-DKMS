#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the exact Phase 5.46 authorized control state."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


instance_path = ROOT / "release/gate-d-execution-instance-phase5.46-v1.json"
envelope_path = ROOT / "release/gate-d-pre-root-bootstrap-envelope-phase5.46-v1.json"
index_path = ROOT / "release/gate-d-attempts-phase5.46-v1/index.json"
attestation_path = ROOT / "docs/evidence/gate-d-phase5.46-authorization-attestation.json"
prompt = (ROOT / "docs/contracts/gate-d-phase5.46-authorized-execution-prompt.md").read_text()

instance = json.loads(instance_path.read_text())
attestation = json.loads(attestation_path.read_text())
expected_instance = "cece70ab06d8a3b6de0240851b1ec2d7612e2d699f0f6c97de57a42da0687f2e"
expected_envelope = "f71efda6d310137d4372c98a8c90d2104ff57fe744159dd84c6a7b06844d3dd5"
expected_index = "e1858c68af8362a3c9ac969b5335317617e8e67491ddc916c3190c2eb6a8243d"

assert sha256(instance_path) == expected_instance
assert sha256(envelope_path) == expected_envelope
assert sha256(index_path) == expected_index
assert instance["authorization"]["targetExecutionApproved"] is True
assert instance["executionReady"] is True
assert "b65410f9301428878decfe1e4cb05aea9a2b9b35" in instance["authorization"]["approvalScope"]
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
print("Phase 5.46 authorization state: PASS")
