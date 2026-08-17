#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the Phase 5.51 canonical live-target predecessor snapshot."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEW = ROOT / "docs/evidence/gate-d-live-target-snapshot-wspr5-phase5.51-v1.json"
OLD = ROOT / "docs/evidence/gate-d-live-target-snapshot-wspr5-phase5.50-v1.json"
spec = importlib.util.spec_from_file_location("validator", ROOT / "scripts/gate_d_live_snapshot_validate.py")
validator = importlib.util.module_from_spec(spec); spec.loader.exec_module(validator)
new = json.loads(NEW.read_text()); old = json.loads(OLD.read_text())
assert validator.validate(new) == {"valid":True,"readOnly":True,"outputDisabled":True,
    "snapshotSha256":"badb3633cdf6bacce6fa3292174d3cea993a1ed4f0278f75c597bd204ee63e9a"}
assert new["administratorLedger"]["release"] == "0.0.0-phase5.50"
assert new["administratorLedger"]["sha256"] == "3877dece6b50b866246d3fc01bdc8c9aa036e5876f87d84d37557954c4d14fc2"
assert new["packagePathsSha256"] == "0abef11659eefaa805ad0459ac962c220d7cc3195537ad617eee553ca31efd53"
assert new["terminalRecovery"] == old["terminalRecovery"]
assert new["boot"] == old["boot"] and new["kernel"] == old["kernel"]
assert new["runtime"] == old["runtime"] and new["services"] == old["services"]
assert new["physicalSafety"] == old["physicalSafety"]
before = {item["path"]: item for item in old["packagePaths"]}
after = {item["path"]: item for item in new["packagePaths"]}
assert before.keys() == after.keys() and len(after) == 28
changed = {path for path in after if before[path] != after[path]}
assert changed == {
    "/usr/libexec/rp1-gpclk-dkms/gate-d-attempts", "/usr/libexec/rp1-gpclk-dkms/gate-d-executor",
    "/usr/libexec/rp1-gpclk-dkms/gate-d-instance", "/usr/libexec/rp1-gpclk-dkms/gate_d_attempts.py",
    "/usr/libexec/rp1-gpclk-dkms/gate_d_instance.py", "/usr/libexec/rp1-gpclk-dkms/gate_d_outer.py",
    "/usr/libexec/rp1-gpclk-dkms/rp1-gpclk-admin", "/usr/libexec/rp1-gpclk-dkms/rp1-gpclk-diagnostics"}
assert hashlib.sha256(NEW.read_bytes()).hexdigest() == "badb3633cdf6bacce6fa3292174d3cea993a1ed4f0278f75c597bd204ee63e9a"
print("Phase 5.51 canonical live-target snapshot: PASS")
