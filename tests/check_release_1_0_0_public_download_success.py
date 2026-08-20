#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
evidence = json.loads((ROOT / "docs/evidence/release-1.0.0-public-download-verification-success.json").read_text())
roadmap = json.loads((ROOT / "release/release-integration-gates-v1.json").read_text())
gates = {gate["id"]: gate for gate in roadmap["gates"]}

assert evidence["release"] == roadmap["release"] == "1.0.0"
assert evidence["releaseDecisionCommit"] == "d8c45a33e9a8b16cf5ea9a89736347347bc14817"
assert len(evidence["assets"]) == 8
assert evidence["assets"]["rp1-gpclk-dkms_1.0.0-1_all.deb"]["sha256"] == roadmap["candidateSnapshot"]["finalPackageSha256"]
assert evidence["assets"]["rp1-gpclk-dkms-qualification-1.0.0.tar.gz"]["sha256"] == roadmap["candidateSnapshot"]["qualificationArchiveSha256"]
assert all(value is True for key, value in evidence["verification"].items() if key not in {"productControlAndDataMemberCount", "qualificationRegularMemberCount", "qualificationCanonicalInventorySha256", "productContainsQualificationContent"})
assert evidence["verification"]["productContainsQualificationContent"] is False
assert evidence["verification"]["productControlAndDataMemberCount"] == 50
assert evidence["verification"]["qualificationRegularMemberCount"] == 16
assert all(value is False for value in evidence["safety"].values())
assert all(evidence["cleanup"].values())
assert evidence["result"] == "pass-public-release-download-verified-consumable"
assert evidence["nextGate"] == "consumer-integration"
assert roadmap["currentClassification"] == "publicly-verified-consumable-module-release"
assert roadmap["candidateSnapshot"]["consumableByDependentRelease"] is True
assert gates["public-download-verification"]["status"] == "passed"
assert gates["consumer-integration"]["status"] == "blocked"

print("Release 1.0.0 public-download verification: PASS")
