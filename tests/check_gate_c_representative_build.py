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

phase515 = json.loads((ROOT / "release/gate-c-representative-build-manifest-phase5.15-v1.json").read_text())
assert phase515["candidate"]["release"] == "0.0.0-phase5.15"
assert phase515["candidate"]["sourceCommit"] == "123a94c46a2fb068a5e83c42b440f6b8a07545f6"
assert phase515["candidate"]["sourceArchiveSha256"] == \
    "6a767723a9cbbf32b68d95c67221b0a56430a037508254aa8c3a65a9cd1bbb24"
assert phase515["result"]["moduleSha256"] == \
    "e692b0973fd7a39894c17f3d743d6fea387305b6828fe57485fcd8331105e6af"
assert phase515["result"]["exitStatus"] == phase515["result"]["diagnosticsCount"] == 0
assert phase515["result"]["compatibilityState"] == "Compatible-unqualified"
assert phase515["result"]["liveEligible"] is False
assert phase515["evidence"]["manifestSha256"] == \
    "711b2e4142a4457b29f052140b03bd156af2b92796cd4329e2041919f2cf6fdf"
assert phase515["claimBoundary"] == boundary

phase521 = json.loads((ROOT / "release/gate-c-representative-build-manifest-phase5.21-v1.json").read_text())
assert phase521["candidate"] == {
    "release": "0.0.0-phase5.21",
    "sourceCommit": "d0046092dfa9ffa0c58171ddcb52b7819cc50fc6",
    "sourceArchiveSha256": "fc5828d91446843d8ea78a09691c973d74082bea7655b6c0547a06d35fba1624",
    "uapiHeaderSha256": "1d411644352e61402bd4685a5692070d543ab2ee5b016d394294aa98970bd7fb",
}
assert phase521["representativeSystem"]["kernelRelease"] == "6.18.34+rpt-rpi-2712"
assert phase521["result"]["moduleSha256"] == \
    "8f533495f1b4f9404d346237c2f41cb4c88f7552ee1a40472f4aa058fd028ade"
assert phase521["result"]["exitStatus"] == phase521["result"]["diagnosticsCount"] == 0
assert phase521["result"]["compatibilityState"] == "Compatible-unqualified"
assert phase521["result"]["liveEligible"] is False
assert phase521["evidence"]["manifestSha256"] == \
    "1a9d86f973de58f3af47ee6877d1d5579786e2e8f46c74ed1931b17d9c939305"
assert phase521["evidence"]["cleanupComplete"] is True
assert phase521["evidence"]["helpersExecuted"] is False
assert phase521["claimBoundary"] == boundary

phase522 = json.loads((ROOT / "release/gate-c-representative-build-manifest-phase5.22-v1.json").read_text())
assert phase522["candidate"] == {
    "release": "0.0.0-phase5.22",
    "sourceCommit": "f7ddea06a68dedceb57aeec0ddedb67598a797e1",
    "sourceArchiveSha256": "2601cadb4f2abe25b72c7ed3237c00307bbcc11a8ed671331fef677089f93be9",
    "uapiHeaderSha256": "1d411644352e61402bd4685a5692070d543ab2ee5b016d394294aa98970bd7fb",
}
assert phase522["representativeSystem"]["kernelRelease"] == "6.18.34+rpt-rpi-2712"
assert phase522["result"]["moduleSha256"] == \
    "c4b9a04f3914a738fd3854354d42eb64f5b8c498ec7b7092a1cb68fe73c1c809"
assert phase522["result"]["exitStatus"] == phase522["result"]["diagnosticsCount"] == 0
assert phase522["result"]["compatibilityState"] == "Compatible-unqualified"
assert phase522["result"]["liveEligible"] is False
assert phase522["evidence"]["manifestSha256"] == \
    "abe852382d01a321df5f74b36979a00b29b6e8863e3f68457a3f22ae00d3197a"
assert phase522["evidence"]["cleanupComplete"] is True
assert phase522["evidence"]["helpersExecuted"] is False
assert phase522["evidence"]["evidenceSealResumed"] is True
assert phase522["evidence"]["buildRepeated"] is False
assert phase522["claimBoundary"] == boundary

