#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the Phase 5.52 preauthorization recapture attestation."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATTESTATION = ROOT / "docs/evidence/gate-d-phase5.52-preauthorization-recapture-attestation.json"
value = json.loads(ATTESTATION.read_text())
snapshot = ROOT / value["canonicalSnapshot"]["path"]
assert value["controlSetCommit"] == "477d0b0c62b70a56a6ca61e9b3b56114461db2e5"
assert snapshot.stat().st_size == value["canonicalSnapshot"]["size"] == \
    value["recapture"]["size"] == 7083
digest = hashlib.sha256(snapshot.read_bytes()).hexdigest()
assert digest == value["canonicalSnapshot"]["sha256"] == \
    value["recapture"]["sha256"] == \
    "449201a0a51ca8b278b7ae077410e515aa9c176eac42f4ba86bd62ef4c36451f"
assert value["recapture"]["captureCount"] == 2
assert value["recapture"]["capturesByteIdentical"] is True
assert value["recapture"]["installedOnTarget"] is False
assert value["recapture"]["temporaryFilesRemoved"] is True
assert set(value["validation"].values()) == {"passed", "identical"}
for key, relative in {
    "envelopeSha256":"release/gate-d-pre-root-bootstrap-envelope-phase5.52-v1.json",
    "executionInstanceSha256":"release/gate-d-execution-instance-phase5.52-v1.json",
    "attemptIndexSha256":"release/gate-d-attempts-phase5.52-v1/index.json",
}.items():
    payload = subprocess.check_output(
        ["git", "show", f"{value['controlSetCommit']}:{relative}"], cwd=ROOT)
    assert hashlib.sha256(payload).hexdigest() == value["controls"][key]
instance = json.loads(subprocess.check_output([
    "git", "show",
    f"{value['controlSetCommit']}:release/gate-d-execution-instance-phase5.52-v1.json",
], cwd=ROOT))
assert instance["authorization"]["approved"] is False
assert instance["authorization"]["targetExecutionApproved"] is False
assert instance["inputsReady"] is True and instance["executionReady"] is False
assert value["releaseArchive"]["sha256"] == \
    "0c67dee49a26bf5ab103d04bcf493bba8ae373a9f45b87e5704f52ede96bce01"
assert value["result"] == {
    "controlSetRetired":False,
    "eligibleForSeparateAuthorizationDecision":True,
    "authorizationRecorded":False,
    "targetStaged":False,
    "lifecycleExecuted":False,
}
print("Phase 5.52 preauthorization recapture: PASS")
