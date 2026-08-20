#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the sealed Phase 5.48 representative-build record."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "release/gate-c-representative-build-manifest-phase5.48-v1.json"
INVENTORY = ROOT / "docs/evidence/gate-c-phase5.48-release-input-inventory.json"
manifest = json.loads(MANIFEST.read_text())
inventory = json.loads(INVENTORY.read_text())
SOURCE_COMMIT = "ef96f246b66b25bb70536341b60a5f1e64708c65"


def frozen(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{SOURCE_COMMIT}:{path}"], cwd=ROOT)

assert manifest["candidate"] == {
    "release": "0.0.0-phase5.48",
    "sourceCommit": "ef96f246b66b25bb70536341b60a5f1e64708c65",
    "archiveSha256": "18418395eac577d8718c1e74f6601e005160d2768ea7634a35d00e4ddead9120",
    "cleanSourceArchiveSha256": "8be8d197027def46aa6b93e12a19483df56b2719729961f4b5ca9cec9d5e20c9",
}
result = manifest["result"]
assert result["status"] == "passed" and result["exitStatus"] == 0
assert result["diagnosticsCount"] == result["correctedOrchestrationDiagnostics"] == 1
assert result["compatibilityState"] == "Compatible-unqualified"
assert result["liveEligible"] is False
assert result["moduleVersion"] == "0.0.0-phase5.48"
assert result["moduleSha256"] == \
    "3ee865f9293b69f45f5c17a9217896a2d68c2addd7c494088b430aecb3faf615"
assert result["bootstrapSha256"] == hashlib.sha256(
    frozen("scripts/gate_d_bootstrap.py")).hexdigest()
assert result["outerExecutorSha256"] == hashlib.sha256(
    frozen("scripts/gate_d_outer.py")).hexdigest()
assert result["busyInjectorSourceSha256"] == hashlib.sha256(
    frozen("tools/gate_d_busy_injector.c")).hexdigest()
assert result["releaseInputInventory"]["sha256"] == hashlib.sha256(
    INVENTORY.read_bytes()).hexdigest()
assert {item["name"]: item["sha256"] for item in result["releaseInputs"]} == \
    {item["name"]: item["sha256"] for item in inventory["artifacts"]}
assert all(item["type"] == "file" and item["mode"] == "0644" and
           item["owner"] == item["group"] == "pi" for item in inventory["artifacts"])
assert all(value is False for value in manifest["preflight"].values())
assert all(value is False for value in manifest["safety"].values())
assert manifest["claimCeiling"] == "representative stock-kernel build compatibility only"
print("Phase 5.48 representative build: PASS")
