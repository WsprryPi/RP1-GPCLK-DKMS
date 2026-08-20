#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Exercise the final split-artifact staging transport and entry points."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import tarfile
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
release = os.environ.get("PHASE5_53_FINAL_RELEASE_DIRECTORY")
if not release:
    print("Phase 5.53 final staging transport: SKIP (release directory not supplied)")
    raise SystemExit
spec = importlib.util.spec_from_file_location(
    "final_transport", ROOT / "scripts/build_phase5_53_final_staging_transport.py")
assert spec and spec.loader
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


with tempfile.TemporaryDirectory() as temporary:
    root = pathlib.Path(temporary)
    first = root / "transport-1.ustar"
    second = root / "transport-2.ustar"
    first_map = root / "source-map-1.json"
    second_map = root / "source-map-2.json"
    manifest = builder.build(pathlib.Path(release), first, first_map)
    repeated = builder.build(pathlib.Path(release), second, second_map)
    assert first.read_bytes() == second.read_bytes() and manifest == repeated
    assert manifest["regularFileCount"] == len(manifest["sources"]) == 151
    assert {item["owner"] for item in manifest["sources"]} == {
        "release-directory", "repository-control-set", "split-archive-member",
        "separately-sealed-envelope", "separately-sealed-same-version-plan"}
    extracted = root / "extracted"
    extracted.mkdir()
    with tarfile.open(first, "r:") as transport:
        members = transport.getmembers()
        assert sum(item.isfile() for item in members) == 151
        names = [item.name.rstrip("/") for item in members]
        assert len(names) == len(set(names))
        assert all(item.isfile() or item.isdir() for item in members)
        assert not any(item.pax_headers for item in members)
        transport.extractall(extracted, filter="data")
    stage = extracted / builder.STAGE
    envelope_path = stage / builder.SEALED_ENVELOPE
    same_path = stage / builder.SEALED_SAME_VERSION
    envelope = json.loads(envelope_path.read_text())
    same = json.loads(same_path.read_text())
    base = "/home/pi/gate-d-inputs/" + builder.STAGE
    for item in envelope["inputFiles"]:
        path = pathlib.Path(item["path"].replace(base, str(stage)))
        assert path.is_file() and not path.is_symlink() and sha(path) == item["sha256"]
    for field in ("probeArgv", "qualificationInstallArgv", "qualificationRecoveryArgv",
                  "productRollbackArgv"):
        staged_paths = [value for value in same[field] if value.startswith(base + "/")]
        assert staged_paths and all(pathlib.Path(value.replace(base, str(stage))).is_file()
                                    for value in staged_paths)
    driver = stage / f"extracted/rp1-gpclk-dkms-qualification-0.0.0-phase5.53/scripts/gate_d_same_version_driver.py"
    assert driver.is_file() and same["qualificationArchiveSha256"] == \
        "916a5522e3998ae43f203c217fedce90ad8d4c2d52ae0bd4491407e3cf17211d"
    validation = subprocess.run(
        [sys.executable, str(driver), "validate", str(same_path), str(root / "unused-journal")],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    assert json.loads(validation.stdout) == {
        "outputDisabled": True, "readOnly": True, "valid": True}
    executor = pathlib.Path(envelope["stagedExecutor"]["path"].replace(base, str(stage)))
    rewritten = json.loads(json.dumps(envelope).replace(base, str(stage)).replace(
        "/home/pi/gate-d-qualification/" + builder.STAGE, str(root / "qualification")))
    marker = rewritten["proposedRoot"]["marker"]
    marker["rootPath"] = str(root / "qualification")
    rewritten["proposedRoot"]["markerSha256"] = hashlib.sha256(
        (json.dumps(marker, sort_keys=True, separators=(",", ":")) + "\n").encode()).hexdigest()
    document = root / "rewritten-envelope.json"
    document.write_text(json.dumps(rewritten, indent=2, sort_keys=True) + "\n")
    result = subprocess.run(
        [sys.executable, str(executor), "pre-root-bootstrap", str(document),
         "--envelope-sha256", sha(document)], text=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=True)
    assert json.loads(result.stdout) == {
        "outputDisabled": True, "readOnly": True, "valid": True}

print("Phase 5.53 final 151-file staging transport and archived entry points: PASS")
