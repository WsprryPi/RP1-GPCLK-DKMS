#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
value = json.loads((ROOT / "docs/evidence/gate-d-phase5.50-metadata-free-staging-preroot-attestation.json").read_text())
assert value["kind"] == "gate-d-metadata-free-staging-preroot-attestation"
assert value["candidate"]["sourceCommit"] == "c24160517b10900bf61243d4988f38247eeed58e"
assert value["recapture"] == {
    "captureCount": 2,
    "size": 7082,
    "sha256": "3db85e0ada2427c997cdca878d0f2d53fc0c61d5aab68761e65a2a6cf349a6d5",
    "capturesByteIdentical": True,
    "rawByteComparison": "identical",
    "targetIndependentValidation": "passed",
    "localIndependentValidation": "passed",
}
transport = value["transport"]
assert transport["regularFileCount"] == 759
assert transport["directoryCount"] == 34
assert transport["forbiddenPathCount"] == 0
assert transport["extendedAttributeKeyCountOnTarget"] == 0
assert transport["targetPathSetIdentical"] is True
assert value["staging"]["inputCount"] == 63
assert value["transition"]["status"] == "complete"
assert value["transition"]["checkpoint"] == "commit"
assert value["transition"]["liveOutput"] is False
assert value["installedIdentities"]["transitionFilesVerified"] == 55
assert value["installedIdentities"]["installedToolsVerified"] == 22
assert value["installedIdentities"]["standaloneInstanceValidation"] == "passed"
assert value["installedIdentities"]["installedExecutorValidation"] == "blocked"
assert value["blocker"] == {
    "stage": "installed-permanent-executor-validation",
    "error": "installed trust bootstrap requires execution-instance schema 3, 4, or 5",
    "cause": "The frozen permanent executor omits schema 6 from its trust-bootstrap allowlist.",
    "requiresSuccessorCandidate": True,
}
assert value["postState"] == {
    "moduleLoaded": False,
    "endpointPresent": False,
    "overlayActive": False,
    "candidateDkmsTestVersionPresent": False,
    "allSixServicesInactive": True,
    "transientFilesRemoved": True,
    "lifecycleAttemptStarted": False,
    "outputDisabled": True,
}
print("Phase 5.50 pre-root transition failed closed before attempt 1: PASS")
