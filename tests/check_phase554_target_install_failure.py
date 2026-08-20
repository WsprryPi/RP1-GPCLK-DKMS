#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
evidence = json.loads((ROOT / "docs/evidence/phase5.54-target-install-failure.json").read_text())
prompt = (ROOT / "docs/contracts/phase5.54-gpio4-orphan-recovery-authorization-prompt.md").read_text()

assert evidence["kind"] == "phase5.54-target-install-failure-evidence"
assert evidence["predecessorRemoval"]["attempts"] == 1
assert evidence["predecessorRemoval"]["status"] == "removed"
assert evidence["packageInstallation"]["attempts"] == 1
assert evidence["packageInstallation"]["result"] == "failed-before-configuration"
assert evidence["packageInstallation"]["dpkgAuditEmpty"] is True
assert evidence["packageInstallation"]["dpkgStatus"] == "install ok not-installed"
assert evidence["rootCause"]["phase553LedgerOwnedGpio4"] is False
assert evidence["rootCause"]["gpio4FileSha256"] == evidence["rootCause"]["candidateGpio4FileSha256"]
assert evidence["preservedState"]["moduleLoaded"] is False
assert evidence["preservedState"]["overlayApplied"] is False
for identity in (evidence["failureStateCaptureSha256"], evidence["packageSha256"], evidence["rootCause"]["gpio4FileSha256"]):
    assert identity in prompt
assert "exactly one" in prompt and "package-install retry" in prompt
print("Phase 5.54 stopped install failure: PASS")
