#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate sealed Phase 5.51 representative-build evidence."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "release/gate-c-representative-build-manifest-phase5.51-v1.json"
INVENTORY = ROOT / "docs/evidence/gate-c-phase5.51-release-input-inventory.json"
TRANSCRIPT = ROOT / "docs/evidence/gate-c-phase5.51-representative-build-transcript.txt"
def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
value = json.loads(MANIFEST.read_text())
assert value["candidate"] == {"release":"0.0.0-phase5.51","sourceCommit":"cc87e0cdec7195eb69de2a6606f388e23ee0799c","archiveSha256":"253bd54054eb0b673f9e61c58a46b6b7ca2cf78d756fe4e80656f4ac1233f549","cleanSourceArchiveSha256":"dfd923dfc83ba3a47b787814068787c0c5eb6d1f9da7d9d7f7d5c4da44e7bcc0"}
result = value["result"]
assert result["status"] == "passed" and result["exitStatus"] == 0
assert result["diagnosticsCount"] == result["correctedOrchestrationDiagnostics"] == 4
assert result["compatibilityState"] == "Compatible-unqualified" and result["liveEligible"] is False
assert result["moduleVersion"] == "0.0.0-phase5.51" and result["archivedPermanentExecutorRegression"] is True
assert result["retainedFileCount"] == 771 and result["specialFileCount"] == 0
assert result["executionInstanceValidatorSha256"] == sha(ROOT / "scripts/gate_d_instance.py")
assert result["executionInstanceSchemaSha256"] == sha(ROOT / "schema/gate-d-execution-instance-v1.schema.json")
assert result["buildTranscriptSha256"] == sha(TRANSCRIPT)
assert result["releaseInputInventory"] == {"path":"docs/evidence/gate-c-phase5.51-release-input-inventory.json","sha256":sha(INVENTORY)}
inventory = json.loads(INVENTORY.read_text())
assert inventory["sourceCommit"] == value["candidate"]["sourceCommit"] and len(inventory["artifacts"]) == 7
assert all(item["type"] == "file" and item["mode"] == "0644" for item in inventory["artifacts"])
assert [(item["name"], item["sha256"]) for item in inventory["artifacts"]] == [(item["name"], item["sha256"]) for item in result["releaseInputs"]]
assert value["target"]["transactionJournalSha256"] == "3877dece6b50b866246d3fc01bdc8c9aa036e5876f87d84d37557954c4d14fc2"
assert value["target"]["phase550PreRootJournalSha256"] == "0f513c50f8e4ed5b2f53967072c50433796b29395b5c474bd7a57b5efd12ec67"
assert all(flag is False for flag in value["safety"].values())
assert value["claimCeiling"] == "representative stock-kernel build compatibility only"
print("Phase 5.51 representative build: PASS")
