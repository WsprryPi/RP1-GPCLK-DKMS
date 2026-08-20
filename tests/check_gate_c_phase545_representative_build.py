#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the sealed Phase 5.45 representative-build record."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "release/gate-c-representative-build-manifest-phase5.45-v1.json"
INVENTORY = ROOT / "docs/evidence/gate-c-phase5.45-release-input-inventory.json"

manifest = json.loads(MANIFEST.read_text())
inventory = json.loads(INVENTORY.read_text())

assert manifest["candidate"] == {
    "release": "0.0.0-phase5.45",
    "sourceCommit": "4b50db7868b7fe5ca9d830f51cd404c250192188",
    "archiveSha256": "21d05675e9d12ddb4c051868578c410737b733786357cee20eb2b0ce03f63356",
    "cleanSourceArchiveSha256": "013cb149d8322011b6942be2d000812a04d7035221ad48a3591aaf8ce908a36f",
}
assert manifest["target"]["kernelRelease"] == "6.18.34+rpt-rpi-2712"
assert manifest["target"]["kernelConfigSha256"] == \
    "2a83d4324e9b47d418b4efac18d3af43d15cc956b71c5a8eb074060bf8383801"
result = manifest["result"]
assert result["status"] == "passed"
assert result["exitStatus"] == result["diagnosticsCount"] == 0
assert result["compatibilityState"] == "Compatible-unqualified"
assert result["liveEligible"] is False
assert result["moduleVersion"] == "0.0.0-phase5.45"
assert result["moduleSha256"] == \
    "977c6997fd87dfb68c61ab4b82db904e86310083741d3a41c0405a417aa36d95"
assert result["releaseInputInventory"]["sha256"] == hashlib.sha256(
    INVENTORY.read_bytes()
).hexdigest()
expected = {item["name"]: item["sha256"] for item in inventory["artifacts"]}
actual = {item["name"]: item["sha256"] for item in result["releaseInputs"]}
assert actual == expected
assert set(inventory["artifacts"][0]) == {
    "name", "type", "size", "mode", "owner", "group", "sha256"
}
assert all(item["type"] == "file" and item["mode"] == "0644" and
           item["owner"] == item["group"] == "pi" for item in inventory["artifacts"])
assert all(value is False for value in manifest["preflight"].values())
assert all(value is False for value in manifest["safety"].values())
assert manifest["claimCeiling"] == \
    "representative stock-kernel build compatibility only"

print("Phase 5.45 representative build: PASS")
