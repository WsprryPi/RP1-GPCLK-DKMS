#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
evidence = json.loads(
    (ROOT / "docs/evidence/phase5.54-closure-reconciliation.json").read_text()
)
roadmap = json.loads((ROOT / "release/release-integration-gates-v1.json").read_text())

assert evidence["reconciliationCommit"] == "4405babbeb192cdd3f8277f51d7d497283560643"
assert evidence["results"]["cleanWorktreePassCount"] == 2
assert evidence["results"]["offlineSuitePassedTwice"] is True
assert evidence["results"]["packageSuitePassedTwice"] is True
assert evidence["results"]["transcriptsByteIdentical"] is True
assert evidence["results"]["transcriptSha256Each"] == (
    "c5b8565ec4dc9ed3e82bc5fdae4f63f815ae725e4e28b236a8db96a2f9691061"
)
assert evidence["nextGate"] == "semantic-version-selection"
assert evidence["result"] == "pass-next-gate-semantic-version-selection"

gates = {gate["id"]: gate for gate in roadmap["gates"]}
assert gates["closure-reconciliation"]["status"] == "passed"
assert gates["offline-checks-twice"]["status"] == "passed"
assert gates["semantic-version-selection"]["status"] == "blocked"
assert roadmap["expectedTag"] is None
assert roadmap["modulePublicationConfirmed"] is False
assert roadmap["candidateSnapshot"]["consumableByDependentRelease"] is False

print("Phase 5.54 closure reconciliation: PASS")
