#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Ensure the Phase 5.51 decision prompt is exact and non-authorizing."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
prompt = (ROOT / "docs/contracts/gate-d-phase5.51-authorization-decision-prompt.md").read_text()
expected = {
    "64baef473a04810627598015b32797e46e6e43a2",
    "cd81650bd324ec3e8d608bfe2cc67252d34e4e88",
    "cc87e0cdec7195eb69de2a6606f388e23ee0799c",
    "253bd54054eb0b673f9e61c58a46b6b7ca2cf78d756fe4e80656f4ac1233f549",
    "badb3633cdf6bacce6fa3292174d3cea993a1ed4f0278f75c597bd204ee63e9a",
    "37317c18c907ddd9af9856bade74fd3ec5e60aaab046fa2732cb81de8de5c81a",
    "7f64de228549c1a64748d80a6123e18c0dbc07e63861d0e192b5ddfe0098e444",
    "a1d547226090dbcb58375774983ebe7a0fa3cd05e30963b58d7dc2e5524f2960",
}
assert all(identity in prompt for identity in expected)
attestation = ROOT / "docs/evidence/gate-d-phase5.51-preauthorization-recapture-attestation.json"
assert hashlib.sha256(attestation.read_bytes()).hexdigest() in prompt
instance = json.loads(subprocess.check_output([
    "git", "show",
    "cd81650bd324ec3e8d608bfe2cc67252d34e4e88:release/gate-d-execution-instance-phase5.51-v1.json"
], cwd=ROOT))
assert instance["authorization"]["approved"] is False
assert instance["authorization"]["targetExecutionApproved"] is False
assert instance["executionReady"] is False
assert "This prompt does not itself record authorization" in prompt
assert "complete exact archived Phase" in prompt
assert "Python, schema, and executor tool graph" in prompt
print("Phase 5.51 authorization decision prompt: PASS")
