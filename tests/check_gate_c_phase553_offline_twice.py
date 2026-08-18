#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate exact-freeze Phase 5.53 split-artifact offline evidence."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidence/gate-c-phase5.53-offline-checks-twice.json"
TRANSCRIPT = ROOT / "docs/evidence/gate-c-phase5.53-offline-checks-twice-transcript.txt"

value = json.loads(EVIDENCE.read_text())
assert value["release"] == "0.0.0-phase5.53"
assert value["sourceCommit"] == "1884c0f1c53c661495576bf10ce08d8bf7a90bc3"
assert value["worktreeState"] == "clean-detached-exact-commit"
split = value["splitReleaseUnit"]
assert split["productArchive"] == {
    "name": "rp1-gpclk-dkms-0.0.0-phase5.53.tar.gz",
    "sha256": "ae6df3a66a9a26a6fb8474e5896c9053b9f69580d8c45383a5556fc397ebb549",
    "members": 54,
}
assert split["qualificationArchive"] == {
    "name": "rp1-gpclk-dkms-qualification-0.0.0-phase5.53.tar.gz",
    "sha256": "8bd6eff31a90b95c43372d96bac47a4c6fe92b74de92da10e58d99a8ed63c052",
    "members": 25,
}
assert split["validatedEachRun"] is True
assert split["ordinaryInstallProductOnlyRegression"] == "passed"
assert split["qualificationModeDualArchiveRegression"] == "passed"
assert [item["release"] for item in value["archivedReleaseInputs"]] == [
    "0.0.0-phase5.43", "0.0.0-phase5.45", "0.0.0-phase5.46",
    "0.0.0-phase5.47", "0.0.0-phase5.48", "0.0.0-phase5.50",
    "0.0.0-phase5.51", "0.0.0-phase5.52",
]
assert value["archivedValidatorsPassed"] == [
    item["release"] for item in value["archivedReleaseInputs"]
]
assert len(value["runs"]) == 2
assert all(run["exitStatus"] == 0 and run["passLines"] == 172 and
           run["skipLines"] == 3 and run["failLines"] == 0
           for run in value["runs"])
assert value["transcriptsByteIdentical"] is True
assert len({run["transcriptSha256"] for run in value["runs"]}) == 1
assert hashlib.sha256(TRANSCRIPT.read_bytes()).hexdigest() == \
    value["runs"][0]["transcriptSha256"]
text = TRANSCRIPT.read_text()
assert "release unit validation: PASS (0.0.0-phase5.53" in text
for release in value["archivedValidatorsPassed"]:
    phase = release.removeprefix("0.0.0-phase")
    assert f"Phase {phase} exact archived" in text
assert text.count("SKIP") == 3 and "FAIL" not in text
assert value["result"] == "passed"
print("Phase 5.53 split-artifact offline checks twice: PASS")
