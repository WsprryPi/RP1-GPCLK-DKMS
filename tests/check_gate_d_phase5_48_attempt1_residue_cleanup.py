#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
value = json.loads((ROOT / "docs/evidence/gate-d-phase5.48-attempt1-residue-cleanup-attestation.json").read_text())
assert value["kind"] == "gate-d-attempt-owned-residue-cleanup-attestation"
assert value["authentication"]["journalStatus"] == "complete"
assert value["authentication"]["journalSealed"] is True
assert value["authentication"]["evidenceChecksumsVerified"] is True
assert value["removed"] == {
    "path": "/var/lib/rp1-gpclk-dkms/gate-d/runs/phase5.48-ef96f246b66b/staging/gd-current-supported-kernel-gpio4",
    "ownerUid": 0,
    "groupGid": 0,
    "mode": "0700",
    "regularFileCount": 866,
    "regularFileBytes": 4870095,
    "symlinkCount": 0,
    "specialFileCount": 0,
    "recursiveRemoval": "exact-literal-path-only",
}
assert value["preserved"]["stagingParentEmpty"] is True
assert value["preserved"]["sealedAttemptEvidenceUnchanged"] is True
assert value["postState"] == {
    "exactResidueAbsentRootAuthorized": True,
    "moduleLoaded": False,
    "endpointPresent": False,
    "overlayActive": False,
    "candidateDkmsPresent": False,
    "predecessorDkmsPresent": False,
    "allSixServicesInactive": True,
    "lifecycleAttempt1Retried": False,
    "lifecycleAttempt2Started": False,
    "outputDisabled": True,
}
assert value["successorGate"]["phase548FrozenBytesModified"] is False
assert value["successorGate"]["repairRequired"] is True
assert value["successorGate"]["protectedAbsenceProbeRequiresAuthority"] is True
print("Phase 5.48 attempt 1 exact residue cleanup: PASS")
