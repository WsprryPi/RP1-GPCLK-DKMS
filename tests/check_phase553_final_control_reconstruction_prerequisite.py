#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the final-control reconstruction prerequisite evidence."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
value = json.loads((ROOT / "docs/evidence/phase5.53-final-control-reconstruction-prerequisite.json").read_text())
assert value["kind"] == "phase5.53-final-control-reconstruction-prerequisite"
assert value["productArchiveSha256"] == "032a0ca214427ebb6115b933042e7135f03c2ed6ce4f5c399686b2cf61395a76"
assert value["qualificationSourceCommit"] == "9534590a4adedd8338c93c9bbfd6a48b7c8035c3"
assert value["qualificationArchiveSha256"] == "8d0ab952fa775f8f88ebdc529f173a995c15a97d20ee1546d74159602b2b3626"
assert value["generations"] == 2
assert value["byteIdentical"] is True
assert value["independentValidationsPassed"] == 2
assert value["productRetainedByteIdentical"] is True
assert value["consumer"]["installedPath"] == "/usr/libexec/rp1-gpclk-dkms/gate-d-same-version"
assert value["consumer"]["qualificationOnly"] is True
assert value["consumer"]["targetExecutionApproved"] is False
print("Phase 5.53 final-control reconstruction prerequisite: PASS")
