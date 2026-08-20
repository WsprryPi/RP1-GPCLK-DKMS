#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import copy
import importlib.util
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("lifecycle_policy", ROOT / "scripts/lifecycle_policy.py")
assert spec and spec.loader
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)

contract = json.loads((ROOT / "release/lifecycle-removal-contract-v1.json").read_text())
layout = json.loads((ROOT / "release/release-layout-v1.json").read_text())
assert contract["release"] == layout["release"]
assert set(contract["acceptanceFields"]) == set(policy.ABSENT_FIELDS + policy.TRUE_FIELDS)

clean = {field: False for field in policy.ABSENT_FIELDS}
clean.update({field: True for field in policy.TRUE_FIELDS})
result = policy.evaluate_complete_removal(clean)
assert result["accepted"] and result["repeatedRemovalSafe"] and result["readOnly"]
for field in clean:
    failed = copy.deepcopy(clean)
    failed[field] = not failed[field]
    result = policy.evaluate_complete_removal(failed)
    assert not result["accepted"] and field in result["failures"]
for malformed in ({}, {**clean, "unknown": False}, {**clean, "moduleLoaded": None}):
    try:
        policy.evaluate_complete_removal(malformed)
    except ValueError:
        pass
    else:
        raise AssertionError("incomplete, unknown, or indeterminate removal evidence accepted")

rollback = {"operation": "upgrade", "status": "inactive-failed", "liveOutput": False,
            "cleanupProven": True, "successorOwnershipKnown": True,
            "predecessorComplete": True, "rollbackTargetsUnchanged": True,
            "administratorBytesUnchanged": True, "predecessorRelease": "1.0.0",
            "successorRelease": "1.1.0"}
assert policy.rollback_plan(rollback)["to"] == "1.0.0"
for field in ("cleanupProven", "successorOwnershipKnown", "predecessorComplete",
              "rollbackTargetsUnchanged", "administratorBytesUnchanged"):
    bad = copy.deepcopy(rollback); bad[field] = False
    try:
        policy.rollback_plan(bad)
    except ValueError:
        pass
    else:
        raise AssertionError(f"rollback accepted failed assertion: {field}")
for bad_value in (True, None):
    bad = copy.deepcopy(rollback); bad["liveOutput"] = bad_value
    try:
        policy.rollback_plan(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("rollback accepted live or unknown output state")
same_release = {**rollback, "successorRelease": rollback["predecessorRelease"]}
try:
    policy.rollback_plan(same_release)
except ValueError:
    pass
else:
    raise AssertionError("same-release rollback accepted")

base_recovery = {"operation": "upgrade", "status": "inactive-recovery-required",
                 "checkpoint": "preflight", "liveOutput": False,
                 "ownershipKnown": True, "cleanupLatch": False,
                 "hardwareActivityAbsent": True}
for checkpoint in policy.CHECKPOINTS:
    state = {**base_recovery, "checkpoint": checkpoint}
    plan = policy.recovery_plan(state)
    assert plan["checkpoint"] == checkpoint and not plan["automatic"]
for field, value in (("ownershipKnown", False), ("cleanupLatch", True),
                     ("hardwareActivityAbsent", False), ("liveOutput", True)):
    bad = {**base_recovery, field: value}
    try:
        policy.recovery_plan(bad)
    except ValueError:
        pass
    else:
        raise AssertionError(f"unsafe recovery accepted: {field}")
for bad in ({**base_recovery, "checkpoint": "unknown"},
            {**base_recovery, "operation": "repair"},
            {**base_recovery, "extra": False}):
    try:
        policy.recovery_plan(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("unrecognized or expanded recovery accepted")

source = (ROOT / "scripts/lifecycle_policy.py").read_text()
for prohibited in ("subprocess", "os.system", "modprobe", "dtoverlay", "/dev/mem", "reboot"):
    assert prohibited not in source

print("Phase 5.9 lifecycle policy: PASS")
