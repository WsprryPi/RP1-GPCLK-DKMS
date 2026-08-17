#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the Phase 5.45 preauthorization recapture attestation."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
value = json.loads((ROOT / "docs/evidence/gate-d-phase5.45-preauthorization-recapture-attestation.json").read_text())
snapshot = ROOT / value["canonicalSnapshot"]["path"]
assert value["controlSetCommit"] == "53e55780d6e1aec4551836e9c499de501a83a602"
assert snapshot.stat().st_size == value["canonicalSnapshot"]["size"] == 7057
assert hashlib.sha256(snapshot.read_bytes()).hexdigest() == \
    value["canonicalSnapshot"]["sha256"] == value["recapture"]["sha256"]
assert value["recapture"]["temporaryFilesRemoved"] is True
assert set(value["validation"].values()) == {"passed", "identical"}
result = value["result"]
assert result["controlSetRetired"] is False
assert result["eligibleForSeparateAuthorizationDecision"] is True
assert result["authorizationRecorded"] is False
assert result["targetStaged"] is result["lifecycleExecuted"] is False
instance = json.loads((ROOT / "release/gate-d-execution-instance-phase5.45-v1.json").read_text())
assert instance["authorization"]["targetExecutionApproved"] is False
assert instance["executionReady"] is False
print("Phase 5.45 preauthorization recapture: PASS")
