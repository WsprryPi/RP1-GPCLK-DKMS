#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate Phase 5.47 metadata-free staging and pre-root evidence."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
value = json.loads((ROOT / "docs/evidence/gate-d-phase5.47-metadata-free-staging-preroot-attestation.json").read_text())

assert value["authorizationCommit"] == "ecfb65795f8a79a7d60264814c8fea2ac459d15d"
assert value["failedPredecessorCommit"] == "da7cb93b62c2b825c7afa72417546de1420e8a0d"
assert value["recapture"]["sha256"] == "7f018fb331c769c44eb1691fdabc4a8a6ff22e0a3debc9e1ed69404d829332b0"
assert value["recapture"]["rawByteComparison"] == "identical"
transport = value["transport"]
assert transport["regularFileCount"] == 669
assert transport["forbiddenPathCount"] == 0
assert transport["extendedAttributeKeyCount"] == 0
assert transport["targetPathSetIdentical"] is True
assert value["staging"]["inputCount"] == 62
assert value["staging"]["allInputHashesVerifiedOnTarget"] is True
assert value["transition"] == {
    "operationId": "phase5.47-pre-root-transition",
    "status": "complete",
    "checkpoint": "commit",
    "completedAt": "2026-08-17T16:53:56.364828+00:00",
    "administratorInvoked": True,
    "liveOutput": False,
}
installed = value["installedIdentities"]
assert installed["transitionFilesVerified"] == 54
assert installed["installedToolsVerified"] == 22
assert installed["installedExecutorValidation"] == "passed"
post = value["postState"]
assert post["allSixServicesInactive"] and post["transientFilesRemoved"]
assert post["forbiddenTargetFileCount"] == 0
assert post["outputDisabled"] and not post["lifecycleAttemptStarted"]
assert not any(post[key] for key in (
    "moduleLoaded", "endpointPresent", "overlayActive",
    "candidateDkmsTestVersionPresent",
))
print("Phase 5.47 metadata-free staging and pre-root transition: PASS")
