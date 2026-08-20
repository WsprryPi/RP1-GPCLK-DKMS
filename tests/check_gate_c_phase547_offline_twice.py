#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate exact-freeze Phase 5.47 offline-checks-twice evidence."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidence/gate-c-phase5.47-offline-checks-twice.json"
TRANSCRIPT = ROOT / "docs/evidence/gate-c-phase5.47-offline-checks-twice-transcript.txt"

value = json.loads(EVIDENCE.read_text())
assert value["release"] == "0.0.0-phase5.47"
assert value["sourceCommit"] == "c5320ac5419a04d17345370204524f219b7ff403"
assert value["worktreeState"] == "clean-detached-exact-commit"
assert value["archivedReleaseInputs"] == [
    {"release": "0.0.0-phase5.43", "sha256": "a8a200d069ad433353a8812ef6a9a4c585b75a9f6af3d6501ac3672e90c997c3"},
    {"release": "0.0.0-phase5.45", "sha256": "21d05675e9d12ddb4c051868578c410737b733786357cee20eb2b0ce03f63356"},
    {"release": "0.0.0-phase5.46", "sha256": "0e0debdd96560602bd61457afc59782cfad2a4fb1b6f9b54e0d2505453e6c8f2"},
]
assert value["transcriptsByteIdentical"] is True
assert value["result"] == "passed"
runs = value["runs"]
assert len(runs) == 2
transcript_hash = hashlib.sha256(TRANSCRIPT.read_bytes()).hexdigest()
assert transcript_hash == "d113c818841adae4ca77ec23fe04a88989bd4c85b9a79b5cfd7a882e4149413b"
assert all(run["exitStatus"] == 0 and run["passLines"] == 105 and
           run["skipLines"] == 3 and run["failLines"] == 0 and
           run["transcriptSha256"] == transcript_hash for run in runs)
lines = TRANSCRIPT.read_text().splitlines()
assert len(lines) == 122
assert sum("PASS" in line for line in lines) == 105
assert sum("SKIP" in line for line in lines) == 3
assert not any("FAIL" in line for line in lines)
assert value["declaredSkips"] == [
    "Phase 2E UAPI client compile: Linux target only",
    "Phase 3B UAPI client compile: Linux target only",
    "Phase 4A UAPI client compile: Linux target only",
]

print("Phase 5.47 offline checks twice: PASS")
