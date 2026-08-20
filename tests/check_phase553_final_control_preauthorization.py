#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the final Phase 5.53 control preauthorization recapture."""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
value = json.loads((ROOT / "docs/evidence/phase5.53-final-control-preauthorization-recapture.json").read_text())
assert value["kind"] == "phase5.53-final-control-preauthorization-recapture"
assert value["authorizationCommit"] == "d391d43a1698c09c1f3dc70037aa39ee475d3db2"
assert value["qualificationArchiveSha256"] == "916a5522e3998ae43f203c217fedce90ad8d4c2d52ae0bd4491407e3cf17211d"
assert value["canonicalSnapshotSha256"] == "cbaed5a7972bb317a9dc27cabead9419ffde2db474df4de493373b6aa474524f"
assert value["captureCount"] == 2 and value["captureBytes"] == 16745
assert value["capturesByteIdentical"] is True
assert value["capturesMatchCanonicalSnapshot"] is True
assert value["target"]["contact"] == "read-only"
assert value["target"]["targetToolFileCreated"] is False
assert value["target"]["packagePathCount"] == 72
assert all(value["target"][key] is False for key in
           ("moduleLoaded", "endpointPresent", "overlayActive", "liveOutput"))
offline = value["offlineRegeneration"]
assert offline["independentReleaseDirectories"] == 2
assert offline["qualificationValidationsPassed"] == 2
assert offline["deterministicControlChecksPassed"] == 2
assert offline["sealedRootAndFakeSystemValidationPassed"] is True
assert offline["attemptCount"] == 38
assert all(offline[key] is False for key in
           ("authorityApproved", "targetExecutionApproved", "executionReady"))
assert value["prohibitedOperationsPerformed"] == []
print("Phase 5.53 final control preauthorization recapture: PASS")
