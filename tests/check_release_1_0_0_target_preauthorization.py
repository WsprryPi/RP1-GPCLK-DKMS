#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
evidence = json.loads((ROOT / "docs/evidence/release-1.0.0-final-target-preauthorization-recapture.json").read_text())
prompt = (ROOT / "docs/contracts/release-1.0.0-final-target-verification-authorization-prompt.md").read_text()

for identity in (
    evidence["candidateSourceCommit"], evidence["controlCommit"],
    evidence["recaptureSha256"], evidence["productPackageSha256"],
    evidence["qualificationArchiveSha256"],
):
    assert identity in prompt
assert evidence["result"] == "ready-for-explicit-authorization"
assert evidence["qualificationClosure"]["everyInvokedQualificationPathPresent"] is True
assert evidence["qualificationClosure"]["completeChecksumEnforcementPresent"] is True
assert evidence["physicalSafetyConfirmationFresh"] is False
assert evidence["targetMutationAuthorized"] is False
assert evidence["targetMutationPerformed"] is False
for phrase in (
    "final read-only recapture", "Stop without mutation on any mismatch",
    "Si5351 path is physically disconnected", "antenna or transmitter is connected",
    "exactly one GPIO4 lifecycle", "exactly once for GPIO20",
    "exactly one conventional package removal", "live_output=1",
    "publication remain separate gates",
):
    assert phrase in prompt

print("Release 1.0.0 target preauthorization recapture: PASS")
