#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Ensure the Phase 5.50 decision prompt is exact and non-authorizing."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
prompt = (ROOT / "docs/contracts/gate-d-phase5.50-authorization-decision-prompt.md").read_text()
expected = {
    "8e908928642bf3a4052f13cfb087c77a9bcbc7f8",
    "dbc983e275ca6250c93d67d6dc3639f32ad3dff1",
    "c24160517b10900bf61243d4988f38247eeed58e",
    "ef989bf79faa5c30ddaf8ac5651d75b1755ba2fa385680692183e6145b2927c2",
    "3db85e0ada2427c997cdca878d0f2d53fc0c61d5aab68761e65a2a6cf349a6d5",
    "620932f550ee70273d7f57b12a6406bfbb50722356d4ccf6542493120ad80fe0",
    "ea907b44043421a483009f1c9998be2e71732a54a32eabf398231e29af1e8226",
    "44c7bdb65e71970f1f15ef2c9d36bb6b1172ddb33350e19c0a2e3874ea3dc66f",
}
assert all(identity in prompt for identity in expected)
attestation = ROOT / "docs/evidence/gate-d-phase5.50-preauthorization-recapture-attestation.json"
assert hashlib.sha256(attestation.read_bytes()).hexdigest() in prompt
instance = json.loads(subprocess.check_output([
    "git", "show",
    "dbc983e275ca6250c93d67d6dc3639f32ad3dff1:release/gate-d-execution-instance-phase5.50-v1.json"
], cwd=ROOT))
assert instance["authorization"]["approved"] is False
assert instance["authorization"]["targetExecutionApproved"] is False
assert instance["executionReady"] is False
assert "This prompt does not itself record authorization" in prompt
assert "complete exact archived Phase" in prompt
assert "Python, schema, and executor tool graph" in prompt
print("Phase 5.50 authorization decision prompt: PASS")