phase523 = json.loads((ROOT / "release/gate-c-representative-build-manifest-phase5.23-v1.json").read_text())
assert phase523["candidate"]["sourceCommit"] == "61ec2032542ac3aea2f51feac904d5450cc17655"
assert phase523["candidate"]["sourceArchiveSha256"] == \
    "04b6f7aee8f19c3f0da9b0d8f6a53f8f68dcaaae464b5cf99b847b587415aa8c"
assert phase523["representativeSystem"]["kernelRelease"] == "6.18.34+rpt-rpi-2712"
assert phase523["result"]["moduleSha256"] == \
    "44fba1121952e4874fcf5814cce721cc3a66d7e199ea1e0cce711c0887f489a3"
assert phase523["result"]["exitStatus"] == phase523["result"]["diagnosticsCount"] == 0
assert phase523["result"]["compatibilityState"] == "Compatible-unqualified"
assert phase523["result"]["liveEligible"] is False
assert phase523["evidence"]["manifestSha256"] == \
    "bed0238f9f46d0e2a64bd70250d47f7fbc407f326ab1d2c106ed6e56764dc5eb"
assert phase523["evidence"]["cleanupComplete"] is True
assert phase523["evidence"]["helpersExecuted"] is False
assert phase523["claimBoundary"] == boundary

phase524 = json.loads((ROOT / "release/gate-c-representative-build-manifest-phase5.24-v1.json").read_text())
assert phase524["candidate"]["sourceCommit"] == "2a6ddeb8e0f7d31a26bbe4ebdc4bc0458a41c8c5"
assert phase524["candidate"]["sourceArchiveSha256"] == \
    "0da181f1ccfa9fb9edbd34456cec95730be8922283d1c5b207af376491413d8a"
assert phase524["representativeSystem"]["kernelRelease"] == "6.18.34+rpt-rpi-2712"
assert phase524["result"]["moduleSha256"] == \
    "0f3a2de824d689a7cde95d43ead1006b5e1ca40506fb33baadea3c605b0a826d"
assert phase524["result"]["exitStatus"] == phase524["result"]["diagnosticsCount"] == 0
assert phase524["result"]["compatibilityState"] == "Compatible-unqualified"
assert phase524["result"]["liveEligible"] is False
assert phase524["evidence"]["manifestSha256"] == \
    "92ab327e22d3d18042d9e4be255a7e56e62fbec6228abe3db0ade5001d02de53"
assert phase524["evidence"]["cleanupComplete"] is True
assert phase524["evidence"]["helpersExecuted"] is False
assert phase524["claimBoundary"] == boundary

phase525 = json.loads((ROOT / "release/gate-c-representative-build-manifest-phase5.25-v1.json").read_text())
assert phase525["candidate"]["sourceCommit"] == "d9f8fd8b17f1c2ee9324704c6b6630dfccfb5e4e"
assert phase525["candidate"]["sourceArchiveSha256"] == \
    "e615750897009b79d0ead1e3bbf4133e0c4d5c157cc259d513a76ad65bd993e4"
assert phase525["representativeSystem"]["kernelRelease"] == "6.18.34+rpt-rpi-2712"
assert phase525["result"]["moduleSha256"] == \
    "556129fcd35cf0f64f8e5cd22dd2af932c83ecc1ff43fe3b940a81c667667398"
assert phase525["result"]["exitStatus"] == phase525["result"]["diagnosticsCount"] == 0
assert phase525["result"]["compatibilityState"] == "Compatible-unqualified"
assert phase525["result"]["liveEligible"] is False
assert phase525["evidence"]["manifestSha256"] == \
    "79168bfa7978b5e2e69097a5bbe5397627b193185ddb85c86ce56899f37f6857"
assert phase525["evidence"]["cleanupComplete"] is True
assert phase525["evidence"]["helpersExecuted"] is False
assert phase525["claimBoundary"] == boundary

print("Gate C representative build: PASS")
