#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
evidence = json.loads((ROOT / "docs/evidence/release-1.0.0-final-artifact-reproduction.json").read_text())
repair = json.loads((ROOT / "docs/evidence/release-1.0.0-overlay-id-capture-repair.json").read_text())
roadmap = json.loads((ROOT / "release/release-integration-gates-v1.json").read_text())
snapshot = roadmap["candidateSnapshot"]
gates = {gate["id"]: gate for gate in roadmap["gates"]}

assert evidence["release"] == roadmap["release"] == "1.0.0"
assert evidence["debianVersion"] == roadmap["debianVersion"] == "1.0.0-1"
assert evidence["sourceCommit"] == snapshot["sourceCommit"] == "a20abc828ec300ad3227a34be7572f4fa28525b2"
assert evidence["product"]["sha256"] == snapshot["finalPackageSha256"]
assert repair["qualificationArchiveSha256"] == snapshot["qualificationArchiveSha256"]
assert repair["productPackageSha256"] == evidence["product"]["sha256"]
assert evidence["independentBuilds"] == 2
assert evidence["byteIdenticalArtifactSets"] is True
assert evidence["offlineSuite"]["runs"] == 2
assert evidence["offlineSuite"]["byteIdenticalTranscripts"] is True
assert evidence["product"]["dataMemberCount"] == 45
assert evidence["product"]["controlMemberCount"] == 5
assert evidence["qualification"]["regularMemberCount"] == 16
assert all(evidence["validation"].values())
assert gates["final-artifact-reproduction"]["status"] == "passed"
assert gates["final-candidate-target-verification"]["status"] == "blocked"
assert evidence["nextGate"] == "final-candidate-target-verification"
assert evidence["targetContacted"] is False
assert evidence["tagCreated"] is False
assert evidence["published"] is False
assert roadmap["modulePublicationConfirmed"] is False
assert snapshot["consumableByDependentRelease"] is False

print("Release 1.0.0 final artifact reproduction: PASS")
