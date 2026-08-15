#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the exact, non-live Gate C representative-build decision."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
value = json.loads((ROOT / "release/gate-c-representative-build-manifest-v1.json").read_text())

assert set(value) == {
    "SPDX-License-Identifier", "schemaVersion", "kind", "candidate",
    "representativeSystem", "result", "evidence", "additionalBuilds",
    "claimBoundary",
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
additional = value["additionalBuilds"]
assert additional["summarySha256"] == hashlib.sha256(
    (ROOT / "docs/evidence/gate-c-wspr5-version-kernel-build-matrix-20260815.md").read_bytes()
).hexdigest()
results = additional["results"]
assert {(item["release"], item["kernelRelease"]) for item in results} == {
    ("0.0.0-phase5.2", "6.18.34+rpt-rpi-2712"),
    ("0.0.0-phase5.2", "6.12.75+rpt-rpi-2712"),
    ("0.0.0-phase5.13", "6.12.75+rpt-rpi-2712"),
}
assert all(item["exitStatus"] == 0 and item["diagnosticsCount"] == 0 and
           item["compatibilityState"] == "Compatible-unqualified" and
           item["liveEligible"] is False for item in results)

successor = json.loads((ROOT / "release/gate-c-representative-build-manifest-phase5.14-v1.json").read_text())
assert set(successor) == {
    "SPDX-License-Identifier", "schemaVersion", "kind", "candidate",
    "representativeSystem", "result", "evidence", "claimBoundary",
}
assert successor["candidate"] == {
    "release": "0.0.0-phase5.14",
    "sourceCommit": "7bbdfe1b5c83e1417e9dc5e0c4a7385136fd094a",
    "sourceArchiveSha256": "d0c17f2842716052bb49b1a4fc079d3d48a5674bae8610eee2ab9d17ac548bea",
    "uapiHeaderSha256": "1d411644352e61402bd4685a5692070d543ab2ee5b016d394294aa98970bd7fb",
}
assert successor["representativeSystem"]["kernelConfigSha256"] == \
    "2a83d4324e9b47d418b4efac18d3af43d15cc956b71c5a8eb074060bf8383801"
assert successor["result"]["moduleSha256"] == \
    "b41deafac7c5b49cafa9f13bbc4dba01585d5e013137c7e7015fb284a1990449"
assert successor["result"]["exitStatus"] == successor["result"]["diagnosticsCount"] == 0
assert successor["result"]["compatibilityState"] == "Compatible-unqualified"
assert successor["result"]["liveEligible"] is False
assert successor["evidence"]["cleanupComplete"] is True
assert successor["evidence"]["manifestSha256"] == \
    "8cb7a946676bf31a79419b8bf7c7550bf3ebb9a49b618f3bc94868ea3842e56b"
assert successor["claimBoundary"] == boundary

print("Gate C representative build: PASS")
