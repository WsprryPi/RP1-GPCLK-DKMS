#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the exact, non-live Gate C representative-build decision."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
value = json.loads((ROOT / "release/gate-c-representative-build-manifest-v1.json").read_text())

assert set(value) == {
    "SPDX-License-Identifier", "schemaVersion", "kind", "candidate",
    "representativeSystem", "result", "evidence", "claimBoundary",
}
assert value["SPDX-License-Identifier"] == "MIT"
assert value["schemaVersion"] == 1
assert value["kind"] == "gate-c-representative-build-manifest"
assert value["candidate"] == {
    "release": "0.0.0-phase5.13",
    "sourceCommit": "61ee2ea592c2551eca56fd0566fef43097b8c682",
    "sourceArchiveSha256": "58cb12864b291380fefd31ea9a203f7ee308767790787e3fce0be352dab19b14",
    "uapiHeaderSha256": "1d411644352e61402bd4685a5692070d543ab2ee5b016d394294aa98970bd7fb",
}
assert value["representativeSystem"]["host"] == "wspr5"
assert value["representativeSystem"]["kernelRelease"] == "6.18.34+rpt-rpi-2712"
assert value["result"]["exitStatus"] == 0
assert value["result"]["compatibilityState"] == "Compatible-unqualified"
assert value["result"]["liveEligible"] is False
assert value["result"]["diagnosticsCount"] == 0
boundary = value["claimBoundary"]
assert boundary["routeNeutralBuildOnly"] is True
assert boundary["satisfiesRouteSpecificCompatibilityEntry"] is False
assert boundary["satisfiesGateDRepresentativeLifecycleRow"] is False
assert all(boundary[key] is False for key in (
    "dkmsRegistered", "installed", "signed", "loaded", "bound",
    "clockDisabledTargetLifecycleExecuted", "gpioClockDmaTransmissionOrRfActivity",
))
assert value["evidence"]["cleanupComplete"] is True
assert value["evidence"]["moduleLoaded"] is False
assert value["evidence"]["driverBound"] is False

print("Gate C representative build: PASS")
