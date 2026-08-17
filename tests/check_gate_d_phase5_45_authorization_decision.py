#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Ensure the Phase 5.45 decision prompt is exact and non-authorizing."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
prompt = (ROOT / "docs/contracts/gate-d-phase5.45-authorization-decision-prompt.md").read_text()
expected = {
    "53e55780d6e1aec4551836e9c499de501a83a602",
    "59c83bd57de5eb69c1982c4c24bc868564f5f7d7",
    "4b50db7868b7fe5ca9d830f51cd404c250192188",
    "21d05675e9d12ddb4c051868578c410737b733786357cee20eb2b0ce03f63356",
    "66208586a112792e91185a7ce67d5952427dc218fb8a392ac1bfb221ed51e4c8",
    "8418fd031ac14e40c69c19b2d192783f2acf092351406b6455b3c96ede1f03ba",
    "39708b026f38da5edc83932a740d246233d26e4f87fccfc73a540e13542bef90",
    "3375c809dd699949f991742716628016a680bcf7253fc30ba8f3de52c294f020",
}
assert all(identity in prompt for identity in expected)
attestation = ROOT / "docs/evidence/gate-d-phase5.45-preauthorization-recapture-attestation.json"
assert hashlib.sha256(attestation.read_bytes()).hexdigest() in prompt
instance = json.loads((ROOT / "release/gate-d-execution-instance-phase5.45-v1.json").read_text())
assert instance["authorization"]["targetExecutionApproved"] is False
assert instance["executionReady"] is False
assert "This prompt does not itself record authorization" in prompt
print("Phase 5.45 authorization decision prompt: PASS")
