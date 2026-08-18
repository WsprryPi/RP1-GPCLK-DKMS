#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate additive eight-role pre-root release-input handling."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import pathlib
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("gate_d_preroot_split", ROOT / "scripts/gate_d_preroot.py")
assert spec and spec.loader
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

legacy = json.loads((ROOT / "release/gate-d-pre-root-bootstrap-envelope-phase5.52-v1.json").read_text())
split = copy.deepcopy(legacy)
split["schemaVersion"] = 6
release = split["candidate"]["release"]
parent = pathlib.PurePosixPath(split["candidate"]["archivePath"]).parent
qualification = {
    "role": "qualificationArchive",
    "path": str(parent / f"rp1-gpclk-dkms-qualification-{release}.tar.gz"),
    "sha256": "a" * 64,
}
split["releaseInputs"].append(qualification)
split["inputFiles"].append({"path": qualification["path"], "sha256": qualification["sha256"]})
assert tool.validate(split)["outputDisabled"] is True
assert tool.validate(legacy)["outputDisabled"] is True

for mutate in (
    lambda value: value["releaseInputs"].pop(),
    lambda value: value["releaseInputs"][-1].update(role="archive"),
    lambda value: value["releaseInputs"][-1].update(path=str(parent / "qualification.tar.gz")),
    lambda value: value["releaseInputs"][-1].update(path="/other/rp1-gpclk-dkms-qualification-0.0.0-phase5.52.tar.gz"),
):
    invalid = copy.deepcopy(split)
    mutate(invalid)
    try:
        tool.validate(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid split release-input graph accepted")


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


with tempfile.TemporaryDirectory() as temporary:
    prefix = pathlib.Path(temporary)
    staging = prefix / "staging"
    staging.mkdir()
    role_names = tool.release_input_roles(6, "0.0.0-phase5.53")
    paths = {}
    for role, name in role_names.items():
        if role == "checksums":
            continue
        path = staging / name
        path.write_bytes(f"{role}\n".encode())
        paths[role] = path
    checksums = staging / "SHA256SUMS"
    checksums.write_text("".join(
        f"{sha(path)}  {path.name}\n" for path in sorted(paths.values(), key=lambda item: item.name)))
    paths["checksums"] = checksums
    value = {
        "schemaVersion": 6,
        "candidate": {"release": "0.0.0-phase5.53"},
        "releaseInputs": [
            {"role": role, "path": f"/staging/{path.name}", "sha256": sha(path)}
            for role, path in paths.items()
        ],
    }
    tool.validate_release_inputs(value, prefix=prefix)
    checksums.write_text(checksums.read_text().replace(sha(paths["qualificationArchive"]), "0" * 64))
    value["releaseInputs"][-1]["sha256"] = sha(checksums)
    try:
        tool.validate_release_inputs(value, prefix=prefix)
    except ValueError:
        pass
    else:
        raise AssertionError("stale qualification checksum accepted")

print("Gate D split pre-root release inputs: PASS")
