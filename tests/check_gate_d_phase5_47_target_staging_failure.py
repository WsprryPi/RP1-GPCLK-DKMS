#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the Phase 5.47 failed-closed target-staging attestation."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
value = json.loads((ROOT / "docs/evidence/gate-d-phase5.47-target-staging-preroot-failure-attestation.json").read_text())

assert value["authorizationCommit"] == "ecfb65795f8a79a7d60264814c8fea2ac459d15d"
assert value["recapture"] == {
    "size": 7057,
    "sha256": "7f018fb331c769c44eb1691fdabc4a8a6ff22e0a3debc9e1ed69404d829332b0",
    "rawByteComparison": "identical",
    "targetIndependentValidation": "passed",
    "localIndependentValidation": "passed",
}
assert value["staging"]["inputCount"] == 62
assert value["staging"]["targetPathSetVerification"] == "failed"
assert "AppleDouble" in value["staging"]["failure"]
negative = value["negativeContentReview"]
assert negative["sealedArchiveAppleDoubleMemberCount"] == 0
assert negative["targetExtrasRejected"] is True
assert "not in independently derived allowlist" in negative["forbiddenClasses"]
assert value["transition"] == {
    "started": False,
    "administratorInvoked": False,
    "lifecycleAttemptStarted": False,
    "liveOutput": False,
}
assert all(value["cleanup"].values())
post = value["postState"]
assert post["allSixServicesInactive"] is True and post["outputDisabled"] is True
assert not any(post[key] for key in (
    "moduleLoaded", "endpointPresent", "overlayActive",
    "candidateDkmsTestVersionPresent",
))
print("Phase 5.47 target staging failed closed and cleaned up: PASS")
