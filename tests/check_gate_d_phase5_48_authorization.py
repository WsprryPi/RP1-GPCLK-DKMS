#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the exact Phase 5.48 authorized control state."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


instance_path = ROOT / "release/gate-d-execution-instance-phase5.48-v1.json"
envelope_path = ROOT / "release/gate-d-pre-root-bootstrap-envelope-phase5.48-v1.json"
index_path = ROOT / "release/gate-d-attempts-phase5.48-v1/index.json"
attestation_path = ROOT / "docs/evidence/gate-d-phase5.48-authorization-attestation.json"
prompt = (ROOT / "docs/contracts/gate-d-phase5.48-authorized-execution-prompt.md").read_text()

instance = json.loads(instance_path.read_text())
attestation = json.loads(attestation_path.read_text())
expected_instance = "3dc6dff32898768e52f9a6d5d46075b65a33a60c3759d14dbae53009134cc667"
expected_envelope = "9d01a08530d6d059936d51e4a5dbd796cd8b3353efbd5d52cf891ee51e5b3699"
expected_index = "aa71bda96970d8e1c2faabf7121a8015cefa5148fde5cb89d809cfef1d37265f"

assert sha256(instance_path) == expected_instance
assert sha256(envelope_path) == expected_envelope
assert sha256(index_path) == expected_index
assert instance["authorization"]["targetExecutionApproved"] is True
assert instance["executionReady"] is True
assert "74e8d1cc9de118e96444ef71c7d0ed34eb25e3d8" in instance["authorization"]["approvalScope"]
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
print("Phase 5.48 authorization state: PASS")
