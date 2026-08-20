#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the final qualification-only split offline gate evidence."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
value = json.loads((ROOT / "docs/evidence/phase5.53-final-qualification-only-split-offline-checks-twice.json").read_text())
assert value["kind"] == "phase5.53-final-qualification-only-split-offline-checks-twice"
assert value["product"]["archiveSha256"] == "032a0ca214427ebb6115b933042e7135f03c2ed6ce4f5c399686b2cf61395a76"
assert value["qualification"]["archiveSha256"] == "6dd18ef1543cf824aba1c9d9057fd014c529df149ef705b721e9d75ad4bbe3bc"
assert value["product"]["regenerated"] is False
assert value["qualification"]["regenerated"] is False
assert value["qualification"]["archivedInstallerFakeSystemInstallRemoveBeforeEachRun"] == "passed"
assert value["qualification"]["productSentinelUnchanged"] is True
assert len(value["runs"]) == 2
assert all(run == {"id": index, "exitStatus": 0, "passLines": 203,
                   "skipLines": 15, "failLines": 0,
                   "transcriptSha256": "29051d30d06467b5bb4371323e4ce696a8263c248eddef583caa4d42e5ddd8f9"}
           for index, run in enumerate(value["runs"], 1))
assert value["transcriptsByteIdentical"] is True
transcript = ROOT / value["durableTranscript"]
assert hashlib.sha256(transcript.read_bytes()).hexdigest() == value["runs"][0]["transcriptSha256"]
text = transcript.read_text()
assert text.count("PASS") == 203 and text.count("SKIP") == 15 and "FAIL" not in text
assert len(value["declaredSkips"]["historicalOrSeparatelySuppliedArchiveInputs"]) == 12
assert len(value["declaredSkips"]["linuxTargetOnlyCompileChecks"]) == 3
assert all(item in text for group in value["declaredSkips"].values() for item in group)
assert value["result"] == "passed"
assert value["nextGate"] == "qualification-tooling-installation"
assert value["targetContactPerformed"] is False
assert value["targetMutationPerformed"] is False
assert value["hardwareOrRfActivityPerformed"] is False
print("Phase 5.53 final qualification-only split offline checks twice: PASS")
