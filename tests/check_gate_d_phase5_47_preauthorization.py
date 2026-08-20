#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the Phase 5.47 preauthorization recapture attestation."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATTESTATION = ROOT / "docs/evidence/gate-d-phase5.47-preauthorization-recapture-attestation.json"
value = json.loads(ATTESTATION.read_text())
snapshot = ROOT / value["canonicalSnapshot"]["path"]

assert value["controlSetCommit"] == "547201f4973bc14776651962e0aba8e020b5a1f3"
assert snapshot.stat().st_size == value["canonicalSnapshot"]["size"] == 7057
snapshot_sha = hashlib.sha256(snapshot.read_bytes()).hexdigest()
assert snapshot_sha == value["canonicalSnapshot"]["sha256"] == value["recapture"]["sha256"]
assert value["recapture"]["size"] == 7057
assert value["recapture"]["installedOnTarget"] is False
assert value["recapture"]["temporaryFilesRemoved"] is True
assert set(value["validation"].values()) == {"passed", "identical"}

for key, relative in {
    "envelopeSha256": "release/gate-d-pre-root-bootstrap-envelope-phase5.47-v1.json",
    "executionInstanceSha256": "release/gate-d-execution-instance-phase5.47-v1.json",
    "attemptIndexSha256": "release/gate-d-attempts-phase5.47-v1/index.json",
}.items():
    payload = subprocess.check_output([
        "git", "show", f"{value['controlSetCommit']}:{relative}"
    ], cwd=ROOT)
    assert hashlib.sha256(payload).hexdigest() == value["controls"][key]

result = value["result"]
assert result["controlSetRetired"] is False
assert result["eligibleForSeparateAuthorizationDecision"] is True
assert result["authorizationRecorded"] is False
assert result["targetStaged"] is result["lifecycleExecuted"] is False
instance = json.loads(subprocess.check_output([
    "git", "show",
    f"{value['controlSetCommit']}:release/gate-d-execution-instance-phase5.47-v1.json"
], cwd=ROOT))
assert instance["authorization"]["targetExecutionApproved"] is False
assert instance["executionReady"] is False
print("Phase 5.47 preauthorization recapture: PASS")
