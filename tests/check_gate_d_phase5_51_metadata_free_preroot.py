#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the Phase 5.51 metadata-free staging and pre-root evidence."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
value = json.loads((ROOT / "docs/evidence/gate-d-phase5.51-metadata-free-staging-preroot-attestation.json").read_text())

assert value["kind"] == "gate-d-metadata-free-staging-preroot-attestation"
assert value["authorizationCommit"] == "f25ecb5f57cec4f255861e8f790aea11e4e804eb"
assert value["candidate"] == {
    "sourceCommit": "cc87e0cdec7195eb69de2a6606f388e23ee0799c",
    "archiveSha256": "253bd54054eb0b673f9e61c58a46b6b7ca2cf78d756fe4e80656f4ac1233f549",
}
assert value["recapture"] == {
    "captureCount": 2,
    "size": 7082,
    "sha256": "badb3633cdf6bacce6fa3292174d3cea993a1ed4f0278f75c597bd204ee63e9a",
    "capturesByteIdentical": True,
    "canonicalByteComparison": "identical",
    "targetArchivedValidation": "passed",
    "localArchivedValidation": "passed",
}
assert value["transport"] == {
    "format": "ustar",
    "sha256": "038607efc4bc8838939715f745c4dc68f038deb83684f83469f6c5f79fdb0929",
    "regularFileCount": 792,
    "directoryCountIncludingRoot": 34,
    "forbiddenPathCount": 0,
    "extendedAttributeKeyCountOnTarget": 0,
    "outerPaxHeaderCount": 0,
    "targetPathSetIdentical": True,
    "targetContentHashesIdentical": True,
}
assert value["staging"]["inputCount"] == 63
assert value["staging"]["archiveRegularMemberCount"] == 729
assert value["staging"]["allInputHashesVerifiedOnTarget"] is True
assert value["staging"]["archivedExecutorReadOnlyValidation"] == "passed"
assert value["transition"]["status"] == "complete"
assert value["transition"]["checkpoint"] == "commit"
assert value["transition"]["liveOutput"] is False
assert value["installedIdentities"]["transitionFilesVerified"] == 55
assert value["installedIdentities"]["installedToolsVerified"] == 22
assert value["installedIdentities"]["installedExecutorSchema6Validation"] == "passed"
assert value["postState"] == {
    "moduleLoaded": False,
    "endpointPresent": False,
    "overlayActive": False,
    "candidateDkmsTestVersionPresent": False,
    "allSixServicesInactive": True,
    "transientFilesRemoved": True,
    "forbiddenPathCount": 0,
    "lifecycleAttemptStarted": False,
    "outputDisabled": True,
}
print("Phase 5.51 metadata-free staging and pre-root transition: PASS")
