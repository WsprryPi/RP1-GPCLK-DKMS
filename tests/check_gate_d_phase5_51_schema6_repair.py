#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the committed Phase 5.51 permanent-executor repair evidence."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATTESTATION = ROOT / "docs/evidence/gate-d-phase5.51-permanent-executor-schema6-repair-attestation.json"
value = json.loads(ATTESTATION.read_text())
commit = value["repairCommit"]

for section, path_key, hash_key in (
    ("repair", "permanentExecutorPath", "permanentExecutorSha256"),
    ("regression", "path", "sha256"),
):
    relative = value[section][path_key]
    payload = subprocess.check_output(["git", "show", f"{commit}:{relative}"], cwd=ROOT)
    assert hashlib.sha256(payload).hexdigest() == value[section][hash_key]

executor = subprocess.check_output([
    "git", "show", f"{commit}:scripts/gate_d_outer.py"], cwd=ROOT).decode()
assert "instance_schema not in {3,4,5,6}" in executor
assert "{3:4,4:5,5:5,6:5}[instance_schema]" in executor
assert value["regression"]["installedExecutorSelectionPath"] == "passed"
assert value["regression"]["schema6Bootstrap"] == "passed"
assert value["regression"]["exactIndexedAttemptSchemaVersion"] == 2
assert value["regression"]["exactIndexedAttemptValidation"] == "passed"
assert set(value["regression"].values()) >= {"passed"}
assert set(value["validation"].values()) == {
    "passed", "e48b0cb3ce9e552688b84656445bf6760752f15fc5febdf3caeff39e310c8ada"}
assert value["scope"]["sourceFrozen"] is False
assert value["scope"]["targetConnected"] is False
assert value["result"]["blockerResolvedInCommittedBytes"] is True
assert value["result"]["eligibleForSeparateFreezeDecision"] is True
print("Phase 5.51 permanent-executor schema-6 repair: PASS")
