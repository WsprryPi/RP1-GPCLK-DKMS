#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate and remove one exactly identified failed pre-root residue."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import subprocess

SHA = __import__("re").compile(r"[0-9a-f]{64}")
BASELINE = {"moduleLoaded": False, "endpointPresent": False, "overlayActive": False,
            "dkmsTestVersions": False, "liveOutput": False}


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(value: dict) -> dict:
    required = {"SPDX-License-Identifier", "schemaVersion", "kind", "operationId",
                "host", "candidate", "root", "marker", "journal",
                "administratorState", "preservedPaths", "expectedBaseline", "safety"}
    if (not isinstance(value, dict) or set(value) != required or
            value.get("SPDX-License-Identifier") != "MIT" or value.get("schemaVersion") != 1 or
            value.get("kind") != "gate-d-failed-preroot-residue-recovery"):
        raise ValueError("invalid residue-recovery identity")
    if value["host"] != "wspr5" or value["candidate"] != "0.0.0-phase5.24":
        raise ValueError("residue-recovery target differs")
    identities = (value["marker"], value["journal"])
    if any(not isinstance(item, dict) or set(item) != {"path", "sha256"} or
           not pathlib.PurePosixPath(item.get("path", "")).is_absolute() or
           not SHA.fullmatch(item.get("sha256", "")) for item in identities):
        raise ValueError("invalid residue-recovery file identity")
    root = pathlib.PurePosixPath(value["root"])
    if (not root.is_absolute() or root in {pathlib.PurePosixPath("/"), pathlib.PurePosixPath("/home/pi")} or
            pathlib.PurePosixPath(value["marker"]["path"]).parent != root):
        raise ValueError("invalid residue-recovery root")
    admin = value["administratorState"]
    if (not isinstance(admin, dict) or set(admin) != {"path", "expected"} or
            admin.get("expected") != "absent" or not pathlib.PurePosixPath(admin.get("path", "")).is_absolute()):
        raise ValueError("invalid residue-recovery administrator state")
    if value["expectedBaseline"] != BASELINE:
        raise ValueError("residue-recovery baseline differs")
    safety = {"outputDisabled": True, "liveOutput": False, "gpioAccess": False,
              "clockEnabled": False, "dmaActive": False, "sdrActive": False, "rf": False}
    if value["safety"] != safety:
        raise ValueError("residue-recovery safety differs")
    if (not isinstance(value["preservedPaths"], list) or not value["preservedPaths"] or
            any(not pathlib.PurePosixPath(path).is_absolute() for path in value["preservedPaths"])):
        raise ValueError("residue-recovery preservation boundary differs")
    return {"valid": True, "readOnly": True, "outputDisabled": True}


def execute(value: dict, *, prefix: pathlib.Path, probe, execute: bool = False) -> dict:
    validate(value)
    def rooted(raw: str) -> pathlib.Path:
        pure = pathlib.PurePosixPath(raw)
        path = prefix.joinpath(*pure.parts[1:])
        current = prefix
        for part in pure.parts[1:]:
            current /= part
            if current.exists() and current.is_symlink():
                raise ValueError("symlink in residue-recovery path")
        return path
    root = rooted(value["root"]); marker = rooted(value["marker"]["path"])
    journal = rooted(value["journal"]["path"]); administrator = rooted(value["administratorState"]["path"])
    if not root.exists() and not journal.exists() and not marker.exists():
        if probe() != BASELINE: raise ValueError("already-clean residue baseline differs")
        return {"status": "already-clean", "outputDisabled": True}
    if (root.is_symlink() or not root.is_dir() or marker.is_symlink() or not marker.is_file() or
            digest(marker) != value["marker"]["sha256"] or journal.is_symlink() or
            not journal.is_file() or digest(journal) != value["journal"]["sha256"] or
            administrator.exists() or administrator.is_symlink() or probe() != BASELINE):
        raise ValueError("residue-recovery precondition differs")
    children = list(root.iterdir())
    if children != [marker]:
        raise ValueError("residue-recovery root contains unexpected bytes")
    if not execute:
        return {"status": "ready", "readOnly": True, "outputDisabled": True}
    marker.unlink(); root.rmdir(); journal.unlink()
    if probe() != BASELINE:
        raise ValueError("residue-recovery post-state differs")
    return {"status": "complete", "outputDisabled": True}


def live_probe() -> dict:
    overlays = subprocess.run(["/usr/bin/dtoverlay", "-l"], stdout=subprocess.PIPE,
                              text=True, check=False).stdout
    dkms = subprocess.run(["/usr/sbin/dkms", "status"], stdout=subprocess.PIPE,
                          text=True, check=False).stdout
    return {"moduleLoaded": pathlib.Path("/sys/module/rp1_gpclk_dkms").exists(),
            "endpointPresent": pathlib.Path("/dev/rp1-gpclk").exists(),
            "overlayActive": "rp1-gpclk" in overlays,
            "dkmsTestVersions": "rp1-gpclk-dkms/" in dkms, "liveOutput": False}


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("document", type=pathlib.Path)
    parser.add_argument("--execute", action="store_true"); args = parser.parse_args()
    value = json.loads(args.document.read_text(encoding="utf-8"))
    if args.execute and os.geteuid() != 0: raise SystemExit("residue recovery requires root and --execute")
    print(json.dumps(execute(value, prefix=pathlib.Path("/"), probe=live_probe,
                             execute=args.execute), indent=2, sort_keys=True))


if __name__ == "__main__": main()
