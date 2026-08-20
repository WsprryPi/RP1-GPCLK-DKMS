#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Ensure the Phase 5.46 decision prompt is exact and non-authorizing."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
prompt = (ROOT / "docs/contracts/gate-d-phase5.46-authorization-decision-prompt.md").read_text()
expected = {
    "f1e5fa27bed175533f6a291152fa70700b88285b",
    "334d7cc3b2a14dc00e48ffb45f169ad7c8390c86",
    "b43e2744b212f5bc53ad40584254f52310af4684",
    "0e0debdd96560602bd61457afc59782cfad2a4fb1b6f9b54e0d2505453e6c8f2",
    "bc4c307350d6e74c9cbb85ef890fbaf0e8ad969ecdeb661a98703b70bd4a1859",
    "480f5cfece7b2de88f84ec60e1bdf7ee50af08bea46e17efc49234e45ffe21cc",
    "a7c815965d5b732f50bda6c7cf9b995c261532f611b3aa215745c0fbd44d7ecd",
    "e1858c68af8362a3c9ac969b5335317617e8e67491ddc916c3190c2eb6a8243d",
}
assert all(identity in prompt for identity in expected)
attestation = ROOT / "docs/evidence/gate-d-phase5.46-preauthorization-recapture-attestation.json"
assert hashlib.sha256(attestation.read_bytes()).hexdigest() in prompt
instance = json.loads(subprocess.check_output([
    "git", "show",
    "334d7cc3b2a14dc00e48ffb45f169ad7c8390c86:release/gate-d-execution-instance-phase5.46-v1.json"
], cwd=ROOT))
assert instance["authorization"]["targetExecutionApproved"] is False
assert instance["executionReady"] is False
assert "This prompt does not itself record authorization" in prompt
print("Phase 5.46 authorization decision prompt: PASS")
