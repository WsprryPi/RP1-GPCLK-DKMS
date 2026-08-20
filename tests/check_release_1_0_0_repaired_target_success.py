#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
evidence = json.loads((ROOT / "docs/evidence/release-1.0.0-repaired-target-verification-success.json").read_text())
roadmap = json.loads((ROOT / "release/release-integration-gates-v1.json").read_text())
gates = {gate["id"]: gate for gate in roadmap["gates"]}

assert evidence["productPackageSha256"] == roadmap["candidateSnapshot"]["finalPackageSha256"]
assert evidence["qualificationArchiveSha256"] == roadmap["candidateSnapshot"]["qualificationArchiveSha256"]
assert evidence["preflight"]["stockDkmsInstallCount"] == 4
assert evidence["gpio4"]["attemptCount"] == evidence["gpio20"]["attemptCount"] == 1
assert evidence["gpio4"]["uapiQueryAcquireReleasePassed"] is True
assert evidence["gpio20"]["uapiQueryAcquireReleasePassed"] is True
assert evidence["packageLifecycle"]["removalAttemptCount"] == 1
assert evidence["packageLifecycle"]["reinstallAttemptCount"] == 1
assert evidence["finalState"]["packageVersion"] == "1.0.0-1"
assert evidence["finalState"]["stockDkmsInstallCount"] == 4
assert evidence["finalState"]["scopedKernelWarningsErrorsFailures"] == []
assert all(evidence["cleanup"].values())
assert not any(evidence["safety"].values())
assert evidence["result"] == "pass-final-candidate-target-verified-inactive"
assert roadmap["currentClassification"] == "target-verified-release-candidate-awaiting-review"
assert gates["final-candidate-target-verification"]["status"] == "passed"
assert gates["release-review-and-claim-audit"]["status"] == "blocked"
assert evidence["nextGate"] == "release-review-and-claim-audit"

print("Release 1.0.0 repaired final target verification: PASS")
