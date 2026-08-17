#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
value = json.loads((ROOT / "docs/evidence/gate-d-phase5.48-attempt1-residue-blocker-attestation.json").read_text())
assert value["kind"] == "gate-d-attempt-terminal-residue-blocker-attestation"
assert value["attempt"]["indexEntry"] == 1
assert value["execution"]["reportedStatus"] == "complete"
assert value["execution"]["completedSteps"] == 19
assert value["execution"]["sealed"] is True
assert value["execution"]["liveOutput"] is False
assert value["functionalResult"]["loadParameter"] == "live_output=0"
assert value["functionalResult"]["outputDisabled"] is True
assert value["residue"]["regularFileCount"] == 866
assert value["residue"]["regularFileBytes"] == 4870095
assert value["residue"]["expectedFinalState"] == "empty-inactive-baseline"
assert value["residue"]["presentAfterSealing"] is True
assert value["independentValidation"] == {
    "initialUnprivilegedPathProbe": "false-negative-due-to-root-owned-parent",
    "rootLevelInventory": "residue-confirmed",
    "classification": "sealed-executor-terminal-residue-discrepancy",
    "safeToAdvance": False,
}
assert value["result"] == {
    "manualCleanupPerformed": False,
    "retryPerformed": False,
    "lifecycleAttempt2Started": False,
    "outputDisabled": True,
}
print("Phase 5.48 attempt 1 terminal residue blocker: PASS")
