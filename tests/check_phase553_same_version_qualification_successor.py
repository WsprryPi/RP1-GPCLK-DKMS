#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate Phase 5.53 same-version qualification-successor evidence."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
value = json.loads((ROOT / "docs/evidence/phase5.53-same-version-qualification-successor.json").read_text())
assert value["kind"] == "phase5.53-same-version-qualification-successor"
assert value["product"] == {
    "sourceCommit": "4e7a64a0ca353d2fcab6e25891f5254746e2b91a",
    "archiveSha256": "032a0ca214427ebb6115b933042e7135f03c2ed6ce4f5c399686b2cf61395a76",
    "regenerated": False,
    "retainedByteIdentical": True,
}
successor = value["qualificationSuccessor"]
assert successor["sourceCommit"] == "927ed05b3466222b6e8795d8ed82221620480b65"
assert successor["archiveSha256"] == "e5614893f61fba63bc76dafa9d4d9ebab0e37437c3a7a8b2b997fa72891ffc59"
assert successor["members"] == 30
assert successor["generations"] == 2
assert successor["byteIdentical"] is True
assert successor["independentValidationsPassed"] == 2
assert successor["dirtySource"] is False
assert successor["publishable"] is False
assert value["orchestration"]["authorizationFieldsFalse"] is True
assert value["orchestration"]["liveOutputDisabled"] is True
assert value["validation"]["completeOfflineSuite"] == "passed"
assert value["claimCeiling"].startswith("offline qualification orchestration")
print("Phase 5.53 same-version qualification successor: PASS")
