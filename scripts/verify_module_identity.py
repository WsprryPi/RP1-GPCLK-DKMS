#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Verify exact unstripped and DKMS-installed RP1 GPCLK module identities."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
ENTRY = "v1.0.1-wspr5-gpio4-6.18.34"
TRANSFORM = "strip --strip-debug; hash uncompressed ELF before filesystem compression"


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("module", type=pathlib.Path)
    parser.add_argument(
        "--manifest",
        type=pathlib.Path,
        default=ROOT / "release/compatibility-decisions-v1.json",
    )
    args = parser.parse_args()
    module = args.module.resolve()
    if module.is_symlink() or not module.is_file():
        raise SystemExit("module must be a real file")
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    entry = next((item for item in manifest["entries"] if item["id"] == ENTRY), None)
    if entry is None:
        raise SystemExit("exact GPIO4 compatibility entry is absent")
    build = entry["build"]
    if build.get("moduleInstalledTransform") != TRANSFORM:
        raise SystemExit("installed-module transform differs")
    raw = sha256(module)
    if raw != build["moduleUnsignedSha256"]:
        raise SystemExit("unstripped module identity differs")
    strip = shutil.which("strip")
    if strip is None:
        raise SystemExit("strip is unavailable")
    with tempfile.TemporaryDirectory(prefix="rp1-gpclk-module-identity-") as directory:
        installed = pathlib.Path(directory) / "rp1_gpclk_dkms.ko"
        shutil.copyfile(module, installed)
        subprocess.run([strip, "--strip-debug", str(installed)], check=True)
        normalized = sha256(installed)
    if normalized != build["moduleInstalledSha256"]:
        raise SystemExit("normalized installed module identity differs")
    print(json.dumps({
        "entry": ENTRY,
        "moduleUnsignedSha256": raw,
        "moduleInstalledSha256": normalized,
        "moduleInstalledTransform": TRANSFORM,
        "valid": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
