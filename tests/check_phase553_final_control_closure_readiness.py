#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate final Phase 5.53 control-closure readiness evidence."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
value=json.loads((ROOT/"docs/evidence/phase5.53-final-control-closure-readiness.json").read_text())
assert value["kind"]=="phase5.53-final-control-closure-readiness"
assert value["productArchiveSha256"]=="032a0ca214427ebb6115b933042e7135f03c2ed6ce4f5c399686b2cf61395a76"
assert value["qualificationSourceCommit"]=="e86d5d58eb3c85dd6057b152f49205ec9138bb72"
assert value["qualificationArchiveSha256"]=="aae3c0f546917aeefd92d36ed6fe4de5522806056d8fb22a5c7abd0f1b7cacb1"
assert value["generations"]==2 and value["byteIdentical"] is True
assert value["independentValidationsPassed"]==2
assert value["closure"]["preRootSchemaVersion"]==7
assert value["closure"]["priorLedgerStatus"]=="removed"
assert value["closure"]["nonCyclic"] is True
assert value["closure"]["authorizationInherited"] is False
print("Phase 5.53 final control closure readiness: PASS")
