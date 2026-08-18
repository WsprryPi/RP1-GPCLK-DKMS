#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate exact Phase 5.53 recapture and offline authorization state."""
import hashlib, json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
attestation=json.loads((ROOT/"docs/evidence/gate-d-phase5.53-preauthorization-recapture-attestation.json").read_text())
instance=json.loads((ROOT/"release/gate-d-execution-instance-phase5.53-v1.json").read_text())
envelope=ROOT/"release/gate-d-pre-root-bootstrap-envelope-phase5.53-v1.json"
index=ROOT/"release/gate-d-attempts-phase5.53-v1/index.json"
assert attestation["controlSetCommit"]=="2838380a639d7af71ddc53be20829efd56cedc1d"
assert attestation["recapture"]=={"capturedUtc":"2026-08-18T16:00:18Z","captureCount":2,"capturesByteIdentical":True,"canonicalByteIdentical":True,"size":7083,"sha256":"df8e80bc4b3382d9213d52cbc273b398e85124a2d2f58169c3a6f6aa339dbcf7","targetFilesCreated":False,"targetMutationsPerformed":False}
assert sha(ROOT/attestation["captureTool"]["path"])==attestation["captureTool"]["sha256"]
authorized=attestation["authorizedOfflineControls"]
old_envelope=subprocess.check_output(["git","show","2d1a5c3e5ca2388679423aa4f2f0f07a56c2d830:release/gate-d-pre-root-bootstrap-envelope-phase5.53-v1.json"],cwd=ROOT)
assert hashlib.sha256(old_envelope).hexdigest()==authorized["envelopeSha256"]
repaired=attestation["repairedOfflineControls"]
assert sha(ROOT/"release/gate-d-execution-instance-phase5.53-v1.json")==repaired["executionInstanceSha256"]
assert sha(envelope)==repaired["envelopeSha256"] and sha(index)==repaired["attemptIndexSha256"]
assert instance["authorization"]["approved"] is False and instance["authorization"]["targetExecutionApproved"] is False and instance["executionReady"] is False
assert "require a new explicit authorization" in instance["authorization"]["approvalScope"]
assert attestation["authorization"]["targetStagingAuthorized"] is False and attestation["authorization"]["preRootTransitionAuthorized"] is False
assert attestation["result"]["targetStaged"] is False and attestation["result"]["lifecycleExecuted"] is False
assert attestation["result"]["controlSetRetired"] is True
print("Phase 5.53 authorization state: PASS")
