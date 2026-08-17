#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the Phase 5.50 canonical snapshot and retained build inventory."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEW = ROOT / "docs/evidence/gate-d-live-target-snapshot-wspr5-phase5.50-v1.json"
OLD = ROOT / "docs/evidence/gate-d-live-target-snapshot-wspr5-phase5.49-v1.json"
RETAINED = ROOT / "docs/evidence/gate-d-retained-build-inventory-wspr5-phase5.50-v1.json"
BUILD = ROOT / "release/gate-c-representative-build-manifest-phase5.50-v1.json"
spec = importlib.util.spec_from_file_location(
    "snapshot_validator", ROOT / "scripts/gate_d_live_snapshot_validate.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

new = json.loads(NEW.read_text())
old = json.loads(OLD.read_text())
retained = json.loads(RETAINED.read_text())
build = json.loads(BUILD.read_text())
result = validator.validate(new)
assert result == {
    "valid": True,
    "readOnly": True,
    "outputDisabled": True,
    "snapshotSha256": "3db85e0ada2427c997cdca878d0f2d53fc0c61d5aab68761e65a2a6cf349a6d5",
}
assert NEW.read_bytes() == OLD.read_bytes()
assert new["administratorLedger"]["sha256"] == \
    "bdc113ca499f920097affe3e31a96bc98b4cd10fdd23b85e8e59880bb6f40378"
assert new["terminalRecovery"]["sha256"] == \
    "b76bb27c57af55136042559be4bbc385d6e3498755d3bd39737800703963c514"
assert new["packagePathsSha256"] == \
    "a8675f7525158f84c57481de41d730ae0ce0f3ce40d16b884eefc2f7ae947824"
assert len(new["packagePaths"]) == 28

assert hashlib.sha256(RETAINED.read_bytes()).hexdigest() == \
    "2be9caf90f9db8278d6423a870736064d6acce2ccd7fa796aad7c5c5f6db4a5d"
assert set(retained) == {
    "SPDX-License-Identifier", "schemaVersion", "kind", "host", "release",
    "sourceCommit", "basePath", "topLevel", "releaseArtifacts",
    "helperArtifacts", "extractedRoot", "treeFileCount", "treeSha256",
    "readOnly",
}
assert retained["SPDX-License-Identifier"] == "MIT"
assert retained["schemaVersion"] == 1
assert retained["kind"] == "gate-d-retained-representative-build-inventory"
assert retained["host"] == "wspr5" and retained["release"] == "0.0.0-phase5.50"
assert retained["sourceCommit"] == build["candidate"]["sourceCommit"]
assert retained["basePath"] == "/home/pi/gate-c-evidence/phase5.50-c241605"
assert retained["topLevel"] == ["bin", "extracted", "release"]
assert retained["extractedRoot"] == "rp1-gpclk-dkms-0.0.0-phase5.50"
assert retained["treeFileCount"] == 738
assert retained["treeSha256"] == \
    "acba4411c1d708ece449748c18114c587f62ae3838f66f1d5644856a60561e6c"
assert retained["readOnly"] is True
assert all(item["type"] == "file" and item["mode"] == "0644"
           for item in retained["releaseArtifacts"])
assert [(item["name"], item["sha256"]) for item in retained["releaseArtifacts"]] == \
       [(item["name"], item["sha256"]) for item in build["result"]["releaseInputs"]]
assert {item["name"]: item["sha256"] for item in retained["helperArtifacts"]} == {
    "gate-d-busy-injector": build["result"]["busyInjectorSha256"],
    "gate-d-uapi-probe": build["result"]["uapiProbeSha256"],
}
print("Phase 5.50 canonical snapshot and retained build inventory: PASS")
