#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
evidence = json.loads((ROOT / "docs/evidence/release-1.0.0-module-publication-success.json").read_text())
roadmap = json.loads((ROOT / "release/release-integration-gates-v1.json").read_text())
gates = {gate["id"]: gate for gate in roadmap["gates"]}

assert evidence["tag"]["name"] == "v1.0.0"
assert evidence["tag"]["peeledCommit"] == "d8c45a33e9a8b16cf5ea9a89736347347bc14817"
assert evidence["githubRelease"]["draft"] is False
assert evidence["githubRelease"]["prerelease"] is False
assert len(evidence["assets"]) == 8
assert evidence["assets"]["rp1-gpclk-dkms_1.0.0-1_all.deb"]["sha256"] == roadmap["candidateSnapshot"]["finalPackageSha256"]
assert evidence["assets"]["rp1-gpclk-dkms-qualification-1.0.0.tar.gz"]["sha256"] == roadmap["candidateSnapshot"]["qualificationArchiveSha256"]
assert all(evidence["verification"].values())
assert evidence["publicAssetsDownloadedFresh"] is False
assert evidence["publicDownloadVerificationPassed"] is False
assert roadmap["modulePublicationConfirmed"] is True
assert roadmap["currentClassification"] == "publicly-verified-consumable-module-release"
assert gates["module-publication"]["status"] == "passed"
assert gates["public-download-verification"]["status"] == "passed"
assert evidence["nextGate"] == "fresh public-download verification"

print("Release 1.0.0 module publication: PASS")
