#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the final Phase 5.43 envelope using exact release-archive tools."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import pathlib
import tarfile
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
RELEASE = "0.0.0-phase5.43"


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=pathlib.Path)
    args = parser.parse_args()
    archive = args.archive.resolve()
    manifest = json.loads((ROOT / "release/gate-c-representative-build-manifest-phase5.43-v1.json").read_text())
    envelope = json.loads((ROOT / "release/gate-d-pre-root-bootstrap-envelope-phase5.43-v1.json").read_text())
    if sha(archive) != manifest["candidate"]["archiveSha256"]:
        raise SystemExit("Phase 5.43 release archive identity differs")
    prefix = f"rp1-gpclk-dkms-{RELEASE}"
    members = {
        "outer": f"{prefix}/scripts/gate_d_outer.py",
        "preroot": f"{prefix}/scripts/gate_d_preroot.py",
    }
    with tempfile.TemporaryDirectory() as temporary:
        destination = pathlib.Path(temporary)
        with tarfile.open(archive, "r:gz") as unit:
            names = set(unit.getnames())
            if not set(members.values()).issubset(names):
                raise SystemExit("Phase 5.43 archive tool graph is incomplete")
            for name in members.values():
                member = unit.getmember(name)
                if not member.isfile() or member.issym() or member.islnk():
                    raise SystemExit("Phase 5.43 archived tool is not a regular file")
                unit.extract(member, destination, filter="data")
        outer = destination / members["outer"]
        preroot = destination / members["preroot"]
        if sha(outer) != envelope["stagedExecutor"]["sha256"]:
            raise SystemExit("archived outer executor differs from final envelope")
        if sha(preroot) != envelope["preRootModule"]["sha256"]:
            raise SystemExit("archived pre-root module differs from final envelope")
        spec = importlib.util.spec_from_file_location("phase5_43_archived_preroot", preroot)
        if spec is None or spec.loader is None:
            raise SystemExit("cannot load archived pre-root module")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.validate(envelope)
        if result != {"valid": True, "readOnly": True, "outputDisabled": True}:
            raise SystemExit("archived pre-root validation result differs")
    print("Phase 5.43 exact archived pre-root envelope validation: PASS")


if __name__ == "__main__":
    main()
