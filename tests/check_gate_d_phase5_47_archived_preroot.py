#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the Phase 5.47 envelope with exact frozen archive tools."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import pathlib
import tarfile
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
RELEASE = "0.0.0-phase5.47"


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=pathlib.Path)
    archive = parser.parse_args().archive.resolve()
    manifest = json.loads((ROOT / "release/gate-c-representative-build-manifest-phase5.47-v1.json").read_text())
    envelope = json.loads((ROOT / "release/gate-d-pre-root-bootstrap-envelope-phase5.47-v1.json").read_text())
    plan = json.loads((ROOT / "release/gate-d-target-operation-plan-phase5.47-v1.json").read_text())
    instance = json.loads((ROOT / "release/gate-d-execution-instance-phase5.47-v1.json").read_text())
    index = json.loads((ROOT / "release/gate-d-attempts-phase5.47-v1/index.json").read_text())
    if sha(archive) != manifest["candidate"]["archiveSha256"]:
        raise SystemExit("Phase 5.47 release archive identity differs")
    prefix = f"rp1-gpclk-dkms-{RELEASE}"
    identities = {
        identity["sourcePath"]: identity["sourceSha256"]
        for identity in plan["pythonModules"].values()
    }
    identities.update({identity["path"]: identity["sha256"]
                       for identity in index["executors"].values()})
    members = {path: f"{prefix}/{path}" for path in identities}
    with tempfile.TemporaryDirectory() as temporary:
        destination = pathlib.Path(temporary)
        with tarfile.open(archive, "r:gz") as unit:
            for name in members.values():
                member = unit.getmember(name)
                if not member.isfile() or member.issym() or member.islnk():
                    raise SystemExit("Phase 5.47 archived tool is not a regular file")
                unit.extract(member, destination, filter="data")
        outer_path = plan["pythonModules"]["gate_d_outer"]["sourcePath"]
        preroot_path = plan["pythonModules"]["gate_d_preroot"]["sourcePath"]
        outer = destination / members[outer_path]
        preroot = destination / members[preroot_path]
        if sha(outer) != envelope["stagedExecutor"]["sha256"]:
            raise SystemExit("archived outer executor differs from final envelope")
        if sha(preroot) != envelope["preRootModule"]["sha256"]:
            raise SystemExit("archived pre-root module differs from final envelope")
        transitions = {
            item["destination"]: item["sha256"] for item in envelope["transitionFiles"]}
        matrix = instance["executionPolicy"]["matrixPolicy"]
        if transitions.get(matrix) != instance["executionPolicy"]["matrixPolicySha256"]:
            raise SystemExit("qualification-root matrix-policy transition is incomplete")
        for path, expected in identities.items():
            archived = destination / members[path]
            if sha(archived) != expected:
                raise SystemExit(f"archived frozen input differs: {path}")
            if transitions.get(path) != expected:
                raise SystemExit(f"qualification-root transition is incomplete: {path}")
        spec = importlib.util.spec_from_file_location("phase5_47_archived_preroot", preroot)
        if spec is None or spec.loader is None:
            raise SystemExit("cannot load archived Phase 5.47 pre-root module")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert module.validate(envelope) == {"valid": True, "readOnly": True,
                                             "outputDisabled": True}
    print("Phase 5.47 exact archived pre-root envelope validation: PASS")


if __name__ == "__main__":
    main()
