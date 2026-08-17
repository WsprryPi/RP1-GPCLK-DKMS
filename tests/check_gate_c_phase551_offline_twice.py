#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate exact-freeze Phase 5.51 offline-checks-twice evidence."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidence/gate-c-phase5.51-offline-checks-twice.json"
TRANSCRIPT = ROOT / "docs/evidence/gate-c-phase5.51-offline-checks-twice-transcript.txt"
value = json.loads(EVIDENCE.read_text())
assert value["release"] == "0.0.0-phase5.51"
assert value["sourceCommit"] == "cc87e0cdec7195eb69de2a6606f388e23ee0799c"
assert value["worktreeState"] == "clean-detached-exact-commit"
assert value["archivedReleaseInputs"] == [
    {"release":"0.0.0-phase5.43","sha256":"a8a200d069ad433353a8812ef6a9a4c585b75a9f6af3d6501ac3672e90c997c3"},
    {"release":"0.0.0-phase5.45","sha256":"21d05675e9d12ddb4c051868578c410737b733786357cee20eb2b0ce03f63356"},
    {"release":"0.0.0-phase5.46","sha256":"0e0debdd96560602bd61457afc59782cfad2a4fb1b6f9b54e0d2505453e6c8f2"},
    {"release":"0.0.0-phase5.47","sha256":"497368ac11b32e5491dab76103ad3bb2da0975c086e9898a801c5c2df1be82be"},
    {"release":"0.0.0-phase5.48","sha256":"18418395eac577d8718c1e74f6601e005160d2768ea7634a35d00e4ddead9120"},
    {"release":"0.0.0-phase5.50","sha256":"ef989bf79faa5c30ddaf8ac5651d75b1755ba2fa385680692183e6145b2927c2"},
]
digest = hashlib.sha256(TRANSCRIPT.read_bytes()).hexdigest()
assert digest == "00ff8e08ead66e0bbf3664fb8c84827666a8ba526182f984179e3620ea11d44b"
assert value["transcriptsByteIdentical"] is True and value["result"] == "passed"
assert len(value["runs"]) == 2
assert all(run["exitStatus"] == 0 and run["passLines"] == 144 and run["skipLines"] == 3 and
           run["failLines"] == 0 and run["transcriptSha256"] == digest for run in value["runs"])
lines = TRANSCRIPT.read_text().splitlines()
assert len(lines) == 180 and sum("PASS" in line for line in lines) == 144
assert sum("SKIP" in line for line in lines) == 3 and not any("FAIL" in line for line in lines)
for release in value["archivedValidatorsPassed"]:
    phase = release.removeprefix("0.0.0-phase")
    label = "pre-root envelope" if phase != "5.50" else "control-set"
    assert f"Phase {phase} exact archived {label} validation: PASS" in lines
assert [line.replace(": SKIP (", ": ").removesuffix(")") for line in lines if "SKIP" in line] == value["declaredSkips"]
assert value["representativeBuildValidator"] == {"commit":"7e61c9e3359916481dda744175fa57b9f0a10733","result":"passed","execution":"independent-after-frozen-runs"}
assert value["rejectedRuns"]["count"] == 2
print("Phase 5.51 offline checks twice: PASS")
