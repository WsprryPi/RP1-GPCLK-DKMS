#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the single-Pi Gate D execution policy and route decision."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROWS = [
    "current-supported-kernel", "prior-supported-kernel-downgrade",
    "newer-unknown-kernel", "signing-not-enforced",
    "signing-enforced-enrolled-key", "deliberate-build-failure",
    "deliberate-signature-rejection", "missing-headers",
    "overlay-or-resource-conflict", "interrupted-upgrade", "stale-manifest",
    "corrupted-archive-or-dtbo", "removal-inactive",
    "removal-open-or-active", "reinstall-after-removal",
]
DEFERRED = {
    "newer-unknown-kernel", "signing-enforced-enrolled-key",
    "deliberate-signature-rejection", "missing-headers",
    "overlay-or-resource-conflict",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


policy_path = ROOT / "release/gate-d-matrix-policy-v2.json"
route_path = ROOT / "release/gate-d-route-compatibility-decision-v1.json"
instance = json.loads((ROOT / "release/gate-d-execution-instance-v1.json").read_text())
policy = json.loads(policy_path.read_text())
route = json.loads(route_path.read_text())

assert policy["schemaVersion"] == 2
assert policy["kind"] == "gate-d-matrix-execution-policy"
assert [row["id"] for row in policy["rows"]] == ROWS
classifications = {row["id"]: row["classification"] for row in policy["rows"]}
assert {row for row, value in classifications.items()
        if value == "deferred-environmental"} == DEFERRED
assert set(classifications.values()) == {"required-executable", "deferred-environmental"}
assert "never satisfy" in policy["simulationRule"]
assert "All fifteen" in policy["qualificationRule"]

assert route["kind"] == "gate-d-route-compatibility-decision"
assert {entry["route"] for entry in route["routes"]} == {"GPIO4", "GPIO20"}
assert all(entry["state"] == "Unavailable" and entry["liveEligible"] is False
           for entry in route["routes"])
boundary = route["decisionBoundary"]
assert boundary == {
    "routeSpecific": True,
    "outputDisabled": True,
    "positiveReleaseManifestEntryEstablished": False,
    "installationOrBindingAuthorized": False,
    "readOnlyTargetIdentityRefreshRequired": True,
}
assert route["candidate"]["representativeBuildManifestSha256"] == digest(
    ROOT / "release/gate-c-representative-build-manifest-v1.json")
assert instance["executionPolicy"]["matrixPolicySha256"] == digest(policy_path)
assert instance["executionPolicy"]["routeDecisionSha256"] == digest(route_path)

print("Gate D matrix execution policy: PASS")
