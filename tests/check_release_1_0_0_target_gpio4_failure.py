#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
evidence = json.loads((ROOT / "docs/evidence/release-1.0.0-final-target-verification-gpio4-failure.json").read_text())
roadmap = json.loads((ROOT / "release/release-integration-gates-v1.json").read_text())
gates = {gate["id"]: gate for gate in roadmap["gates"]}

assert evidence["finalRecaptureSha256"] == evidence["preauthorizationRecaptureSha256"]
assert evidence["installation"]["packageVersion"] == "1.0.0-1"
assert evidence["installation"]["stockDkmsInstallCount"] == 4
assert evidence["gpio4Attempt"]["attemptCount"] == 1
assert evidence["gpio4Attempt"]["failureType"] == "qualification-control-defect"
assert evidence["gpio4Attempt"]["probeExecuted"] is False
assert evidence["cleanup"]["soleAttemptOverlayIdentifier"] == "0"
assert evidence["cleanup"]["inactiveBaselineRestored"] is True
assert len(evidence["notAttempted"]) == 4
assert not any(evidence["safety"].values())
assert evidence["result"] == "failed-closed-inactive-final-package-restored"
assert gates["final-candidate-target-verification"]["status"] == "blocked"
assert "release-1.0.0-final-target-verification-gpio4-failure.json" in " ".join(gates["final-candidate-target-verification"]["evidence"])

print("Release 1.0.0 final target GPIO4 failure: PASS")
