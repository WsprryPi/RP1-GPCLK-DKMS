#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
evidence = json.loads((ROOT / "docs/evidence/phase5.54-target-preauthorization-recapture.json").read_text())
prompt = (ROOT / "docs/contracts/phase5.54-target-reset-inactive-install-authorization-prompt.md").read_text()
normalized_prompt = " ".join(prompt.split())

assert evidence["kind"] == "phase5.54-target-preauthorization-recapture"
assert evidence["captureCount"] == 2 and evidence["capturesByteIdentical"] is True
assert evidence["predecessor"] == {
    "release": "0.0.0-phase5.53",
    "ledgerSha256": "d4fe02f8d66ac298f2076b37be297097f392095904cc3809717713cd01a14f8d",
    "ledgerStatus": "complete",
    "ledgerCheckpoint": "commit-state",
    "recoveryRequired": False,
    "liveOutput": False,
    "dkmsStatus": "installed",
    "sourceDirectoryPresent": True,
    "debianPackageRegistered": False,
}
assert evidence["runtime"] == {
    "moduleLoaded": False,
    "endpointPresent": False,
    "overlayApplied": False,
    "bootOverlaySelected": False,
    "controlledServicesActive": 0,
    "qualificationLedgerPresent": False,
}
assert not any(evidence["authorization"].values())
for digest in (
    evidence["candidateEvidenceCommit"],
    evidence["captureSha256"],
    evidence["predecessor"]["ledgerSha256"],
    evidence["candidate"]["packageSha256"],
):
    assert digest in prompt
assert "exactly one ledger-bound Phase 5.53 removal" in normalized_prompt
assert "standard inactive Phase 5.54 package installation" in normalized_prompt
assert "Stop before lifecycle" in normalized_prompt
print("Phase 5.54 target preauthorization: PASS")
