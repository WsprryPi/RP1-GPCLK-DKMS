#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the sealed Phase 5.46 attempt-1 failure record."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
value = json.loads((ROOT / "docs/evidence/gate-d-phase5.46-attempt1-failure-attestation.json").read_text())
attempt = value["attempt"]
result = value["result"]
boundary = value["mutationBoundary"]
post = value["postState"]
recovery = value["recovery"]

assert value["authorizationCommit"] == "6b3dcc83c817e6c0011e6dde649b146df88abc91"
assert value["preRootEvidenceCommit"] == "74b9cd0abe2565ea9fa3a8795cc7b100995f3cb7"
assert attempt["indexEntry"] == 1
assert attempt["operationId"] == "gd-current-supported-kernel-gpio4"
assert result["status"] == "inactive-recovery-required"
assert result["failedStepId"] == "02-capture-preflight"
assert result["failureMessage"] == "symlink in controlled path: /proc/device-tree/rp1-gpclk"
assert result["liveOutput"] is False and result["sealed"] is True
assert boundary["completedOperations"] == ["create-evidence"]
assert not any(value for key, value in boundary.items() if key != "completedOperations")
assert not any(post[key] for key in (
    "moduleLoaded", "endpointPresent", "overlayActive",
    "candidateDkmsTestVersionPresent"))
assert post["allSixServicesInactive"] is True and post["outputDisabled"] is True
assert recovery == {
    "journalReportsRecoveryRequired": True,
    "sameOperationResumeAuthorized": False,
    "separatelyIndexedRecoveryOperationAvailable": False,
    "recoveryInvoked": False,
    "evidencePreserved": True,
}
print("Phase 5.46 attempt 1 sealed preflight failure: PASS")
