#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the Phase 5.51 preauthorization recapture attestation."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATTESTATION = ROOT / "docs/evidence/gate-d-phase5.51-preauthorization-recapture-attestation.json"
value = json.loads(ATTESTATION.read_text()); snapshot = ROOT / value["canonicalSnapshot"]["path"]
assert value["controlSetCommit"] == "64baef473a04810627598015b32797e46e6e43a2"
assert snapshot.stat().st_size == value["canonicalSnapshot"]["size"] == value["recapture"]["size"] == 7082
digest = hashlib.sha256(snapshot.read_bytes()).hexdigest()
assert digest == value["canonicalSnapshot"]["sha256"] == value["recapture"]["sha256"] == "badb3633cdf6bacce6fa3292174d3cea993a1ed4f0278f75c597bd204ee63e9a"
assert value["recapture"]["captureCount"] == 2 and value["recapture"]["capturesByteIdentical"] is True
assert value["recapture"]["installedOnTarget"] is False and value["recapture"]["temporaryFilesRemoved"] is True
assert set(value["validation"].values()) == {"passed", "identical"}
for key, relative in {
    "envelopeSha256":"release/gate-d-pre-root-bootstrap-envelope-phase5.51-v1.json",
    "executionInstanceSha256":"release/gate-d-execution-instance-phase5.51-v1.json",
    "attemptIndexSha256":"release/gate-d-attempts-phase5.51-v1/index.json"}.items():
    payload = subprocess.check_output(["git","show",f"{value['controlSetCommit']}:{relative}"], cwd=ROOT)
    assert hashlib.sha256(payload).hexdigest() == value["controls"][key]
instance = json.loads(subprocess.check_output(["git","show",f"{value['controlSetCommit']}:release/gate-d-execution-instance-phase5.51-v1.json"], cwd=ROOT))
assert instance["authorization"]["approved"] is False and instance["authorization"]["targetExecutionApproved"] is False
assert instance["inputsReady"] is True and instance["executionReady"] is False
assert value["releaseArchive"]["sha256"] == "253bd54054eb0b673f9e61c58a46b6b7ca2cf78d756fe4e80656f4ac1233f549"
assert value["result"] == {"controlSetRetired":False,"eligibleForSeparateAuthorizationDecision":True,"authorizationRecorded":False,"targetStaged":False,"lifecycleExecuted":False}
print("Phase 5.51 preauthorization recapture: PASS")
