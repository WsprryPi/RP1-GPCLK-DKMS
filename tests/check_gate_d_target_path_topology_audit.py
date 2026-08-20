#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the captured wspr5 target-path topology audit."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
value = json.loads((ROOT / "docs/evidence/gate-d-wspr5-target-path-topology-audit.json").read_text())
device_tree = value["deviceTree"]
assert value["host"] == "wspr5" and value["readOnly"] is True
assert device_tree == {
    "alias": "/proc/device-tree",
    "aliasType": "symlink",
    "aliasTarget": "/sys/firmware/devicetree/base",
    "canonicalRoot": "/sys/firmware/devicetree/base",
    "canonicalRootType": "directory",
    "canonicalRootOwner": "root:root",
    "canonicalRootMode": "0755",
    "resource": "/sys/firmware/devicetree/base/rp1-gpclk",
    "resourceState": "absent",
}
paths = {item["path"]: item["state"] for item in value["preflightPaths"]}
assert len(paths) == 11
assert set(paths.values()) <= {"direct", "absent"}
assert paths["/proc/cmdline"] == paths["/proc/sys/kernel/random/boot_id"] == "direct"
assert paths["/sys/module/rp1_gpclk_dkms"] == paths["/dev/rp1-gpclk"] == "absent"
assert value["result"] == {
    "onlyCanonicalAliasRequiresSpecialHandling": True,
    "genericControlledPathPolicyMayRemainStrict": True,
    "repairedResolverLiveTopologyCheck": "passed",
    "transientRepairScriptRemoved": True,
    "hardwareAccessed": False,
    "systemStateChanged": False,
}
print("Gate D wspr5 target-path topology audit: PASS")
