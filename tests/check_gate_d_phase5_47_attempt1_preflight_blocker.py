#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the Phase 5.47 attempt-1 service-prestate blocker."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
value = json.loads((ROOT / "docs/evidence/gate-d-phase5.47-attempt1-preflight-blocker-attestation.json").read_text())
snapshot = json.loads((ROOT / "docs/evidence/gate-d-live-target-snapshot-wspr5-phase5.47-v1.json").read_text())
attempt = json.loads((ROOT / "release/gate-d-attempts-phase5.47-v1/gd-current-supported-kernel-gpio4.json").read_text())

assert value["preflight"]["safeToInvokeAttempt"] is False
assert value["preflight"]["attemptEvidenceAbsent"] is True
assert value["result"] == {
    "classification": "sealed-control-set-service-prestate-conflict",
    "executorInvoked": False,
    "attemptEvidenceCreated": False,
    "serviceMutationPerformed": False,
    "lifecycleAttempt2Started": False,
    "outputDisabled": True,
}
required = {item["name"]: item["requiredPreState"] for item in attempt["services"]}
conflicts = value["serviceContractConflicts"]
assert set(conflicts) == {"wsprrypi", "sdrplay", "SoapySDRServer"}
for name, conflict in conflicts.items():
    assert snapshot["services"][name + ".service"] == "inactive"
    assert required[name] == "active"
    assert conflict == {
        "canonicalSnapshot": "inactive",
        "live": "inactive",
        "attemptRequired": "active",
    }
post = value["postState"]
assert post["allSixServicesInactive"] and post["outputDisabled"]
assert not any(post[key] for key in (
    "moduleLoaded", "endpointPresent", "overlayActive",
    "candidateDkmsTestVersionPresent",
))
print("Phase 5.47 attempt 1 service-prestate blocker: PASS")
