#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate Phase 5.51 attempt 2 and prevent executor/path regressions."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
prompt = (ROOT / "docs/contracts/gate-d-phase5.51-attempt2-current-kernel-gpio20-prompt.md").read_text()
value = json.loads((ROOT / "docs/evidence/gate-d-phase5.51-attempt2-current-kernel-gpio20-attestation.json").read_text())

permanent = "/usr/libexec/rp1-gpclk-dkms/gate-d-executor"
archived = ("/home/pi/gate-d-inputs/phase5.51-cc87e0cdec71/extracted/"
            "rp1-gpclk-dkms-0.0.0-phase5.51/scripts/gate_d_outer.py")
assert permanent in prompt and archived in prompt
assert "SourceFileLoader" in prompt
assert "do not import from, modify, remove" in prompt
assert value["attempt"] == {
    "ordinal": 2,
    "operationId": "gd-current-supported-kernel-gpio20",
    "documentSha256": "7daa31d418905a8b218f25f35ef8b6dcc87a5c79b472db743abf5ff8f2cd0f9b",
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
    "completedUtc": "2026-08-17T23:55:23.838919Z",
    "liveOutput": False,
    "journalSha256": "fbc9657f9d3f825a8893a8449f112b4f25b0029c27f411d2bbc64db383ca6f98",
    "evidenceSha256SumsSha256": "d79cbff2075bbd8e688a5f19e89a3886f429567267a4ffd39d2729dfd575d047",
}
assert value["uapiResult"] == "route=gpio20 build=0.0.0-phase5.51 live_eligible=0 released=1"
assert value["evidenceFiles"] == sorted(value["evidenceFiles"])
assert len(value["evidenceFiles"]) == 7
assert set(value["postState"].values()) <= {True, False, 0}
assert value["postState"]["outputDisabled"] is True
assert value["postState"]["historicalNamespacesExcludedFromMutation"] is True
print("Phase 5.51 attempt 2 current-kernel GPIO20: PASS")
