#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the sealed Phase 5.53 split-artifact representative build."""

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "release/gate-c-representative-build-manifest-phase5.53-v1.json"
INVENTORY = ROOT / "docs/evidence/gate-c-phase5.53-release-input-inventory.json"
TRANSCRIPT = ROOT / "docs/evidence/gate-c-phase5.53-representative-build-transcript.txt"
SOURCE = "1884c0f1c53c661495576bf10ce08d8bf7a90bc3"
manifest = json.loads(MANIFEST.read_text())
inventory = json.loads(INVENTORY.read_text())


def frozen(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{SOURCE}:{path}"], cwd=ROOT)


assert manifest["candidate"] == {
    "release": "0.0.0-phase5.53",
    "sourceCommit": SOURCE,
    "productArchiveSha256": "ae6df3a66a9a26a6fb8474e5896c9053b9f69580d8c45383a5556fc397ebb549",
    "qualificationArchiveSha256": "8bd6eff31a90b95c43372d96bac47a4c6fe92b74de92da10e58d99a8ed63c052",
}
result = manifest["result"]
assert result["status"] == "passed" and result["exitStatus"] == 0
assert result["diagnosticsCount"] == 0
assert result["compatibilityState"] == "Compatible-unqualified"
assert result["liveEligible"] is False
assert result["moduleVersion"] == "0.0.0-phase5.53"
assert result["moduleSha256"] == \
    "5c4dd52fb86487f79f72c4f0bcebbe9cb76ee42f53fa682fc12f0ad640e6c87b"
for key, path in {
    "administratorSha256": "scripts/rp1-gpclk-admin.py",
    "diagnosticsSha256": "scripts/rp1-gpclk-diagnostics.py",
    "bootstrapSha256": "scripts/gate_d_bootstrap.py",
    "preRootModuleSha256": "scripts/gate_d_preroot.py",
    "outerExecutorSha256": "scripts/gate_d_outer.py",
    "residueToolSha256": "scripts/gate_d_residue.py",
    "uapiProbeSourceSha256": "tools/gate_d_uapi_probe.c",
    "busyInjectorSourceSha256": "tools/gate_d_busy_injector.c",
}.items():
    assert result[key] == hashlib.sha256(frozen(path)).hexdigest()
assert result["buildTranscriptSha256"] == hashlib.sha256(TRANSCRIPT.read_bytes()).hexdigest()
text = TRANSCRIPT.read_text()
assert text.splitlines()[0] == f"sourceCommit={SOURCE}"
assert text.splitlines()[-1] == "post-state=PASS"
assert "product-build-qualification-archive=unused-and-unchanged" in text
assert len(inventory["artifacts"]) == 8
assert {item["name"] for item in inventory["artifacts"]} >= {
    "rp1-gpclk-dkms-0.0.0-phase5.53.tar.gz",
    "rp1-gpclk-dkms-qualification-0.0.0-phase5.53.tar.gz",
}
assert all(item["type"] == "file" and item["mode"] == "0644" and
           item["owner"] == item["group"] == "pi" for item in inventory["artifacts"])
assert inventory["specialFiles"] == inventory["extendedAttributes"] == []
assert all(value is False for value in manifest["preflight"].values())
assert all(value is False for value in manifest["safety"].values())
assert manifest["claimCeiling"] == \
    "representative stock-kernel build compatibility only; lifecycle matrix remains blocked"
print("Phase 5.53 split-artifact representative build: PASS")
