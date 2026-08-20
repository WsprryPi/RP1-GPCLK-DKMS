#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
roadmap = json.loads((ROOT / "release/release-integration-gates-v1.json").read_text())
decision = json.loads(
    (ROOT / "docs/evidence/release-1.0.0-semantic-version-selection.json").read_text()
)

assert '#define RP1_GPCLK_MODULE_VERSION "1.0.0"' in (
    ROOT / "include/rp1_gpclk/version.h"
).read_text()
assert "MODULE_VERSION := 1.0.0" in (ROOT / "debian/rules").read_text()
assert (ROOT / "debian/changelog").read_text().startswith(
    "rp1-gpclk-dkms (1.0.0-1) unstable;"
)
assert roadmap["release"] == decision["version"] == "1.0.0"
assert roadmap["debianVersion"] == decision["debianVersion"] == "1.0.0-1"
assert roadmap["expectedTag"] == decision["expectedTag"] == "v1.0.0"
gates = {gate["id"]: gate for gate in roadmap["gates"]}
assert gates["semantic-version-selection"]["status"] == "passed"
assert gates["final-artifact-reproduction"]["status"] == "passed"
assert gates["final-candidate-target-verification"]["status"] == "blocked"
assert roadmap["modulePublicationConfirmed"] is False
assert decision["tagCreated"] is False
assert decision["artifactConstructed"] is False
assert decision["targetContacted"] is False
assert decision["published"] is False
assert decision["result"] == "selected-not-built-not-tagged-not-published"

print("Release 1.0.0 semantic version selection: PASS")
