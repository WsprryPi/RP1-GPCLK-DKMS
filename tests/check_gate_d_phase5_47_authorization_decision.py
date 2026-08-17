#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Ensure the Phase 5.47 decision prompt is exact and non-authorizing."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
prompt = (ROOT / "docs/contracts/gate-d-phase5.47-authorization-decision-prompt.md").read_text()
expected = {
    "547201f4973bc14776651962e0aba8e020b5a1f3",
    "0bcacf062762afe01891a01f10fb83c57796af2c",
    "c5320ac5419a04d17345370204524f219b7ff403",
    "497368ac11b32e5491dab76103ad3bb2da0975c086e9898a801c5c2df1be82be",
    "7f018fb331c769c44eb1691fdabc4a8a6ff22e0a3debc9e1ed69404d829332b0",
    "616fc066cde992c28dc2c9647dd93fc5bdf8ca9e70938642379017bae591cc16",
    "6d5aa62b1c4a0611ea97fcc7568b4b2b0d7448d5cd1bea36d0f9a5c59e738d1c",
    "dc68030fa86386659f92a93f56a96d05979af2c541d1be7bfc3e3b33c2e4651d",
}
assert all(identity in prompt for identity in expected)
attestation = ROOT / "docs/evidence/gate-d-phase5.47-preauthorization-recapture-attestation.json"
assert hashlib.sha256(attestation.read_bytes()).hexdigest() in prompt
instance = json.loads(subprocess.check_output([
    "git", "show",
    "0bcacf062762afe01891a01f10fb83c57796af2c:release/gate-d-execution-instance-phase5.47-v1.json"
], cwd=ROOT))
assert instance["authorization"]["targetExecutionApproved"] is False
assert instance["executionReady"] is False
assert "This prompt does not itself record authorization" in prompt
assert "complete exact archived Phase 5.47 Python and executor" in prompt
print("Phase 5.47 authorization decision prompt: PASS")
