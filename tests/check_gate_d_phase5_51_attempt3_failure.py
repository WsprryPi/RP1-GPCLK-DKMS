#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the sealed Phase 5.51 attempt-3 preflight failure."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
prompt = (ROOT / "docs/contracts/gate-d-phase5.51-attempt3-prior-kernel-downgrade-gpio4-prompt.md").read_text()
value = json.loads((ROOT / "docs/evidence/gate-d-phase5.51-attempt3-prior-kernel-downgrade-gpio4-failure-attestation.json").read_text())
attempt = value["attempt"]
result = value["result"]
boundary = value["mutationBoundary"]
post = value["postState"]

assert "/usr/libexec/rp1-gpclk-dkms/gate-d-executor" in prompt
assert "--resume --execute" in prompt
assert "6.12.75+rpt-rpi-2712" in prompt and "6.18.34+rpt-rpi-2712" in prompt
assert attempt == {
    "indexEntry": 3,
    "operationId": "gd-prior-supported-kernel-downgrade-gpio4",
    "documentSha256": "e4002b4b21f2fdbacfbdc4d7180b0b037bae6344e17ef3148edd5680af0f4fe7",
    "indexSha256": "a1d547226090dbcb58375774983ebe7a0fa3cd05e30963b58d7dc2e5524f2960",
    "executorPath": "/usr/libexec/rp1-gpclk-dkms/gate-d-executor",
    "executorSha256": "33b5cb5ec1e50e7f2206873fe537a7d34e3237d6157d54f4cafebece5d84cd01",
}
assert result["status"] == "inactive-recovery-required"
assert result["failedStepId"] == "02-capture-preflight"
assert result["failureMessage"] == "running kernel differs from attempt"
assert result["liveOutput"] is False and result["sealed"] is True
assert boundary["completedOperations"] == ["create-evidence"]
assert not any(item for key, item in boundary.items() if key != "completedOperations")
assert not any(post[key] for key in (
    "moduleLoaded", "endpointPresent", "overlayActive",
    "candidateDkmsTestVersionPresent", "predecessorDkmsTestVersionPresent"))
assert post["attemptStagingAbsent"] is True
assert post["allSixServicesInactive"] is True and post["outputDisabled"] is True
assert value["recovery"] == {
    "journalReportsRecoveryRequired": True,
    "sameOperationResumeAuthorized": False,
    "recoveryInvoked": False,
    "evidencePreserved": True,
}
print("Phase 5.51 attempt 3 sealed prior-kernel preflight failure: PASS")
