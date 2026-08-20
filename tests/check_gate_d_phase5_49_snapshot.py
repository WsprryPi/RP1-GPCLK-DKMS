#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the canonical Phase 5.49 predecessor snapshot."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEW = ROOT / "docs/evidence/gate-d-live-target-snapshot-wspr5-phase5.49-v1.json"
OLD = ROOT / "docs/evidence/gate-d-live-target-snapshot-wspr5-phase5.48-v1.json"
spec = importlib.util.spec_from_file_location(
    "snapshot_validator", ROOT / "scripts/gate_d_live_snapshot_validate.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)
new = json.loads(NEW.read_text())
old = json.loads(OLD.read_text())

result = validator.validate(new)
assert result == {
    "valid": True,
    "readOnly": True,
    "outputDisabled": True,
    "snapshotSha256": "3db85e0ada2427c997cdca878d0f2d53fc0c61d5aab68761e65a2a6cf349a6d5",
}
assert hashlib.sha256(NEW.read_bytes()).hexdigest() == result["snapshotSha256"]
assert new["administratorLedger"]["release"] == "0.0.0-phase5.48"
assert new["administratorLedger"]["sha256"] == \
    "bdc113ca499f920097affe3e31a96bc98b4cd10fdd23b85e8e59880bb6f40378"
assert new["terminalRecovery"]["sha256"] == \
    "b76bb27c57af55136042559be4bbc385d6e3498755d3bd39737800703963c514"
assert new["packagePathsSha256"] == \
    "a8675f7525158f84c57481de41d730ae0ce0f3ce40d16b884eefc2f7ae947824"
assert len(new["packagePaths"]) == 28
assert new["administratorLedger"] != old["administratorLedger"]
assert new["terminalRecovery"] != old["terminalRecovery"]
assert new["packagePaths"] != old["packagePaths"]
assert new["packagePathsSha256"] != old["packagePathsSha256"]
assert new["boot"] == old["boot"]
assert new["kernel"] == old["kernel"]
assert new["runtime"] == old["runtime"]
assert new["services"] == old["services"]
assert new["physicalSafety"] == old["physicalSafety"]
print("Phase 5.49 canonical live-target snapshot: PASS")
