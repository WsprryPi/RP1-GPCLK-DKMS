#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate Phase 5.51 controls with only exact frozen archived tool bytes."""
from __future__ import annotations

import hashlib
import importlib
import json
import pathlib
import subprocess
import sys
import tarfile
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
ARCHIVE_SHA256 = "253bd54054eb0b673f9e61c58a46b6b7ca2cf78d756fe4e80656f4ac1233f549"
RELEASE = "0.0.0-phase5.51"

if len(sys.argv) != 2:
    raise SystemExit("usage: check_gate_d_phase5_51_archived_control_set.py ARCHIVE")
archive = pathlib.Path(sys.argv[1]).resolve()

def sha_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()

def sha(path: pathlib.Path) -> str:
    return sha_bytes(path.read_bytes())

if archive.is_symlink() or not archive.is_file() or sha(archive) != ARCHIVE_SHA256:
    raise SystemExit("Phase 5.51 archive identity differs")

instance = json.loads((ROOT / "release/gate-d-execution-instance-phase5.51-v1.json").read_text())
plan = json.loads((ROOT / "release/gate-d-target-operation-plan-phase5.51-v1.json").read_text())
envelope = json.loads((ROOT / "release/gate-d-pre-root-bootstrap-envelope-phase5.51-v1.json").read_text())

with tempfile.TemporaryDirectory() as temporary:
    base = pathlib.Path(temporary)
    extracted = base / "archive"
    extracted.mkdir()
    with tarfile.open(archive, "r:gz") as source:
        members = source.getmembers()
        prefix = f"rp1-gpclk-dkms-{RELEASE}"
        for member in members:
            pure = pathlib.PurePosixPath(member.name)
            if (not pure.parts or pure.parts[0] != prefix or pure.is_absolute() or
                    ".." in pure.parts or not (member.isdir() or member.isfile())):
                raise SystemExit("unsafe Phase 5.51 archive member")
        source.extractall(extracted, filter="data")
    archived_root = extracted / prefix
    archived_schema_dir = archived_root / "schema"
    subprocess.run([
        "check-jsonschema", "--base-uri", archived_schema_dir.as_uri() + "/",
        "--schemafile", str(archived_schema_dir / "gate-d-execution-instance-v1.schema.json"),
        str(ROOT / "release/gate-d-execution-instance-phase5.51-v1.json"),
    ], check=True)
    frozen_root = base / "qualification"
    frozen_root.mkdir(mode=0o700)
    marker = frozen_root / instance["qualificationRoot"]["identityFile"]
    marker.write_text(json.dumps(envelope["proposedRoot"]["marker"], sort_keys=True,
                                 separators=(",", ":")) + "\n")
    marker.chmod(0o400)
    if sha(marker) != instance["qualificationRoot"]["identitySha256"]:
        raise SystemExit("qualification marker identity differs")

    archived_destinations = set()
    for item in envelope["transitionFiles"]:
        relative = pathlib.PurePosixPath(item["destination"])
        if relative.is_absolute() or ".." in relative.parts:
            raise SystemExit("unsafe transition destination")
        archived = archived_root / relative
        generated = ROOT / relative
        if archived.is_file() and not archived.is_symlink():
            payload = archived.read_bytes()
            archived_destinations.add(relative.as_posix())
        elif generated.is_file() and not generated.is_symlink():
            payload = generated.read_bytes()
        else:
            raise SystemExit(f"transition source unavailable: {relative}")
        if sha_bytes(payload) != item["sha256"]:
            raise SystemExit(f"transition identity differs: {relative}")
        target = frozen_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)

    required_archived = {
        "scripts/gate_d_attempts.py", "scripts/gate_d_instance.py",
        "scripts/gate_d_root.py", "scripts/gate_d_target_plan.py",
        "scripts/gate_d_bootstrap.py", "scripts/gate_d_lifecycle.py",
        "scripts/gate_d_outer.py", "scripts/gate_d_preroot.py",
        "schema/gate-d-execution-instance-v1.schema.json",
    }
    if not required_archived <= archived_destinations:
        raise SystemExit("closed root did not use every required archived tool")

    scripts = frozen_root / "scripts"
    sys.path.insert(0, str(scripts))
    for name in ("gate_d_attempts", "gate_d_instance", "gate_d_root",
                 "gate_d_target_plan"):
        sys.modules.pop(name, None)
    archived_root_validator = importlib.import_module("gate_d_root")
    archived_root_validator.validate = lambda reference, verify=True: frozen_root
    archived_instance = importlib.import_module("gate_d_instance")
    result = archived_instance.validate(instance)
    if result["inputsReady"] is not True or result["executionReady"] is not True:
        raise SystemExit("archived validator changed authorized readiness")
    if not instance["authorization"]["approved"] or not instance["authorization"]["targetExecutionApproved"]:
        raise SystemExit("archived validator lost authorization-bearing controls")
    archived_attempts = importlib.import_module("gate_d_attempts")
    expected = archived_attempts.generate(instance, plan, schema_version=2)
    if len(expected) != 38 or any(item.get("schemaVersion") != 2 for item in expected):
        raise SystemExit("archived attempt generation differs")

print("Phase 5.51 exact archived control-set validation: PASS")
