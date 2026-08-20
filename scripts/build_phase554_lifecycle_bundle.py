#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build a deterministic, qualification-only Phase 5.54 control bundle."""

from __future__ import annotations

import argparse
import gzip
import io
import pathlib
import tarfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
MEMBERS = (
    "release/phase5.54-lifecycle-attempt1-v1.json",
    "scripts/phase554_lifecycle_controls.py",
    "tools/gate_d_uapi_probe.c",
)
PREFIX = "rp1-gpclk-dkms-phase5.54-lifecycle-controls"


def build(output: pathlib.Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for relative in MEMBERS:
            source = ROOT / relative
            data = source.read_bytes()
            info = tarfile.TarInfo(f"{PREFIX}/{pathlib.Path(relative).name}")
            info.size = len(data)
            info.mode = 0o755 if source.suffix == ".py" else 0o644
            info.uid = info.gid = 0
            info.uname = info.gname = "root"
            info.mtime = 0
            archive.addfile(info, io.BytesIO(data))
    with output.open("wb") as target:
        with gzip.GzipFile(filename="", mode="wb", fileobj=target, mtime=0) as zipped:
            zipped.write(raw.getvalue())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=pathlib.Path)
    args = parser.parse_args()
    build(args.output)


if __name__ == "__main__":
    main()
