#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate split-artifact invalidation and evidence carry-forward policy."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "release/artifact-scoped-invalidation-policy-v1.json"
value = json.loads(POLICY.read_text())

assert value["schemaVersion"] == 1
assert value["kind"] == "artifact-scoped-invalidation-policy"
assert value["appliesBeforePublicationOnly"] is True
assert set(value["domains"]) == {"product", "qualification"}
product = value["domains"]["product"]
qualification = value["domains"]["qualification"]
assert product["layout"] == "release/release-layout-v1.json"
assert qualification["layout"] == "release/qualification-layout-v1.json"
assert "representative-build" in product["retainedEvidence"]
assert "control-set" in qualification["invalidatedEvidence"]
successor = value["qualificationOnlySuccessor"]
assert "product archive regeneration" in \
    successor["explicitlyNotRequiredWhenProductClosureIsUnchanged"]
assert "representative module rebuild" in \
    successor["explicitlyNotRequiredWhenProductClosureIsUnchanged"]
assert "one complete offline regression suite" in successor["requiredRenewedEvidence"]
assert "published candidate bytes" in successor["failClosedTriggers"]
assert value["publication"] == {
    "requiresOneFinalProductIdentity": True,
    "requiresOneFinalQualificationIdentity": True,
    "supersededQualificationCandidatesAreNotPublished": True,
    "publishedBytesAreImmutable": True,
}
layout = json.loads((ROOT / "release/qualification-layout-v1.json").read_text())
entries = [item for item in layout["artifacts"]
           if item["path"] == "release/artifact-scoped-invalidation-policy-v1.json"]
assert len(entries) == 1 and entries[0]["kind"] == "archive"
assert "no lifecycle" in value["claimCeiling"]
print("artifact-scoped invalidation policy: PASS")
