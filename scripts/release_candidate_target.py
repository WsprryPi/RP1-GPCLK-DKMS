#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Exact 1.0.0 output-disabled target verification controls."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import subprocess
import sys

MODULE = "rp1_gpclk_dkms"
PACKAGE = "rp1-gpclk-dkms"
MODULE_VERSION = "1.0.0"
PACKAGE_VERSION = "1.0.0-1"
UAPI = Path("/usr/src/rp1-gpclk-dkms-1.0.0/include/uapi/linux/rp1_gpclk.h")
ENDPOINT = Path("/dev/rp1-gpclk")
LIVE = Path("/sys/module/rp1_gpclk_dkms/parameters/live_output")
HASHES = {
    "uapi": "1d411644352e61402bd4685a5692070d543ab2ee5b016d394294aa98970bd7fb",
    "gpio4": "c3e17a685694928468bb18c24f5bb4e25454745d6989e6c9d2c2acf447b908d6",
    "gpio20": "8eaa8afae7f88a665fc9bec6da1b013be049b2a32c909c729caeff9181bcf3aa",
}


def command(argv: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, check=check, text=True, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_identity() -> tuple[str, str]:
    result = command(["/usr/bin/dpkg-query", "-W", "-f=${Status}|${Version}", PACKAGE])
    status, version = result.stdout.strip().split("|", 1)
    return status, version


def active_overlays() -> int:
    result = command(["/usr/bin/sudo", "-n", "/usr/bin/dtoverlay", "-l"])
    return sum(1 for line in result.stdout.splitlines() if line.split(":", 1)[0].isdigit())


def inactive(expect_version: str) -> None:
    status, version = package_identity()
    if status != "install ok installed" or version != expect_version:
        raise RuntimeError(f"package identity differs: {status}|{version}")
    if any(line.startswith(f"{MODULE} ") for line in Path("/proc/modules").read_text().splitlines()):
        raise RuntimeError("module is loaded")
    if ENDPOINT.exists() or active_overlays() != 0:
        raise RuntimeError("endpoint or runtime overlay is active")
    config = Path("/boot/firmware/config.txt").read_text()
    if any(line.strip().startswith(("dtoverlay=rp1-gpclk-gpio4", "dtoverlay=rp1-gpclk-gpio20"))
           for line in config.splitlines()):
        raise RuntimeError("boot overlay is selected")
    if expect_version == PACKAGE_VERSION:
        if digest(UAPI) != HASHES["uapi"]:
            raise RuntimeError("installed UAPI differs")
        for route in ("gpio4", "gpio20"):
            canonical = Path(f"/usr/lib/rp1-gpclk-dkms/overlays/rp1-gpclk-{route}.dtbo")
            boot = Path(f"/boot/firmware/overlays/rp1-gpclk-{route}.dtbo")
            if digest(canonical) != HASHES[route] or digest(boot) != HASHES[route]:
                raise RuntimeError(f"installed {route} overlay differs")


def compile_probe(root: Path) -> Path:
    source = root / "tools/gate_d_uapi_probe.c"
    output = root / "gate_d_uapi_probe"
    command(["/usr/bin/cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
             "-I/usr/src/rp1-gpclk-dkms-1.0.0/include/uapi", str(source), "-o", str(output)])
    return output


def route_attempt(route: str) -> None:
    inactive(PACKAGE_VERSION)
    root = Path(__file__).resolve().parents[1]
    probe = compile_probe(root)
    overlay_id: str | None = None
    loaded = False
    try:
        command(["/usr/bin/sudo", "-n", "/usr/sbin/modprobe", MODULE, "live_output=0"])
        loaded = True
        if LIVE.read_text().strip() not in {"N", "0"}:
            raise RuntimeError("live output gate is not disabled")
        applied = command(["/usr/bin/sudo", "-n", "/usr/bin/dtoverlay", f"rp1-gpclk-{route}"])
        overlay_id = applied.stdout.strip().splitlines()[-1].strip()
        if not overlay_id.isdigit():
            raise RuntimeError("runtime overlay identifier is invalid")
        command(["/usr/bin/sudo", "-n", "/usr/bin/udevadm", "settle"])
        if not ENDPOINT.exists() or LIVE.read_text().strip() not in {"N", "0"}:
            raise RuntimeError("disabled endpoint did not appear")
        command(["/usr/bin/sudo", "-n", str(probe), route, MODULE_VERSION])
        command(["/usr/bin/sudo", "-n", "/usr/bin/dtoverlay", "-r", overlay_id])
        overlay_id = None
        if ENDPOINT.exists():
            raise RuntimeError("endpoint remained after overlay removal")
        command(["/usr/bin/sudo", "-n", "/usr/sbin/rmmod", MODULE])
        loaded = False
        inactive(PACKAGE_VERSION)
    finally:
        if overlay_id is not None:
            command(["/usr/bin/sudo", "-n", "/usr/bin/dtoverlay", "-r", overlay_id], check=False)
        if loaded:
            command(["/usr/bin/sudo", "-n", "/usr/sbin/rmmod", MODULE], check=False)
        probe.unlink(missing_ok=True)


def remove_audit() -> None:
    inactive(PACKAGE_VERSION)
    command(["/usr/bin/sudo", "-n", "/usr/bin/dpkg", "--remove", PACKAGE])
    if command(["/usr/bin/dpkg-query", "-W", PACKAGE], check=False).returncode == 0:
        raise RuntimeError("package remains after removal")
    for path in (Path("/usr/src/rp1-gpclk-dkms-1.0.0"), Path("/usr/lib/rp1-gpclk-dkms"),
                 Path("/boot/firmware/overlays/rp1-gpclk-gpio4.dtbo"),
                 Path("/boot/firmware/overlays/rp1-gpclk-gpio20.dtbo")):
        if path.exists():
            raise RuntimeError(f"owned residue remains: {path}")
    if command(["/usr/bin/sudo", "-n", "/usr/sbin/dkms", "status", f"{PACKAGE}/{MODULE_VERSION}"],
               check=False).stdout.strip():
        raise RuntimeError("DKMS residue remains")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("preflight", "verify-inactive", "route", "remove-audit"))
    parser.add_argument("--expect-version")
    parser.add_argument("--route", choices=("gpio4", "gpio20"))
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.action in {"route", "remove-audit"} and not args.execute:
        raise SystemExit("mutating action requires --execute and separate authorization")
    if args.action in {"preflight", "verify-inactive"}:
        if not args.expect_version:
            raise SystemExit("--expect-version is required")
        inactive(args.expect_version)
    elif args.action == "route":
        if not args.route:
            raise SystemExit("--route is required")
        route_attempt(args.route)
    else:
        remove_audit()
    print(f"release candidate target {args.action}: PASS")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"release candidate target: FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
