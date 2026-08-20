#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the sealed Phase 5.52 representative-build record."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "release/gate-c-representative-build-manifest-phase5.52-v1.json"
INVENTORY = ROOT / "docs/evidence/gate-c-phase5.52-release-input-inventory.json"
TRANSCRIPT = ROOT / "docs/evidence/gate-c-phase5.52-representative-build-transcript.txt"
SOURCE_COMMIT = "f710554c4697d75210cbd33c9eea13474d60557a"
manifest = json.loads(MANIFEST.read_text())
inventory = json.loads(INVENTORY.read_text())


def frozen(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{SOURCE_COMMIT}:{path}"], cwd=ROOT)


assert manifest["candidate"] == {
    "release": "0.0.0-phase5.52",
    "sourceCommit": SOURCE_COMMIT,
    "archiveSha256": "0c67dee49a26bf5ab103d04bcf493bba8ae373a9f45b87e5704f52ede96bce01",
    "cleanSourceArchiveSha256": "e2ab915d05ceaff7093de36bdec18a58dd15eb3344c353ea4014f189e95370fc",
}
result = manifest["result"]
assert result["status"] == "passed" and result["exitStatus"] == 0
assert result["diagnosticsCount"] == result["correctedOrchestrationDiagnostics"] == 0
assert result["compatibilityState"] == "Compatible-unqualified"
assert result["liveEligible"] is False
assert result["moduleVersion"] == "0.0.0-phase5.52"
assert result["moduleSha256"] == \
    "fdadeafbe50b9d515e58220e5f3cd0e3c1eccc5b7703c8768468927bdce4eb86"
for key, path in {
    "bootstrapSha256": "scripts/gate_d_bootstrap.py",
    "preRootModuleSha256": "scripts/gate_d_preroot.py",
    "outerExecutorSha256": "scripts/gate_d_outer.py",
    "residueToolSha256": "scripts/gate_d_residue.py",
    "administratorSha256": "scripts/rp1-gpclk-admin.py",
    "diagnosticsSha256": "scripts/rp1-gpclk-diagnostics.py",
    "uapiProbeSourceSha256": "tools/gate_d_uapi_probe.c",
    "busyInjectorSourceSha256": "tools/gate_d_busy_injector.c",
}.items():
    assert result[key] == hashlib.sha256(frozen(path)).hexdigest()
assert result["buildTranscriptSha256"] == hashlib.sha256(TRANSCRIPT.read_bytes()).hexdigest()
assert TRANSCRIPT.read_text().splitlines()[0] == f"sourceCommit={SOURCE_COMMIT}"
assert TRANSCRIPT.read_text().splitlines()[-1] == "post-state=PASS"
assert result["releaseInputInventory"]["sha256"] == hashlib.sha256(
    INVENTORY.read_bytes()).hexdigest()
assert {item["name"]: item["sha256"] for item in result["releaseInputs"]} == \
    {item["name"]: item["sha256"] for item in inventory["artifacts"]}
assert len(inventory["artifacts"]) == 7
assert all(item["type"] == "file" and item["mode"] == "0644" and
           item["owner"] == item["group"] == "pi" for item in inventory["artifacts"])
assert all(value is False for value in manifest["preflight"].values())
assert all(value is False for value in manifest["safety"].values())
assert manifest["claimCeiling"] == "representative stock-kernel build compatibility only"
print("Phase 5.52 representative build: PASS")
