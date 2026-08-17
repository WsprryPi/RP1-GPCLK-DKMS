#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Ensure the Phase 5.48 decision prompt is exact and non-authorizing."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
prompt = (ROOT / "docs/contracts/gate-d-phase5.48-authorization-decision-prompt.md").read_text()
expected = {
    "833db92a5b3aadf30c3dd617bea734d0d7f5b20a",
    "7423b5076563486123ca32d32406550f68b12d84",
    "ef96f246b66b25bb70536341b60a5f1e64708c65",
    "18418395eac577d8718c1e74f6601e005160d2768ea7634a35d00e4ddead9120",
    "9377d109235305f29e85134026cf9247e5d462b0bd2c8e05d9c0463162156e33",
    "a477e0acc2d6e85d769791b4e6fa82e8a2ea6e9324718f1ac82cd21dd4811d8c",
    "342a4837f239033aeeccfd8b32a1972ba3189a2424e4b8d21f58ccf3c8630c88",
    "aa71bda96970d8e1c2faabf7121a8015cefa5148fde5cb89d809cfef1d37265f",
}
assert all(identity in prompt for identity in expected)
attestation = ROOT / "docs/evidence/gate-d-phase5.48-preauthorization-recapture-attestation.json"
assert hashlib.sha256(attestation.read_bytes()).hexdigest() in prompt
instance = json.loads(subprocess.check_output([
    "git", "show",
    "7423b5076563486123ca32d32406550f68b12d84:release/gate-d-execution-instance-phase5.48-v1.json"
], cwd=ROOT))
assert instance["authorization"]["targetExecutionApproved"] is False
assert instance["executionReady"] is False
assert "This prompt does not itself record authorization" in prompt
assert "complete exact archived Phase 5.48 Python and executor" in prompt
print("Phase 5.48 authorization decision prompt: PASS")
