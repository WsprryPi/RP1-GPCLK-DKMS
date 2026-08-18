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
repaired_instance=subprocess.check_output(["git","show","dff45f11720496a983327131972f7d78ca66ff70:release/gate-d-execution-instance-phase5.53-v1.json"],cwd=ROOT)
repaired_envelope=subprocess.check_output(["git","show","dff45f11720496a983327131972f7d78ca66ff70:release/gate-d-pre-root-bootstrap-envelope-phase5.53-v1.json"],cwd=ROOT)
assert hashlib.sha256(repaired_instance).hexdigest()==repaired["executionInstanceSha256"]
assert hashlib.sha256(repaired_envelope).hexdigest()==repaired["envelopeSha256"]
current=attestation["authorizedRepairedOfflineControls"]
assert sha(ROOT/"release/gate-d-execution-instance-phase5.53-v1.json")==current["executionInstanceSha256"]
assert sha(envelope)==current["envelopeSha256"] and sha(index)==current["attemptIndexSha256"]
assert instance["authorization"]["approved"] is True and instance["authorization"]["targetExecutionApproved"] is True and instance["executionReady"] is True
assert "target staging, pre-root transition, and lifecycle attempts" in instance["authorization"]["approvalScope"]
assert attestation["authorization"]["targetStagingAuthorized"] is False and attestation["authorization"]["preRootTransitionAuthorized"] is False
assert attestation["result"]["targetStaged"] is False and attestation["result"]["lifecycleExecuted"] is False
assert attestation["result"]["controlSetRetired"] is True
assert attestation["result"]["repairedControlSetAuthorized"] is True
assert attestation["repairedAuthorization"]["targetStagingAuthorized"] is False
assert attestation["repairedAuthorization"]["preRootTransitionAuthorized"] is False
print("Phase 5.53 authorization state: PASS")
