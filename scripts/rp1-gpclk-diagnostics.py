#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Bounded, read-only RP1-GPCLK-DKMS diagnostic summary."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import platform
import subprocess


def text(path: pathlib.Path, limit: int = 4096) -> str | None:
    try:
        if path.is_symlink() or not path.is_file():
            return None
        value = path.read_text(errors="replace")
        return value[:limit].strip()
    except OSError:
        return None


def command(args: list[str], limit: int = 8192) -> dict:
    try:
        result = subprocess.run(args, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, timeout=5, check=False, env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin"})
        return {"exitStatus": result.returncode, "stdout": result.stdout[:limit], "stderr": result.stderr[:limit]}
    except (FileNotFoundError, subprocess.TimeoutExpired) as error:
        return {"error": type(error).__name__}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-directory", type=pathlib.Path)
    args = parser.parse_args()
    module = pathlib.Path("/sys/module/rp1_gpclk_dkms")
    device = pathlib.Path("/dev/rp1-gpclk")
    report = {
        "SPDX-License-Identifier": "MIT", "schemaVersion": 1, "readOnly": True,
        "limits": {"commandSeconds": 5, "streamBytes": 8192, "fileBytes": 4096},
        "system": {"kernel": platform.release(), "architecture": platform.machine(), "model": text(pathlib.Path("/proc/device-tree/model"))},
        "dkms": command(["dkms", "status", "-m", "rp1-gpclk-dkms"]),
        "module": {"loaded": module.is_dir(), "liveOutput": text(module / "parameters/live_output")},
        "device": {"present": device.exists()}
    }
    if device.exists():
        status = device.stat()
        report["device"].update({"uid": status.st_uid, "gid": status.st_gid, "mode": f"{status.st_mode & 0o777:04o}"})
    if args.release_directory:
        supplied_release = args.release_directory
        release = supplied_release.resolve()
        report["release"] = {"path": str(release), "realDirectory": supplied_release.is_dir() and not supplied_release.is_symlink()}
        for name in ("release-metadata.json", "rp1-gpclk-compatibility-manifest.json", "SHA256SUMS"):
            path = release / name
            if path.is_file() and not path.is_symlink():
                report["release"][name] = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
