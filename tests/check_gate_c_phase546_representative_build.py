#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the sealed Phase 5.46 representative-build record."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "release/gate-c-representative-build-manifest-phase5.46-v1.json"
INVENTORY = ROOT / "docs/evidence/gate-c-phase5.46-release-input-inventory.json"
manifest = json.loads(MANIFEST.read_text())
inventory = json.loads(INVENTORY.read_text())

assert manifest["candidate"] == {
    "release": "0.0.0-phase5.46",
    "sourceCommit": "b43e2744b212f5bc53ad40584254f52310af4684",
    "archiveSha256": "0e0debdd96560602bd61457afc59782cfad2a4fb1b6f9b54e0d2505453e6c8f2",
    "cleanSourceArchiveSha256": "0cd1cb53fa702a50751dbea465945dbec99f921c99d87ec1e413b2c475aa5448",
}
assert manifest["target"]["kernelRelease"] == "6.18.34+rpt-rpi-2712"
assert manifest["target"]["kernelConfigSha256"] == \
    "d5ba966d17d456a6f29e53baf53464e1fd53f9f8e31481da18f2221f1da2593d"
result = manifest["result"]
assert result["status"] == "passed"
assert result["exitStatus"] == result["diagnosticsCount"] == 0
assert result["compatibilityState"] == "Compatible-unqualified"
assert result["liveEligible"] is False
assert result["moduleVersion"] == "0.0.0-phase5.46"
assert result["moduleSha256"] == \
    "c1203555194b6d7983ca4bde978709f09588878022ea58df8fc90adda23ce6e7"
assert result["releaseInputInventory"]["sha256"] == hashlib.sha256(
    INVENTORY.read_bytes()).hexdigest()
assert {item["name"]: item["sha256"] for item in result["releaseInputs"]} == \
    {item["name"]: item["sha256"] for item in inventory["artifacts"]}
assert all(item["type"] == "file" and item["mode"] == "0644" and
           item["owner"] == item["group"] == "pi" for item in inventory["artifacts"])
assert all(value is False for value in manifest["preflight"].values())
assert all(value is False for value in manifest["safety"].values())
assert manifest["claimCeiling"] == "representative stock-kernel build compatibility only"
print("Phase 5.46 representative build: PASS")
