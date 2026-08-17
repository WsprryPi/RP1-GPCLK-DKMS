#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the exact-freeze Phase 5.45 offline-checks-twice evidence."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidence/gate-c-phase5.45-offline-checks-twice.json"
TRANSCRIPT = ROOT / "docs/evidence/gate-c-phase5.45-offline-checks-twice-transcript.txt"

value = json.loads(EVIDENCE.read_text())
assert value["sourceCommit"] == "4b50db7868b7fe5ca9d830f51cd404c250192188"
assert value["worktreeState"] == "clean-detached-exact-commit"
assert value["archivedPhase543ArchiveSha256"] == \
    "a8a200d069ad433353a8812ef6a9a4c585b75a9f6af3d6501ac3672e90c997c3"
assert value["transcriptsByteIdentical"] is True
assert value["result"] == "passed"
runs = value["runs"]
assert len(runs) == 2
transcript_hash = hashlib.sha256(TRANSCRIPT.read_bytes()).hexdigest()
assert transcript_hash == \
    "5b777fe49c70a3e736bc7271eed361f9841311fe6cfd2fdf4a034bb631030c5b"
assert all(run["exitStatus"] == 0 and run["passLines"] == 87 and
           run["skipLines"] == 3 and run["failLines"] == 0 and
           run["transcriptSha256"] == transcript_hash for run in runs)
lines = TRANSCRIPT.read_text().splitlines()
assert len(lines) == 92
assert sum("PASS" in line for line in lines) == 87
assert sum("SKIP" in line for line in lines) == 3
assert not any("FAIL" in line for line in lines)

print("Phase 5.45 offline checks twice: PASS")
