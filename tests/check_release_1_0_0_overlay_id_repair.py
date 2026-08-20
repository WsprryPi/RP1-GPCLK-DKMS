#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
evidence = json.loads((ROOT / "docs/evidence/release-1.0.0-overlay-id-capture-repair.json").read_text())
roadmap = json.loads((ROOT / "release/release-integration-gates-v1.json").read_text())
prompt = (ROOT / "docs/contracts/release-1.0.0-repaired-target-verification-authorization-prompt.md").read_text()

assert evidence["productChanged"] is False
assert evidence["productPackageSha256"] == roadmap["candidateSnapshot"]["finalPackageSha256"]
assert evidence["qualificationArchiveSha256"] == roadmap["candidateSnapshot"]["qualificationArchiveSha256"]
assert evidence["qualificationBuildCount"] == 2
assert evidence["byteIdenticalQualificationBuilds"] is True
assert evidence["repair"]["applyStdoutUsedForIdentity"] is False
assert all(value for key, value in evidence["repair"].items() if key != "applyStdoutUsedForIdentity")
assert all(evidence["fakeSystem"].values())
assert evidence["successorPlan"]["stepCount"] == 8
assert evidence["successorPlan"]["redundantInitialPackageInstall"] is False
assert evidence["targetContacted"] is False
assert evidence["result"] == "repaired-reproduced-awaiting-new-authorization"
for identity in (evidence["repairSourceCommit"], evidence["productPackageSha256"], evidence["qualificationArchiveSha256"]):
    assert identity in prompt
for phrase in ("before/after overlay-listing delta", "Do not reuse or patch", "without retry or improvisation", "live_output=1"):
    assert phrase in prompt

print("Release 1.0.0 overlay-ID capture repair: PASS")
