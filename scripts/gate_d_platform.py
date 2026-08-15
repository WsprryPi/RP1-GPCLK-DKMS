#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Exact output-disabled platform unbind/rebind helper for Gate D."""

from __future__ import annotations

import argparse
import json
import os
import pathlib

MODULE = "rp1_gpclk_dkms"
DRIVER = pathlib.Path("/sys/bus/platform/drivers/rp1-gpclk-dkms")
PARAMETER = pathlib.Path(f"/sys/module/{MODULE}/parameters/live_output")
ENDPOINT = pathlib.Path("/dev/rp1-gpclk")


def output_disabled() -> bool:
    return PARAMETER.is_file() and PARAMETER.read_text().strip() in {"N", "0", "false", "False"}


def bound_devices() -> list[str]:
    if DRIVER.is_symlink() or not DRIVER.is_dir():
        raise ValueError("platform driver directory is absent or unsafe")
    return sorted(path.name for path in DRIVER.iterdir()
                  if path.is_symlink() and path.name != "module")


def control_write(path: pathlib.Path, device: str) -> None:
    path.write_text(device, encoding="ascii")


def cycle(write_control=control_write, administrator_uid: int | None = None) -> dict:
    uid = os.geteuid() if administrator_uid is None else administrator_uid
    if uid != 0:
        raise PermissionError("root required")
    if not output_disabled():
        raise ValueError("immutable output-disabled gate is not proven")
    devices = bound_devices()
    if len(devices) != 1:
        raise ValueError("exactly one bound platform device is required")
    device = devices[0]
    write_control(DRIVER / "unbind", device)
    if bound_devices() or ENDPOINT.exists():
        raise ValueError("unbind did not remove the exact endpoint")
    write_control(DRIVER / "bind", device)
    if bound_devices() != [device] or not ENDPOINT.exists() or not output_disabled():
        raise ValueError("rebind identity or output-disabled gate differs")
    return {"device": device, "unbindBind": True, "liveOutput": False}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("status", "unbind-bind-cycle"))
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.action == "status":
        result = {"devices": bound_devices(), "liveOutput": not output_disabled(), "readOnly": True}
    else:
        if not args.execute:
            raise SystemExit("unbind/rebind requires --execute")
        result = cycle()
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
