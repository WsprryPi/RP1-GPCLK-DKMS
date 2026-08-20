#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate Phase 5.51 attempt 1 and prevent executor/path regressions."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
prompt = (ROOT / "docs/contracts/gate-d-phase5.51-attempt1-current-kernel-gpio4-prompt.md").read_text()
value = json.loads((ROOT / "docs/evidence/gate-d-phase5.51-attempt1-current-kernel-gpio4-attestation.json").read_text())

permanent = "/usr/libexec/rp1-gpclk-dkms/gate-d-executor"
archived = ("/home/pi/gate-d-inputs/phase5.51-cc87e0cdec71/extracted/"
            "rp1-gpclk-dkms-0.0.0-phase5.51/scripts/gate_d_outer.py")
assert permanent in prompt and archived in prompt
assert "SourceFileLoader" in prompt
assert "do not import from, modify, remove" in prompt
assert value["attempt"] == {
    "ordinal": 1,
    "operationId": "gd-current-supported-kernel-gpio4",
    "documentSha256": "43ff27cb2034f42fa5e981bc4f8288a7e0e466c50a1d45134b7b0a5bb51660ba",
    "indexSha256": "a1d547226090dbcb58375774983ebe7a0fa3cd05e30963b58d7dc2e5524f2960",
    "executorPath": permanent,
    "executorSha256": "33b5cb5ec1e50e7f2206873fe537a7d34e3237d6157d54f4cafebece5d84cd01",
}
assert value["preflight"]["installedExecutorCliValidation"] == "passed"
assert value["preflight"]["installedExecutorCliPlan"] == "passed"
assert value["preflight"]["phase551ForbiddenPathCount"] == 0
assert value["preflight"]["historicalNamespacesExcludedFromMutation"] is True
assert value["result"] == {
    "status": "complete",
    "sealed": True,
    "recoveryRequired": False,
    "recordCount": 20,
    "nextStep": 20,
    "completedUtc": "2026-08-17T23:44:04.807763Z",
    "liveOutput": False,
    "journalSha256": "d1019f18f4cef48d6bbca9ddf9ea875c6b35b58f16830fc18bf5e92a4f190f56",
    "evidenceSha256SumsSha256": "af3e0138e3c64fbb1fb8206eb31b7402d514d92e621583f244c32449fcb5f73e",
}
assert value["evidenceFiles"] == sorted(value["evidenceFiles"])
assert len(value["evidenceFiles"]) == 7
assert set(value["postState"].values()) <= {True, False, 0}
assert value["postState"]["outputDisabled"] is True
assert value["postState"]["historicalNamespacesExcludedFromMutation"] is True
print("Phase 5.51 attempt 1 current-kernel GPIO4: PASS")
