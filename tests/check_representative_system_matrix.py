#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import copy
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
path = ROOT / "release/representative-system-matrix-v1.json"
matrix = json.loads(path.read_text())

EXPECTED_ROWS = [
    "current-supported-kernel", "prior-supported-kernel-downgrade", "newer-unknown-kernel",
    "signing-not-enforced", "signing-enforced-enrolled-key", "deliberate-build-failure",
    "deliberate-signature-rejection", "missing-headers", "overlay-or-resource-conflict",
    "interrupted-upgrade", "stale-manifest", "corrupted-archive-or-dtbo",
    "removal-inactive", "removal-open-or-active", "reinstall-after-removal",
]
ROW_KEYS = {"id", "representativeClass", "selection", "preconditions", "failureInjection",
            "expected", "cleanupResult", "diagnostics", "allowedChanges", "finalState", "residueAudit",
            "maximumDuration", "evidenceIdentity"}
EXPECTED_KEYS = {"compatibilityState", "reason", "liveEligible", "transactionState", "retainedPriorVersion"}
STATES = {"Compatible-unqualified", "Unavailable", "Rejected"}
EXPECTED_STATES = {
    "current-supported-kernel": "Compatible-unqualified",
    "prior-supported-kernel-downgrade": "Compatible-unqualified",
    "newer-unknown-kernel": "Unavailable",
    "signing-not-enforced": "Compatible-unqualified",
    "signing-enforced-enrolled-key": "Compatible-unqualified",
    "deliberate-build-failure": "Unavailable",
    "deliberate-signature-rejection": "Rejected",
    "missing-headers": "Unavailable",
    "overlay-or-resource-conflict": "Rejected",
    "interrupted-upgrade": "Unavailable",
    "stale-manifest": "Rejected",
    "corrupted-archive-or-dtbo": "Rejected",
    "removal-inactive": "Unavailable",
    "removal-open-or-active": "Rejected",
    "reinstall-after-removal": "Compatible-unqualified",
}


def validate(document: dict) -> None:
    if document.get("schemaVersion") != 1 or document.get("outputEnabled") is not False:
        raise ValueError("invalid matrix identity or output gate")
    if document.get("rowOrder") != EXPECTED_ROWS:
        raise ValueError("required row order changed")
    rows = document.get("rows")
    if not isinstance(rows, list) or [row.get("id") for row in rows] != EXPECTED_ROWS:
        raise ValueError("rows missing, extra, duplicated, or reordered")
    for row in rows:
        if set(row) != ROW_KEYS:
            raise ValueError(f"invalid fields for {row.get('id')}")
        if any(not isinstance(row[key], str) or not row[key].strip()
               for key in ROW_KEYS - {"id", "expected", "diagnostics"}):
            raise ValueError(f"empty row contract for {row['id']}")
        if not isinstance(row["diagnostics"], list) or len(row["diagnostics"]) < 4:
            raise ValueError(f"insufficient diagnostics for {row['id']}")
        if not all(isinstance(item, str) and item.strip() for item in row["diagnostics"]):
            raise ValueError(f"invalid diagnostics for {row['id']}")
        if not any("cleanup latch" in item for item in row["diagnostics"]):
            raise ValueError(f"cleanup latch absent for {row['id']}")
        if "unexplained delta" not in row["residueAudit"]:
            raise ValueError(f"unexplained-delta audit absent for {row['id']}")
        expected = row["expected"]
        if not isinstance(expected, dict) or set(expected) != EXPECTED_KEYS:
            raise ValueError(f"invalid expected state for {row['id']}")
        if expected["compatibilityState"] not in STATES or expected["liveEligible"] is not False:
            raise ValueError(f"forbidden state or live eligibility for {row['id']}")
        if expected["compatibilityState"] != EXPECTED_STATES[row["id"]]:
            raise ValueError(f"incorrect compatibility state for {row['id']}")
        if any(not isinstance(expected[key], str) or not expected[key].strip()
               for key in EXPECTED_KEYS - {"liveEligible"}):
            raise ValueError(f"ambiguous expected result for {row['id']}")


validate(matrix)
assert matrix["release"] == json.loads((ROOT / "release/release-layout-v1.json").read_text())["release"]
corrupt = next(row for row in matrix["rows"] if row["id"] == "corrupted-archive-or-dtbo")
for identity in ("source archive", "GPIO4 DTBO", "GPIO20 DTBO"):
    assert identity in corrupt["failureInjection"]
reinstall = next(row for row in matrix["rows"] if row["id"] == "reinstall-after-removal")
assert "proved empty" in reinstall["selection"].lower()
assert "second complete removal" in reinstall["cleanupResult"]

for mutation in (
    lambda doc: doc.update(outputEnabled=True),
    lambda doc: doc["rows"].pop(),
    lambda doc: doc["rows"][0].update(extra="unexpected"),
    lambda doc: doc["rows"][0]["expected"].update(liveEligible=True),
    lambda doc: doc["rows"][0]["expected"].update(compatibilityState="Rejected"),
    lambda doc: doc["rows"][0].update(diagnostics=["too little"]),
    lambda doc: doc["rows"][0].update(residueAudit="clean"),
):
    bad = copy.deepcopy(matrix)
    mutation(bad)
    try:
        validate(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid representative matrix accepted")

print("representative-system matrix: PASS")
