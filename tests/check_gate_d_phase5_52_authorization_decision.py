#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Ensure the Phase 5.52 decision prompt is exact and non-authorizing."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
prompt = (ROOT / "docs/contracts/gate-d-phase5.52-authorization-decision-prompt.md").read_text()
expected = {
    "477d0b0c62b70a56a6ca61e9b3b56114461db2e5",
    "38861a81155242caac79dcecc3cfcc722843d0c2",
    "f710554c4697d75210cbd33c9eea13474d60557a",
    "0c67dee49a26bf5ab103d04bcf493bba8ae373a9f45b87e5704f52ede96bce01",
    "449201a0a51ca8b278b7ae077410e515aa9c176eac42f4ba86bd62ef4c36451f",
    "735a57afd22879f6818fe727341f4c7d5dc4c9d13f0600ce404991bfb3f46c45",
    "5de1a85eafa53a50829d19799655a8f680760e16bb83a39ffdd284b9aafaaf52",
    "744427cc21988c73558dd7a2c89fdbf97915288bf539941e67a8cf080c0e90d8",
}
assert all(identity in prompt for identity in expected)
attestation = ROOT / "docs/evidence/gate-d-phase5.52-preauthorization-recapture-attestation.json"
assert hashlib.sha256(attestation.read_bytes()).hexdigest() in prompt
instance = json.loads(subprocess.check_output([
    "git", "show",
    "38861a81155242caac79dcecc3cfcc722843d0c2:release/gate-d-execution-instance-phase5.52-v1.json",
], cwd=ROOT))
assert instance["authorization"]["approved"] is False
assert instance["authorization"]["targetExecutionApproved"] is False
assert instance["executionReady"] is False
assert "This prompt does not itself record authorization" in prompt
assert "complete exact archived Phase" in prompt
assert "Python, schema, and executor tool graph" in prompt
print("Phase 5.52 authorization decision prompt: PASS")
