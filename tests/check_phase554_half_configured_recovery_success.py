#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
evidence = json.loads(
    (ROOT / "docs/evidence/phase5.54-half-configured-recovery-success.json").read_text()
)

assert evidence["installationAttempts"] == 1
assert evidence["package"] == {
    "version": "0.0.0~phase5.54-2",
    "status": "install ok installed",
    "dpkgAuditEmpty": True,
}
assert evidence["dkms"]["installedKernels"] == [
    "6.12.75+rpt-rpi-2712",
    "6.12.75+rpt-rpi-v8",
    "6.18.34+rpt-rpi-2712",
    "6.18.34+rpt-rpi-v8",
]
assert evidence["dkms"]["customKernelState"] == "absent-build-exclusive-skip"
hashes = evidence["installedHashes"]
assert hashes["canonicalGpio4Dtbo"] == hashes["bootGpio4Dtbo"]
assert hashes["canonicalGpio20Dtbo"] == hashes["bootGpio20Dtbo"]
assert evidence["inactiveState"] == {
    "moduleLoaded": False,
    "endpointPresent": False,
    "activeOverlayCount": 0,
    "bootSelectionCount": 0,
}
assert all(evidence["cleanup"].values())
assert not any(evidence["safety"].values())
assert evidence["result"] == "pass-stopped-before-lifecycle-attempt-1"

print("Phase 5.54 half-configured recovery success: PASS")
