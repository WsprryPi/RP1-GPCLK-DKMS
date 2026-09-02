#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Read-only product/qualification state probe for same-version transition."""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess

FIXED_ENV = {"PATH": "/usr/sbin:/usr/bin:/sbin:/bin"}


def real_marker(root: pathlib.Path, raw: str) -> bool:
    value = pathlib.PurePosixPath(raw)
    if not value.is_absolute() or ".." in value.parts:
        raise ValueError("unsafe same-version marker path")
    path = root.joinpath(*value.parts[1:])
    return path.is_file() and not path.is_symlink()


def capture(root: pathlib.Path, product_marker: str, qualification_marker: str,
            command=subprocess.run) -> dict:
    overlays = command(["/usr/bin/dtoverlay", "-l"], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, text=True, check=False,
                       env=FIXED_ENV).stdout
    dkms = command(["/usr/sbin/dkms", "status"], stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE, text=True, check=False,
                   env=FIXED_ENV).stdout
    module = root / "sys/module/rp1_gpclk_dkms"
    endpoint = root / "dev/rp1-gpclk"
    if module.exists() or endpoint.exists() or "rp1-gpclk" in overlays:
        raise ValueError("same-version probe found active runtime state")
    product = real_marker(root, product_marker)
    qualification = real_marker(root, qualification_marker)
    if qualification and not product:
        raise ValueError("qualification exists without product")
    if product != ("rp1-gpclk-dkms/0.0.0-phase5.53" in dkms):
        raise ValueError("product marker and DKMS state differ")
    return {"product": product, "qualification": qualification,
            "outputActive": False}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product-marker", required=True)
    parser.add_argument("--qualification-marker", required=True)
    args = parser.parse_args()
    print(json.dumps(capture(pathlib.Path("/"), args.product_marker,
                             args.qualification_marker), sort_keys=True))


if __name__ == "__main__":
    main()
