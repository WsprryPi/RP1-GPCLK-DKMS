#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the sealed Phase 5.49 representative-build record."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "release/gate-c-representative-build-manifest-phase5.49-v1.json"
INVENTORY = ROOT / "docs/evidence/gate-c-phase5.49-release-input-inventory.json"
TRANSCRIPT = ROOT / "docs/evidence/gate-c-phase5.49-representative-build-transcript.txt"
SOURCE_COMMIT = "99c4f3fa032ba7c752a3165b885b2786a89bc033"
manifest = json.loads(MANIFEST.read_text())
inventory = json.loads(INVENTORY.read_text())


def frozen(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{SOURCE_COMMIT}:{path}"], cwd=ROOT)


assert manifest["candidate"] == {
    "release": "0.0.0-phase5.49",
    "sourceCommit": SOURCE_COMMIT,
    "archiveSha256": "381a01ccacef65bc4a3c9108a4ade5549ebddc164cbe3bad8d0a50554a95e608",
    "cleanSourceArchiveSha256": "1cc502f9630a8f1fedd133d9c8e610a5d61375fea27a81265d4810f961be5e5b",
}
result = manifest["result"]
assert manifest["target"]["terminalRecoveryJournalSha256"] == \
    "b76bb27c57af55136042559be4bbc385d6e3498755d3bd39737800703963c514"
assert result["status"] == "passed" and result["exitStatus"] == 0
assert result["diagnosticsCount"] == result["correctedOrchestrationDiagnostics"] == 3
assert result["compatibilityState"] == "Compatible-unqualified"
assert result["liveEligible"] is False
assert result["moduleVersion"] == "0.0.0-phase5.49"
assert result["moduleSha256"] == \
    "a81b5d939fd5ca8ddfaa2c1173fc2c433e3da44cfa13d735332a4f6daf4e591d"
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
print("Phase 5.49 representative build: PASS")
