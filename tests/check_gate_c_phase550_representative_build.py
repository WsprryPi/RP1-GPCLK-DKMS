#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate sealed Phase 5.50 representative-build evidence."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "release/gate-c-representative-build-manifest-phase5.50-v1.json"
INVENTORY = ROOT / "docs/evidence/gate-c-phase5.50-release-input-inventory.json"
TRANSCRIPT = ROOT / "docs/evidence/gate-c-phase5.50-representative-build-transcript.txt"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

value = json.loads(MANIFEST.read_text())
assert value["candidate"] == {
    "release": "0.0.0-phase5.50",
    "sourceCommit": "c24160517b10900bf61243d4988f38247eeed58e",
    "archiveSha256": "ef989bf79faa5c30ddaf8ac5651d75b1755ba2fa385680692183e6145b2927c2",
    "cleanSourceArchiveSha256": "3dd62186a322f27ec8c1b6d70f3f5f5df57a6db25765857abc5516d78d34fae4",
}
result = value["result"]
assert result["status"] == "passed" and result["exitStatus"] == 0
assert result["diagnosticsCount"] == result["correctedOrchestrationDiagnostics"] == 4
assert result["compatibilityState"] == "Compatible-unqualified"
assert result["liveEligible"] is False and result["moduleVersion"] == "0.0.0-phase5.50"
assert result["executionInstanceValidatorSha256"] == sha(ROOT / "scripts/gate_d_instance.py")
assert result["executionInstanceSchemaSha256"] == sha(ROOT / "schema/gate-d-execution-instance-v1.schema.json")
assert result["buildTranscriptSha256"] == sha(TRANSCRIPT)
assert result["releaseInputInventory"] == {
    "path": "docs/evidence/gate-c-phase5.50-release-input-inventory.json",
    "sha256": sha(INVENTORY),
}
inventory = json.loads(INVENTORY.read_text())
assert inventory["sourceCommit"] == value["candidate"]["sourceCommit"]
assert len(inventory["artifacts"]) == 7
assert all(item["type"] == "file" and item["mode"] == "0644" for item in inventory["artifacts"])
assert [(item["name"], item["sha256"]) for item in inventory["artifacts"]] == \
       [(item["name"], item["sha256"]) for item in result["releaseInputs"]]
assert value["target"]["transactionJournalSha256"] == \
    "bdc113ca499f920097affe3e31a96bc98b4cd10fdd23b85e8e59880bb6f40378"
assert value["target"]["terminalRecoveryJournalSha256"] == \
    "b76bb27c57af55136042559be4bbc385d6e3498755d3bd39737800703963c514"
assert value["preflight"] == {
    "moduleLoaded": False, "endpointPresent": False, "overlayActivated": False,
    "dkmsRegistered": False, "relevantServicesActive": False,
    "destinationPreexisted": False,
}
assert all(flag is False for flag in value["safety"].values())
assert value["claimCeiling"] == "representative stock-kernel build compatibility only"
print("Phase 5.50 representative build: PASS")
