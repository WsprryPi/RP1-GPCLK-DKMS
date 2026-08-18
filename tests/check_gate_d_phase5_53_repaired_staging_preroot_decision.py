#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the repaired Phase 5.53 staging and pre-root decision prompt."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPT = ROOT / "docs/contracts/gate-d-phase5.53-repaired-staging-preroot-authorization-decision-prompt.md"
prompt = PROMPT.read_text()

expected = {
    "86e66cc26801a66742843afaaba714bcd1409cfd",
    "1062fd5e9a444c64efc2f240659e8d3d946891365976191b7b44f2c595a5b2b7",
    "6156391ff951b326dd0c303628d223e86ee491e08fdc83ec0af9a3c842618b1e",
    "3a6a6047dc8e3ca5c77488a5029bb2165f5b9e71bf32fdc94ec60dcf15ec15e2",
    "36d03d421bedaf2904e0421dfd82e3f942c037e5ff9cad268a60746479dd4f93",
    "d84efdaa5dabdd83d3e61523fe98e15a25979cface08081f67cf00e8d08c56da",
    "df8e80bc4b3382d9213d52cbc273b398e85124a2d2f58169c3a6f6aa339dbcf7",
    "ae6df3a66a9a26a6fb8474e5896c9053b9f69580d8c45383a5556fc397ebb549",
    "d931912d6ccc381b10a2a13d7f3a9122b0f748490ec8eefe0f86a28cb352c8d0",
    "c4bdf3e066527941e5762229d0162b738bea542ec8d47a2cdfda0e66ef7a0ebb",
    "7130a4950dd00f04f4c74a55d3a41976a59752f95d269294a5aefa68644a5fad",
    "aa07ee829ee01d0bdcdfbc3c0882b2ddd582c9f48c5e8b69253b315522a47e9c",
}
assert all(value in prompt for value in expected)

instance_path = ROOT / "release/gate-d-execution-instance-phase5.53-v1.json"
envelope_path = ROOT / "release/gate-d-pre-root-bootstrap-envelope-phase5.53-v1.json"
attestation_path = ROOT / "docs/evidence/gate-d-phase5.53-preauthorization-recapture-attestation.json"
instance = json.loads(instance_path.read_text())
envelope = json.loads(envelope_path.read_text())
attestation = json.loads(attestation_path.read_text())
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

authorized = attestation["authorizedRepairedOfflineControls"]
assert sha(instance_path) == authorized["executionInstanceSha256"]
assert sha(envelope_path) == authorized["envelopeSha256"]
assert sha(attestation_path) in prompt
assert instance["authorization"]["approved"] is True
assert instance["authorization"]["targetExecutionApproved"] is True
assert instance["executionReady"] is True
assert len(envelope["inputFiles"]) == 64
assert len(envelope["releaseInputs"]) == 8
assert len(envelope["transitionFiles"]) == 55
assert len(envelope["installedTools"]) == 22
assert len(envelope["predecessorPackagePaths"]) == 28
assert attestation["repairedAuthorization"]["targetStagingAuthorized"] is False
assert attestation["repairedAuthorization"]["preRootTransitionAuthorized"] is False
assert "must not be reused" in prompt
assert "Stop before lifecycle attempt 1" in prompt
assert "This decision prompt is non-authorizing" in prompt
print("Phase 5.53 repaired staging and pre-root decision prompt: PASS")
