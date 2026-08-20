#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate exact-freeze Phase 5.48 offline-checks-twice evidence."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidence/gate-c-phase5.48-offline-checks-twice.json"
TRANSCRIPT = ROOT / "docs/evidence/gate-c-phase5.48-offline-checks-twice-transcript.txt"
value = json.loads(EVIDENCE.read_text())

assert value["release"] == "0.0.0-phase5.48"
assert value["sourceCommit"] == "ef96f246b66b25bb70536341b60a5f1e64708c65"
assert value["worktreeState"] == "clean-detached-exact-commit"
assert value["archivedReleaseInputs"] == [
    {"release":"0.0.0-phase5.43","sha256":"a8a200d069ad433353a8812ef6a9a4c585b75a9f6af3d6501ac3672e90c997c3"},
    {"release":"0.0.0-phase5.45","sha256":"21d05675e9d12ddb4c051868578c410737b733786357cee20eb2b0ce03f63356"},
    {"release":"0.0.0-phase5.46","sha256":"0e0debdd96560602bd61457afc59782cfad2a4fb1b6f9b54e0d2505453e6c8f2"},
    {"release":"0.0.0-phase5.47","sha256":"497368ac11b32e5491dab76103ad3bb2da0975c086e9898a801c5c2df1be82be"},
]
assert value["transcriptsByteIdentical"] is True and value["result"] == "passed"
digest = hashlib.sha256(TRANSCRIPT.read_bytes()).hexdigest()
assert digest == "a1be4d9860c6199f81830850859dfd14d1542c103ab597e7dff72e430e905789"
assert len(value["runs"]) == 2
assert all(run["exitStatus"] == 0 and run["passLines"] == 117 and
           run["skipLines"] == 3 and run["failLines"] == 0 and
           run["transcriptSha256"] == digest for run in value["runs"])
lines = TRANSCRIPT.read_text().splitlines()
assert len(lines) == 140
assert sum("PASS" in line for line in lines) == 117
assert sum("SKIP" in line for line in lines) == 3
assert not any("FAIL" in line for line in lines)
for release in value["archivedValidatorsPassed"]:
    phase = release.removeprefix("0.0.0-phase")
    assert f"Phase {phase} exact archived pre-root envelope validation: PASS" in lines
assert [line.replace(": SKIP (", ": ").removesuffix(")") for line in lines if "SKIP" in line] == value["declaredSkips"]
print("Phase 5.48 offline checks twice: PASS")
