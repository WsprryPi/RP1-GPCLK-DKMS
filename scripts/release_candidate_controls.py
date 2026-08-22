#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate and render the offline-prepared exact release-candidate target plan."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(root: Path) -> dict:
    identity_path = root / "QUALIFICATION.json"
    inventory_path = root / "PRODUCT-INVENTORY.json"
    plan_path = root / "TARGET-VERIFICATION.json"
    identity = json.loads(identity_path.read_text())
    inventory = json.loads(inventory_path.read_text())
    plan = json.loads(plan_path.read_text())
    if identity.get("release") != "1.1.1" or identity.get("expectedTag") != "v1.1.1":
        raise ValueError("qualification release identity differs")
    if inventory.get("debianVersion") != "1.1.1-1":
        raise ValueError("product inventory version differs")
    if plan.get("kind") != "release-candidate-target-verification" or plan.get("schemaVersion") != 1:
        raise ValueError("target plan identity differs")
    if plan.get("authorized") is not False or plan.get("executed") is not False:
        raise ValueError("offline target plan claims authorization or execution")
    if plan.get("physicalSafety") != {
        "si5351PathDisconnected": "fresh-operator-confirmation-required",
        "antennaOrTransmitterDisconnected": "fresh-operator-confirmation-required",
    }:
        raise ValueError("fresh physical-safety confirmation is not required")
    if plan.get("productPackageSha256") != identity.get("productPackageSha256"):
        raise ValueError("target plan product identity differs")
    if plan.get("productInventorySha256") != sha256(inventory_path):
        raise ValueError("target plan product inventory differs")
    if plan.get("qualificationIdentitySha256") != sha256(identity_path):
        raise ValueError("target plan qualification identity differs")
    steps = plan.get("steps")
    expected = [
        "validated-transfer", "bootstrap-create", "bootstrap-extract-archive",
        "bootstrap-authenticate", "bootstrap-controls", "read-only-preflight",
        "quiesce-services",
        "deactivate-predecessor-and-reboot",
        "reconcile-inactive-predecessor", "install-inactive-package",
        "select-gpio4-and-reboot", "reconcile-gpio4", "inspect-gpio4-output-disabled",
        "select-gpio20-and-reboot", "reconcile-gpio20", "inspect-gpio20-output-disabled",
        "restore-gpio4-and-reboot", "reconcile-restored-gpio4",
        "inspect-restored-gpio4-output-disabled",
        "restore-services",
        "residue-and-service-audit",
        "checksum-evidence",
    ]
    if not isinstance(steps, list) or [step.get("id") for step in steps] != expected:
        raise ValueError("target plan steps differ")
    for step in steps:
        allowed = {"id", "argv", "action", "mutating", "requiresAuthorization",
                   "rebootRequired"}
        if not set(step) <= allowed or not {"id", "mutating", "requiresAuthorization"} <= set(step):
            raise ValueError(f"invalid target step fields: {step.get('id')}")
        if "action" in step or "argv" not in step:
            raise ValueError(f"target step is not executable: {step['id']}")
        if not isinstance(step["argv"], list) or not step["argv"]:
            raise ValueError(f"invalid target step argv: {step['id']}")
        if step["mutating"] and not step["requiresAuthorization"]:
            raise ValueError(f"mutating step lacks authorization gate: {step['id']}")
        for argument in step.get("argv", []):
            if not isinstance(argument, str) or not argument.endswith(".py"):
                continue
            marker = "/rp1-gpclk-dkms-qualification-1.1.1/scripts/"
            relative = (argument if argument.startswith("scripts/") else
                        f"scripts/{argument.rsplit(marker, 1)[1]}" if marker in argument else None)
            if relative is not None and not (root / relative).is_file():
                raise ValueError(f"invoked qualification member is absent: {relative}")
    transfer = next(step for step in steps if step["id"] == "validated-transfer")
    if transfer["argv"] != [
            "/usr/bin/env",
            "--chdir=/home/pi/rp1-gpclk-v1.1.1-owned-service-executor-20260822/release-set",
            "/usr/bin/sha256sum", "--check", "SHA256SUMS"]:
        raise ValueError("transfer step does not enforce the complete checksum set")
    safety = plan.get("safety", {})
    if safety != {
        "liveOutput": False, "endpointAcquire": False,
        "clockOrRateChange": False, "dma": False, "gpioOutput": False,
        "carrier": False, "sdrCapture": False, "transmissionOrRf": False,
        "bootChange": True, "reboot": True,
    }:
        raise ValueError("target plan safety boundary differs")
    return plan


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args()
    plan = validate(args.root.resolve())
    if args.render:
        for step in plan["steps"]:
            print(json.dumps(step, separators=(",", ":")))
    else:
        print("Release 1.1.1 target controls: PASS (offline, unauthorized)")


if __name__ == "__main__":
    main()
