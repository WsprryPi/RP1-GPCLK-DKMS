#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the final Phase 5.53 staging validation stop."""
from __future__ import annotations
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
value = json.loads((ROOT / "docs/evidence/phase5.53-final-staging-validation-stop.json").read_text())
assert value["kind"] == "phase5.53-final-staging-validation-stop"
assert value["authorizedTransportSha256"] == "f8ea112c2b3ff1fe18c8d48dc54f4ee8a5f41427595a163ddde2907e11c9a73b"
assert value["preflight"] == {"captureCount": 2, "captureBytes": 16745,
    "capturesMatchCanonical": True, "requiredTargetPathsInitiallyAbsent": True}
assert value["transport"]["failure"] == "duplicate-staging-root-directory-entry"
assert value["transport"]["directoryRecordCount"] == 31
assert value["transport"]["uniqueDirectoryPathCount"] == 30
assert all(value["mutationBoundary"][key] is False for key in value["mutationBoundary"])
assert value["cleanup"]["exactStagingNamespaceRemoved"] is True
assert value["cleanup"]["stagingNamespaceAbsentAfterCleanup"] is True
assert value["disposition"].startswith("authorization exhausted")
print("Phase 5.53 final staging validation stop: PASS")
