#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the sealed Phase 5.47 representative-build record."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "release/gate-c-representative-build-manifest-phase5.47-v1.json"
INVENTORY = ROOT / "docs/evidence/gate-c-phase5.47-release-input-inventory.json"
manifest = json.loads(MANIFEST.read_text())
inventory = json.loads(INVENTORY.read_text())

assert manifest["candidate"] == {
    "release": "0.0.0-phase5.47",
    "sourceCommit": "c5320ac5419a04d17345370204524f219b7ff403",
    "archiveSha256": "497368ac11b32e5491dab76103ad3bb2da0975c086e9898a801c5c2df1be82be",
    "cleanSourceArchiveSha256": "7d40f032a93c8062934ce5bbeb0c328bd5806ca355f5544dcd7c561267213ed8",
}
assert manifest["target"]["kernelRelease"] == "6.18.34+rpt-rpi-2712"
assert manifest["target"]["deviceTreeAlias"] == \
    "/proc/device-tree -> /sys/firmware/devicetree/base"
result = manifest["result"]
assert result["status"] == "passed"
assert result["exitStatus"] == result["diagnosticsCount"] == 0
assert result["compatibilityState"] == "Compatible-unqualified"
assert result["liveEligible"] is False
assert result["moduleVersion"] == "0.0.0-phase5.47"
assert result["moduleSha256"] == \
    "5c585105cfd5e11a83797bf34f52e9d0ed5a19c5f3ecf7bb74d771f01419ead3"
assert result["bootstrapSha256"] == hashlib.sha256(
    (ROOT / "scripts/gate_d_bootstrap.py").read_bytes()).hexdigest()
assert result["outerExecutorSha256"] == hashlib.sha256(
    (ROOT / "scripts/gate_d_outer.py").read_bytes()).hexdigest()
assert result["busyInjectorSourceSha256"] == hashlib.sha256(
    (ROOT / "tools/gate_d_busy_injector.c").read_bytes()).hexdigest()
assert result["uapiProbeSourceSha256"] == hashlib.sha256(
    (ROOT / "tools/gate_d_uapi_probe.c").read_bytes()).hexdigest()
assert result["releaseInputInventory"]["sha256"] == hashlib.sha256(
    INVENTORY.read_bytes()).hexdigest()
assert {item["name"]: item["sha256"] for item in result["releaseInputs"]} == \
    {item["name"]: item["sha256"] for item in inventory["artifacts"]}
assert all(item["type"] == "file" and item["mode"] == "0644" and
           item["owner"] == item["group"] == "pi" for item in inventory["artifacts"])
assert all(value is False for value in manifest["preflight"].values())
assert all(value is False for value in manifest["safety"].values())
assert manifest["claimCeiling"] == "representative stock-kernel build compatibility only"
print("Phase 5.47 representative build: PASS")
