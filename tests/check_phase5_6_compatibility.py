#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import importlib.util
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("compatibility_policy", ROOT / "scripts/compatibility_policy.py")
assert spec and spec.loader
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)
decisions = json.loads((ROOT / "release/compatibility-decisions-v1.json").read_text())
schema = json.loads((ROOT / "schema/rp1-gpclk-compatibility-manifest-v1.schema.json").read_text())
entries = decisions["entries"]
assert len(entries) == 2 and len({entry["id"] for entry in entries}) == 2
assert {entry["route"] for entry in entries} == {"GPIO4", "GPIO20"}
gpio4 = next(entry for entry in entries if entry["route"] == "GPIO4")
gpio20 = next(entry for entry in entries if entry["route"] == "GPIO20")
required_modes = {"QRSS", "FSKCW", "DFCW", "WSPR"}
for entry in entries:
    assert set(entry) == set(schema["$defs"]["entry"]["required"])
    assert set(entry["build"]) == set(schema["$defs"]["buildIdentity"]["required"])
    assert set(entry["build"]["kernelConfig"]) == set(schema["$defs"]["kernelConfig"]["required"])
    assert set(entry["build"]["signature"]) == set(schema["$defs"]["signature"]["required"])
    assert set(entry["runtime"]) == set(schema["$defs"]["runtimeIdentity"]["required"])
    assert set(entry["overlay"]) == set(schema["$defs"]["overlay"]["required"])
    assert entry["supportedDriveMa"] == 2 and set(entry["supportedModes"]) == required_modes
    for digest in (entry["uapiHeaderSha256"], entry["build"]["kernelConfig"]["sha256"],
                   entry["build"]["moduleUnsignedSha256"], entry["build"]["moduleInstalledSha256"],
                   entry["runtime"]["baseDtSha256"], entry["overlay"]["sourceSha256"],
                   entry["overlay"]["dtboSha256"]):
        assert len(digest) == 64 and set(digest) <= set("0123456789abcdef")
    assert entry["evidence"]
    for item in entry["evidence"]:
        assert set(item) == set(schema["$defs"]["evidence"]["required"])
        assert len(item["sha256"]) == 64 and set(item["sha256"]) <= set("0123456789abcdef")
    assert all(entry["route"] in item["routes"] and required_modes <= set(item["modes"])
               for item in entry["evidence"])

assert gpio4["id"] == "v1.0.1-wspr5-gpio4-6.18.34"
assert gpio4["state"] == "Experimental" and gpio4["liveEligible"]
assert gpio4["build"]["moduleVersion"] == "1.0.1"
assert gpio4["build"]["kernelRelease"] == "6.18.34+rpt-rpi-2712"
assert gpio4["build"]["architecture"] == "arm64"
assert gpio4["build"]["runtimeArchitecture"] == "aarch64"
assert gpio4["runtime"]["piModel"] == "Raspberry Pi 5 Model B Rev 1.0"
assert gpio20["state"] == "Unavailable" and not gpio20["liveEligible"]
assert gpio20["build"]["moduleVersion"] == "0.0.0-phase4d-combined"
assert sum(entry["liveEligible"] for entry in entries) == 1

qualified = {"state": "Qualified", "liveEligible": True, "reason": "exact evidence"}
experimental = {"state": "Experimental", "liveEligible": True, "reason": "enrolled"}
result = policy.evaluate_update(qualified, "identical-rebuild", identity_identical=True,
                                manifest_preserves_state=True)
assert result["state"] == "Qualified" and result["liveEligible"]
for kwargs in ({}, {"identity_identical": True}, {"manifest_preserves_state": True}):
    result = policy.evaluate_update(qualified, "identical-rebuild", **kwargs)
    assert result["state"] == "Compatible-unqualified" and not result["liveEligible"]
result = policy.evaluate_update(qualified, "new-kernel-build-success")
assert result["state"] == "Compatible-unqualified" and not result["liveEligible"]
for event in ("dkms-build-failure", "signing-failure", "module-identity-mismatch",
              "overlay-identity-mismatch", "manifest-missing-or-malformed"):
    result = policy.evaluate_update(qualified, event)
    assert result["state"] == "Unavailable" and not result["allowLoad"] and not result["fallbackAllowed"]
assert policy.evaluate_update(qualified, "dkms-build-failure")["priorInstallation"] == "retain-bootable"
latched = policy.evaluate_update(qualified, "cleanup-failure-latched")
assert latched["state"] == "Rejected" and latched["recoveryRequired"]
recovered = policy.evaluate_update({"state": "Rejected", "liveEligible": False, "reason": "latched"},
                                   "explicit-recovery-success")
assert recovered["state"] == "Unavailable" and not recovered["liveEligible"]
stale = policy.evaluate_update(experimental, "experimental-enrollment-stale")
assert stale["state"] == "Experimental" and not stale["liveEligible"]
preserved = policy.evaluate_update(experimental, "identical-rebuild", identity_identical=True,
                                   manifest_preserves_state=True, enrollment_current=False)
assert preserved["state"] == "Experimental" and not preserved["liveEligible"]
unavailable = {"state": "Unavailable", "liveEligible": False, "reason": "missing"}
preserved_unavailable = policy.evaluate_update(unavailable, "identical-rebuild",
                                               identity_identical=True, manifest_preserves_state=True)
assert not preserved_unavailable["allowLoad"] and not preserved_unavailable["allowBind"]
for bad in ({}, {"state": "Qualified", "liveEligible": True, "reason": "x", "extra": True}):
    try:
        policy.evaluate_update(bad, "new-kernel-build-success")
    except ValueError:
        pass
    else:
        raise AssertionError("malformed prior decision accepted")
for impossible in ({"state": "Qualified", "liveEligible": False, "reason": "x"},
                   {"state": "Rejected", "liveEligible": True, "reason": "x"}):
    try:
        policy.evaluate_update(impossible, "new-kernel-build-success")
    except ValueError:
        pass
    else:
        raise AssertionError("impossible prior state/live combination accepted")
print("Phase 5.6 compatibility and update policy: PASS")
