#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate qualification-only installation successor evidence."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
value = json.loads((ROOT / "docs/evidence/phase5.53-qualification-only-install-successor.json").read_text())
assert value["kind"] == "phase5.53-qualification-only-install-successor"
assert value["sourceCommit"] == "17b8ed285450c37aaf858080b53857737638c6e9"
assert value["retainedProductArchiveSha256"] == "032a0ca214427ebb6115b933042e7135f03c2ed6ce4f5c399686b2cf61395a76"
assert value["qualificationArchiveSha256"] == "6dd18ef1543cf824aba1c9d9057fd014c529df149ef705b721e9d75ad4bbe3bc"
assert value["generation"] == {"count": 2, "byteIdentical": True,
    "independentValidationCount": 2, "productArchiveRetainedByteIdentical": True}
assert value["installer"]["qualificationOnly"] is True
assert all(value["installer"][field] == 0 for field in
           ("ordinaryDkmsCommands", "moduleCommands", "overlayCommands",
            "bootCommands", "serviceCommands"))
assert value["exercise"]["archivedInstallerFakeSystemInstallRemove"] == "passed"
assert value["installer"]["interruptedBuildRecoveryExercised"] is True
assert value["installer"]["ledgerPathsConfinedToInstallRoot"] is True
assert value["targetReady"] is False
assert value["targetContactPerformed"] is False
assert value["targetMutationPerformed"] is False
assert value["hardwareOrRfActivityPerformed"] is False
print("Phase 5.53 qualification-only installation successor: PASS")
