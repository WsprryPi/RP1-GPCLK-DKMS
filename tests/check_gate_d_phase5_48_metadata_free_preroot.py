#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
value = json.loads((ROOT / "docs/evidence/gate-d-phase5.48-metadata-free-staging-preroot-attestation.json").read_text())
assert value["kind"] == "gate-d-metadata-free-staging-preroot-attestation"
assert value["candidate"]["sourceCommit"] == "ef96f246b66b25bb70536341b60a5f1e64708c65"
assert value["recapture"] == {
    "size": 7057,
    "sha256": "9377d109235305f29e85134026cf9247e5d462b0bd2c8e05d9c0463162156e33",
    "rawByteComparison": "identical",
    "targetIndependentValidation": "passed",
    "localIndependentValidation": "passed",
}
transport = value["transport"]
assert transport["regularFileCount"] == 707
assert transport["forbiddenPathCount"] == 0
assert transport["extendedAttributeKeyCount"] == 0
assert transport["targetPathSetIdentical"] is True
assert value["staging"]["inputCount"] == 62
assert value["transition"]["status"] == "complete"
assert value["transition"]["checkpoint"] == "commit"
assert value["transition"]["liveOutput"] is False
assert value["installedIdentities"]["transitionFilesVerified"] == 54
assert value["installedIdentities"]["installedToolsVerified"] == 22
assert value["installedIdentities"]["installedExecutorValidation"] == "passed"
assert value["postState"] == {
    "moduleLoaded": False,
    "endpointPresent": False,
    "overlayActive": False,
    "candidateDkmsTestVersionPresent": False,
    "allSixServicesInactive": True,
    "forbiddenTargetFileCount": 0,
    "transientFilesRemoved": True,
    "lifecycleAttemptStarted": False,
    "outputDisabled": True,
}
print("Phase 5.48 metadata-free staging and pre-root evidence: PASS")
