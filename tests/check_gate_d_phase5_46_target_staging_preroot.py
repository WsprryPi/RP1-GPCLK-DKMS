#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the Phase 5.46 target-staging and pre-root attestation."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
value = json.loads((ROOT / "docs/evidence/gate-d-phase5.46-target-staging-preroot-attestation.json").read_text())
envelope = json.loads((ROOT / "release/gate-d-pre-root-bootstrap-envelope-phase5.46-v1.json").read_text())
instance = ROOT / "release/gate-d-execution-instance-phase5.46-v1.json"
index = ROOT / "release/gate-d-attempts-phase5.46-v1/index.json"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

assert value["authorizationCommit"] == "6b3dcc83c817e6c0011e6dde649b146df88abc91"
assert value["recapture"]["sha256"] == envelope["liveTargetSnapshotSha256"]
assert value["recapture"]["size"] == 7057
assert value["staging"]["inputCount"] == len(envelope["inputFiles"]) == 62
assert value["staging"]["envelopeSha256"] == sha(ROOT / "release/gate-d-pre-root-bootstrap-envelope-phase5.46-v1.json")
assert value["installedIdentities"]["executorSha256"] == envelope["installedPackagePaths"][4]["sha256"]
assert value["installedIdentities"]["rootMarkerSha256"] == envelope["proposedRoot"]["markerSha256"]
assert value["installedIdentities"]["executionInstanceSha256"] == sha(instance)
assert value["installedIdentities"]["attemptIndexSha256"] == sha(index)
assert value["transition"] == {
    "operationId": "phase5.46-pre-root-transition",
    "status": "complete",
    "checkpoint": "commit",
    "completedAt": "2026-08-17T15:06:11.123945+00:00",
    "administratorInvoked": True,
    "liveOutput": False,
}
post = value["postState"]
assert post["allSixServicesInactive"] is True
assert post["transientFilesRemoved"] is True
assert post["lifecycleAttemptStarted"] is False
assert not any(post[key] for key in (
    "moduleLoaded", "endpointPresent", "overlayActive",
    "candidateDkmsTestVersionPresent"))
assert post["outputDisabled"] is True
print("Phase 5.46 target staging and pre-root transition: PASS")
