#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Read-only post-reboot validation for one exact, output-disabled route."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

MODULE = "rp1_gpclk_dkms"
PACKAGE = "rp1-gpclk-dkms"
MODULE_VERSION = "1.1.1"
PACKAGE_VERSION = "1.1.1-1"
ENDPOINT = Path("/dev/rp1-gpclk")
LIVE = Path("/sys/module/rp1_gpclk_dkms/parameters/live_output")
DT_ROOT = Path("/proc/device-tree")
COMPATIBLE = b"wsprrypi,rp1-gpclk-dkms-v1\x00"
ROUTES = {"gpio4": (1, 4), "gpio20": (2, 20)}


def command(argv: list[str]) -> str:
    return subprocess.run(argv, check=True, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT).stdout


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def endpoint_nodes() -> list[Path]:
    nodes = []
    for compatible in DT_ROOT.rglob("compatible"):
        try:
            if compatible.read_bytes() == COMPATIBLE:
                nodes.append(compatible.parent)
        except OSError:
            continue
    return nodes


def be32(path: Path) -> int:
    raw = path.read_bytes()
    if len(raw) != 4:
        raise RuntimeError(f"malformed DT scalar: {path}")
    return int.from_bytes(raw, "big")


def verify(route: str) -> None:
    root = Path(__file__).resolve().parents[1]
    identity = json.loads((root / "QUALIFICATION.json").read_text())
    if (identity.get("release"), identity.get("debianVersion")) != (
            MODULE_VERSION, PACKAGE_VERSION):
        raise RuntimeError("qualification identity version differs")
    status = command(["/usr/bin/dpkg-query", "-W", "-f=${Status}|${Version}", PACKAGE]).strip()
    if status != f"install ok installed|{PACKAGE_VERSION}":
        raise RuntimeError(f"package identity differs: {status}")
    installed = {
        "uapiSha256": Path(f"/usr/src/{PACKAGE}-{MODULE_VERSION}/include/uapi/linux/rp1_gpclk.h"),
        "gpio4DtboSha256": Path("/usr/lib/rp1-gpclk-dkms/overlays/rp1-gpclk-gpio4.dtbo"),
        "gpio20DtboSha256": Path("/usr/lib/rp1-gpclk-dkms/overlays/rp1-gpclk-gpio20.dtbo"),
    }
    for field, path in installed.items():
        if not path.is_file() or digest(path) != identity[field]:
            raise RuntimeError(f"installed identity differs: {field}")
    nodes = endpoint_nodes()
    if len(nodes) != 1:
        raise RuntimeError(f"expected one live endpoint node, found {len(nodes)}")
    expected_route, expected_pin = ROUTES[route]
    node = nodes[0]
    if be32(node / "wsprrypi,route") != expected_route or be32(node / "wsprrypi,pin") != expected_pin:
        raise RuntimeError("live DT route identity differs")
    if not any(line.startswith(f"{MODULE} ") for line in Path("/proc/modules").read_text().splitlines()):
        raise RuntimeError("module is not loaded")
    if not LIVE.is_file() or LIVE.read_text().strip() not in {"N", "0"}:
        raise RuntimeError("live output is not disabled")
    if not ENDPOINT.exists() or Path("/dev/rp1-gpclk0").exists():
        raise RuntimeError("canonical endpoint publication differs")
    matches = []
    for link in Path("/sys/bus/platform/devices").glob("*/of_node"):
        try:
            if link.resolve() == node.resolve():
                matches.append(link.parent)
        except OSError:
            continue
    if len(matches) != 1:
        raise RuntimeError(f"expected one platform device, found {len(matches)}")
    driver = matches[0] / "driver"
    if not driver.is_symlink() or driver.resolve().name != "rp1-gpclk-dkms":
        raise RuntimeError("endpoint is not bound to the candidate driver")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", required=True, choices=tuple(ROUTES))
    args = parser.parse_args()
    verify(args.route)
    print(f"output-disabled rebooted route {args.route}: PASS")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        print(f"output-disabled rebooted route: FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
