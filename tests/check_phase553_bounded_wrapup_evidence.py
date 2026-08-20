#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the Phase 5.53 bounded wrap-up safe-stop evidence."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
value = json.loads((ROOT / "docs/evidence/phase5.53-bounded-wrapup-readiness.json").read_text())
assert value["kind"] == "phase5.53-bounded-wrapup-readiness"
assert value["product"]["archiveSha256"] == "032a0ca214427ebb6115b933042e7135f03c2ed6ce4f5c399686b2cf61395a76"
assert value["qualification"]["archiveSha256"] == "916a5522e3998ae43f203c217fedce90ad8d4c2d52ae0bd4491407e3cf17211d"
assert value["product"]["literalRecordCount"] == value["product"]["uniqueNormalizedNames"] == 54
assert value["qualification"]["literalRecordCount"] == value["qualification"]["uniqueNormalizedNames"] == 33
assert value["blocker"]["acceptedQualificationIdentitySchemas"] == [1, 2, 3]
assert value["blocker"]["finalQualificationIdentitySchema"] == 4
assert value["blocker"]["targetReady"] is False
assert value["targetContactPerformed"] is False
assert value["targetMutationPerformed"] is False
assert value["hardwareOrRfActivityPerformed"] is False
print("Phase 5.53 bounded wrap-up safe stop: PASS")
