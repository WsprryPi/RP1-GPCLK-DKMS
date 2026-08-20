#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the final Phase 5.53 qualification successor freeze evidence."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
value = json.loads((ROOT / "docs/evidence/phase5.53-final-qualification-successor-freeze.json").read_text())
assert value["kind"] == "phase5.53-final-qualification-successor-freeze"
assert value["product"] == {
    "sourceCommit": "4e7a64a0ca353d2fcab6e25891f5254746e2b91a",
    "archiveSha256": "032a0ca214427ebb6115b933042e7135f03c2ed6ce4f5c399686b2cf61395a76",
    "regenerated": False,
    "retainedArtifactsByteIdentical": True,
}
successor = value["qualificationSuccessor"]
assert successor["sourceCommit"] == "2482f0121d16cbd1e4be6cbd93da0eff8d9876e7"
assert successor["archiveSha256"] == "65761067fae7f0fd150a10bf8a7b2e491fb501be2c3fbda1ea5be0d977de4c81"
assert successor["members"] == 28
assert successor["generations"] == 2
assert successor["byteIdentical"] is True
assert successor["independentValidationsPassed"] == 2
assert successor["dirtySource"] is False
assert value["validation"]["oneCompleteOfflineSuite"] == "passed"
assert value["nextGate"] == "final split-candidate offline-checks-twice"
assert "no lifecycle" in value["claimCeiling"]
print("Phase 5.53 final qualification successor freeze: PASS")
