#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import sys
import tarfile
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import gate_d_attempts as attempts
import gate_d_outer as outer

instance = json.loads((ROOT / "release/gate-d-execution-instance-phase5.48-v1.json").read_text())
plan = json.loads((ROOT / "release/gate-d-target-operation-plan-phase5.48-v1.json").read_text())
documents = attempts.generate(instance, plan, schema_version=2)
assert len(documents) == 38
for document in documents:
    attempts.validate_document(document)
    outer.validate_document(document)
    operations = [step["operation"] for step in document["steps"]]
    assert operations.count("remove-attempt-residue") == 1
    cleanup = operations.index("remove-attempt-residue")
    assert operations[cleanup - 1] == "restore-services"
    assert operations[cleanup + 1] == "audit-residue"

document = copy.deepcopy(next(item for item in documents if item["operationId"] == "gd-current-supported-kernel-gpio4"))
with tempfile.TemporaryDirectory() as temporary:
    root = pathlib.Path(temporary)
    (root / "inputs").mkdir()
    for label in ("candidate", "predecessor"):
        archive = root / f"inputs/{label}.tar.gz"
        payload = root / f"{label}.txt"
        payload.write_text(label)
        with tarfile.open(archive, "w:gz") as output:
            output.add(payload, arcname=f"rp1-gpclk-dkms-{label}/README")
        document["inputs"][f"{label}Archive"] = f"/inputs/{label}.tar.gz"
        document["inputs"][f"{label}ArchiveSha256"] = hashlib.sha256(archive.read_bytes()).hexdigest()
    for route in ("gpio4", "gpio20"):
        dtbo = root / f"inputs/rp1-gpclk-{route}.dtbo"
        dtbo.write_bytes(route.encode())
        document["inputs"][f"{route}Dtbo"] = f"/inputs/rp1-gpclk-{route}.dtbo"
        document["inputs"][f"{route}DtboSha256"] = hashlib.sha256(dtbo.read_bytes()).hexdigest()
    dispatcher = outer.ClosedDispatcher(document)
    for step in document["steps"]:
        step["action"] = dispatcher.action(step["operation"]).as_json()
    fake = outer.FilesystemFake(root, document)
    result = outer.execute(document, document_sha256="1" * 64, index_sha256="2" * 64,
                           root=root, runner=fake.run, internal=fake.internal)
    assert result["status"] == "complete" and result["sealed"] is True
    staging = outer.rooted(root, document["inputs"]["stagingDirectory"])
    assert not staging.exists()

with tempfile.TemporaryDirectory() as temporary:
    root = pathlib.Path(temporary)
    denied = copy.deepcopy(document)
    evidence = outer.rooted(root, denied["evidenceDirectory"])
    evidence.mkdir(parents=True)
    staging = outer.rooted(root, denied["inputs"]["stagingDirectory"])
    original_lstat = outer.os.lstat
    outer.os.lstat = lambda path: (_ for _ in ()).throw(PermissionError(path))
    try:
        try:
            outer.default_internal("audit-residue", denied, root)
        except ValueError as error:
            assert "absence is not observable" in str(error)
        else:
            raise AssertionError("permission denial was accepted as absence")
    finally:
        outer.os.lstat = original_lstat

schema1 = attempts.generate(instance, plan)
assert all(item["schemaVersion"] == 1 for item in schema1)
assert all([step["operation"] for step in item["steps"]].count("remove-attempt-residue") ==
           (1 if item["matrixRow"] == "interrupted-upgrade" else 0) for item in schema1)
print("Gate D schema-2 terminal cleanup and authoritative absence: PASS (38 attempts)")
