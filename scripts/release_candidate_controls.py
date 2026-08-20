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
    if identity.get("release") != "1.0.0" or identity.get("expectedTag") != "v1.0.0":
        raise ValueError("qualification release identity differs")
    if inventory.get("debianVersion") != "1.0.0-1":
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
        "read-only-preflight", "validated-transfer", "verify-inactive-current",
        "gpio4-output-disabled-lifecycle",
        "gpio20-output-disabled-lifecycle", "complete-removal-residue-audit",
        "reinstall-final-package", "verify-final-inactive-baseline",
    ]
    if not isinstance(steps, list) or [step.get("id") for step in steps] != expected:
        raise ValueError("target plan steps differ")
    for step in steps:
        if set(step) != {"id", "argv", "mutating", "requiresAuthorization"}:
            raise ValueError(f"invalid target step fields: {step.get('id')}")
        if not isinstance(step["argv"], list) or not step["argv"]:
            raise ValueError(f"invalid target step argv: {step['id']}")
        if step["mutating"] and not step["requiresAuthorization"]:
            raise ValueError(f"mutating step lacks authorization gate: {step['id']}")
        for argument in step["argv"]:
            if argument.startswith("scripts/") and not (root / argument).is_file():
                raise ValueError(f"invoked qualification member is absent: {argument}")
    transfer = next(step for step in steps if step["id"] == "validated-transfer")
    if transfer["argv"] != ["/usr/bin/sha256sum", "--check", "SHA256SUMS"]:
        raise ValueError("transfer step does not enforce the complete checksum set")
    safety = plan.get("safety", {})
    if safety != {
        "liveOutput": False, "clockOrRateChange": False, "dma": False,
        "gpioOutput": False, "bootChange": False, "reboot": False,
        "transmissionOrRf": False,
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
            print(json.dumps({"id": step["id"], "argv": step["argv"]}, separators=(",", ":")))
    else:
        print("Release 1.0.0 target controls: PASS (offline, unauthorized)")


if __name__ == "__main__":
    main()
