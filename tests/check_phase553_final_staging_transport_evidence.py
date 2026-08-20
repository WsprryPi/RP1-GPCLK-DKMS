#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate final Phase 5.53 staging-transport successor evidence."""
from __future__ import annotations
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
value = json.loads((ROOT / "docs/evidence/phase5.53-final-staging-transport-successor.json").read_text())
assert value["kind"] == "phase5.53-final-staging-transport-successor"
assert value["qualificationArchiveSha256"] == "916a5522e3998ae43f203c217fedce90ad8d4c2d52ae0bd4491407e3cf17211d"
assert value["preRootEnvelopeSha256"] == "c32b3f196b48aa0c10da4067173d6025f91c642f7ff3b5c770d5ef5fba5d0bf2"
assert value["sameVersionPlanSha256"] == "30f93036c63db3c2ca9a6d14c9905928f940878c12d5d757c0d761ad4eedbb3c"
closure = value["closure"]
assert closure == {"envelopeInputCount": 63, "releaseInputCount": 8,
    "transitionFileCount": 54, "productArchiveRegularFileCount": 54,
    "qualificationArchiveRegularFileCount": 33, "separatelySealedControlCount": 2,
    "transportRegularFileCount": 151, "transportDirectoryCountIncludingRoot": 31}
assert value["reproduction"]["generationCount"] == 2
assert value["reproduction"]["byteIdentical"] is True
assert value["reproduction"]["transportSha256"] == "f8ea112c2b3ff1fe18c8d48dc54f4ee8a5f41427595a163ddde2907e11c9a73b"
assert value["offlineExercise"] == {"allEnvelopeInputsValidated": True,
    "allSameVersionStagedArgvPathsResolved": True,
    "sameVersionDriverReadOnlyValidationPassed": True,
    "preRootEntrypointReadOnlyValidationPassed": True, "targetContacted": False}
print("Phase 5.53 final staging-transport successor evidence: PASS")
