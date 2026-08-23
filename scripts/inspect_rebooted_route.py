#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Read-only post-reboot validation for one exact, output-disabled route."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

MODULE = "rp1_gpclk_dkms"
PACKAGE = "rp1-gpclk-dkms"
MODULE_VERSION = "1.1.2"
PACKAGE_VERSION = "1.1.2-1"
ENDPOINT = Path("/dev/rp1-gpclk")
LIVE = Path("/sys/module/rp1_gpclk_dkms/parameters/live_output")
DT_ROOT = Path("/proc/device-tree")
COMPATIBLE = b"wsprrypi,rp1-gpclk-dkms-v1\x00"
ROUTES = {"gpio4": (1, 4), "gpio20": (2, 20)}
EVIDENCE_ROOT = Path("/var/lib/rp1-gpclk-dkms/validation-1.1.2-service/evidence")


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


def atomic_evidence(path: Path, value: dict) -> str:
    if not path.is_absolute() or path.parent != EVIDENCE_ROOT:
        raise RuntimeError("evidence path is outside the owned directory")
    if path.parent.exists() and path.parent.is_symlink():
        raise RuntimeError("evidence directory is unsafe")
    if path.exists() or path.is_symlink():
        raise RuntimeError(f"refusing existing evidence path: {path}")
    path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    payload = json.dumps(value, indent=2, sort_keys=True).encode() + b"\n"
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
    return hashlib.sha256(payload).hexdigest()


def verify(route: str) -> dict:
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
    module_path = Path(command(["/usr/sbin/modinfo", "-n", MODULE]).strip())
    if not module_path.is_file():
        raise RuntimeError("installed module file is absent")
    signer = command(["/usr/sbin/modinfo", "-F", "signer", MODULE]).strip()
    sig_id = command(["/usr/sbin/modinfo", "-F", "sig_id", MODULE]).strip()
    endpoint_stat = ENDPOINT.stat()
    open_fds = 0
    for fd in Path("/proc").glob("[0-9]*/fd/*"):
        try:
            observed = fd.stat()
        except OSError:
            continue
        open_fds += ((observed.st_dev, observed.st_ino) ==
                     (endpoint_stat.st_dev, endpoint_stat.st_ino))
    if open_fds:
        raise RuntimeError("canonical endpoint is open")
    pins = {str(pin): command(["/usr/bin/pinctrl", "get", str(pin)]).strip()
            for pin in (4, 20)}
    if any(not re.search(rf"^{pin}:\s+(ip|no)\b", line)
           for pin, line in pins.items()):
        raise RuntimeError("GPIO cleanup state is not input-disabled")
    clocks = []
    summary = Path("/sys/kernel/debug/clk/clk_summary")
    if summary.is_file():
        clocks = [line.strip() for line in summary.read_text().splitlines()
                  if line.split() and line.split()[0] == "clk_gp0"]
        if len(clocks) != 1 or clocks[0].split()[1:3] != ["0", "0"]:
            raise RuntimeError("GPCLK0 cleanup state is not disabled")
    return {
        "schemaVersion": 1, "kind": "rp1-gpclk-output-disabled-route-inspection",
        "route": route, "release": MODULE_VERSION, "packageVersion": PACKAGE_VERSION,
        "sourceCommit": identity["sourceCommit"], "qualificationIdentity": identity,
        "deviceTreeNode": str(node), "deviceTreeRoute": expected_route,
        "deviceTreePin": expected_pin, "platformDevice": str(matches[0]),
        "driver": driver.resolve().name, "endpoint": str(ENDPOINT),
        "endpointOpenFileDescriptors": open_fds, "module": MODULE,
        "modulePath": str(module_path), "moduleFileSha256": digest(module_path),
        "moduleSigner": signer or "none", "moduleSignatureId": sig_id or "none",
        "liveOutput": False, "clockSummary": clocks, "pinctrl": pins,
        "cleanup": {"endpointClosed": True, "clockDisabled": True,
                    "gpioNonOutput": True},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--route", required=True, choices=tuple(ROUTES))
    parser.add_argument("--evidence", required=True, type=Path)
    args = parser.parse_args()
    result = verify(args.route)
    evidence_hash = atomic_evidence(args.evidence, result)
    print(json.dumps({"status": "PASS", "route": args.route,
                      "evidence": str(args.evidence), "sha256": evidence_hash}, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        print(f"output-disabled rebooted route: FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
