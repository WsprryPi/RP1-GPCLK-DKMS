#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the frozen Phase 5.53 split-input control-set blocker."""

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "1884c0f1c53c661495576bf10ce08d8bf7a90bc3"
EVIDENCE = ROOT / "docs/evidence/gate-d-phase5.53-control-set-generation-blocker.json"
SNAPSHOT = ROOT / "docs/evidence/gate-d-live-target-snapshot-wspr5-phase5.53-v1.json"

value = json.loads(EVIDENCE.read_text())
assert value["release"] == "0.0.0-phase5.53" and value["sourceCommit"] == SOURCE
assert value["productArchiveSha256"] == \
    "ae6df3a66a9a26a6fb8474e5896c9053b9f69580d8c45383a5556fc397ebb549"
assert value["qualificationArchiveSha256"] == \
    "8bd6eff31a90b95c43372d96bac47a4c6fe92b74de92da10e58d99a8ed63c052"
assert value["snapshot"] == {
    "captures": 2,
    "byteIdentical": True,
    "sha256": "df8e80bc4b3382d9213d52cbc273b398e85124a2d2f58169c3a6f6aa339dbcf7",
    "readOnlyValidation": "passed",
}
assert hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest() == value["snapshot"]["sha256"]
attempt = value["attemptedControlSet"]
assert attempt["releaseInputCount"] == 8
assert attempt["requiredNewRole"] == "qualificationArchive"
assert not any(attempt[key] for key in
               ("authorizationApproved", "targetExecutionApproved", "executionReady"))
frozen = subprocess.check_output(
    ["git", "show", f"{SOURCE}:scripts/gate_d_preroot.py"], cwd=ROOT, text=True)
roles = frozen.split("RELEASE_INPUT_ROLES = {", 1)[1].split("}", 1)[0]
assert '"archive"' in roles and '"qualificationArchive"' not in roles
assert value["failedAssertion"] == "pre-root release-input graph is incomplete"
assert value["disposition"] == "blocked-fail-closed"
assert value["invalidGeneratedControlsRetained"] is False
assert value["prohibitedWorkPerformed"] is False
assert not (ROOT / "release/gate-d-execution-instance-phase5.53-v1.json").exists()
assert not (ROOT / "release/gate-d-attempts-phase5.53-v1").exists()
print("Phase 5.53 split-input control-set blocker: PASS")
