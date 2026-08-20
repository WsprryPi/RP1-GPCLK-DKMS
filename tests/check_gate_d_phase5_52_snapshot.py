#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the Phase 5.52 canonical live-target predecessor snapshot."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEW = ROOT / "docs/evidence/gate-d-live-target-snapshot-wspr5-phase5.52-v1.json"
OLD = ROOT / "docs/evidence/gate-d-live-target-snapshot-wspr5-phase5.51-v1.json"
spec = importlib.util.spec_from_file_location("validator", ROOT / "scripts/gate_d_live_snapshot_validate.py")
validator = importlib.util.module_from_spec(spec); spec.loader.exec_module(validator)
new = json.loads(NEW.read_text()); old = json.loads(OLD.read_text())
assert validator.validate(new) == {"valid":True,"readOnly":True,"outputDisabled":True,
    "snapshotSha256":"449201a0a51ca8b278b7ae077410e515aa9c176eac42f4ba86bd62ef4c36451f"}
assert new["administratorLedger"]["release"] == "0.0.0-phase5.51"
assert new["administratorLedger"]["sha256"] == "9683e2cb97f6d302bdcab74ec2a33748581302fc2023f178b7511edf437c884a"
assert new["packagePathsSha256"] == "e121ffbfe6d3e54f3433c8ee1a102965dfecc2d423e62d8b110e76b96cdaca32"
assert new["terminalRecovery"]["path"].endswith(
    "/phase5.51-cc87e0cdec71/current-supported-kernel/gd-current-supported-kernel-gpio20/transaction.json")
assert new["terminalRecovery"]["sha256"] == \
    "fbc9657f9d3f825a8893a8449f112b4f25b0029c27f411d2bbc64db383ca6f98"
assert new["boot"] == old["boot"] and new["kernel"] == old["kernel"]
assert new["runtime"] == old["runtime"] and new["services"] == old["services"]
assert new["physicalSafety"] == old["physicalSafety"]
before = {item["path"]: item for item in old["packagePaths"]}
after = {item["path"]: item for item in new["packagePaths"]}
assert before.keys() == after.keys() and len(after) == 28
changed = {path for path in after if before[path] != after[path]}
assert changed == {
    "/usr/libexec/rp1-gpclk-dkms/gate-d-attempts", "/usr/libexec/rp1-gpclk-dkms/gate-d-executor",
    "/usr/libexec/rp1-gpclk-dkms/gate_d_attempts.py", "/usr/libexec/rp1-gpclk-dkms/gate_d_outer.py",
    "/usr/libexec/rp1-gpclk-dkms/rp1-gpclk-admin", "/usr/libexec/rp1-gpclk-dkms/rp1-gpclk-diagnostics"}
assert hashlib.sha256(NEW.read_bytes()).hexdigest() == "449201a0a51ca8b278b7ae077410e515aa9c176eac42f4ba86bd62ef4c36451f"
print("Phase 5.52 canonical live-target snapshot: PASS")
