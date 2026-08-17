#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the exact Phase 5.45 authorized control state."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


instance_path = ROOT / "release/gate-d-execution-instance-phase5.45-v1.json"
envelope_path = ROOT / "release/gate-d-pre-root-bootstrap-envelope-phase5.45-v1.json"
index_path = ROOT / "release/gate-d-attempts-phase5.45-v1/index.json"
attestation_path = ROOT / "docs/evidence/gate-d-phase5.45-authorization-attestation.json"
prompt = (ROOT / "docs/contracts/gate-d-phase5.45-authorized-execution-prompt.md").read_text()

instance = json.loads(instance_path.read_text())
attestation = json.loads(attestation_path.read_text())
expected_instance = "0a4e2b88263262d408aa30c39e4843aa1204735333cedf6bb472dfc1a50ef228"
expected_envelope = "1a01c76d95e06fae7a132b05c3dc5d1ef3db1c71ea4e00fc4f7d6a10cc686742"
expected_index = "3375c809dd699949f991742716628016a680bcf7253fc30ba8f3de52c294f020"

assert sha256(instance_path) == expected_instance
assert sha256(envelope_path) == expected_envelope
assert sha256(index_path) == expected_index
assert instance["authorization"]["targetExecutionApproved"] is True
assert instance["executionReady"] is True
assert "d25abbf877fb889435b16e0b7d033291d0388af5" in instance["authorization"]["approvalScope"]
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
print("Phase 5.45 authorization state: PASS")
