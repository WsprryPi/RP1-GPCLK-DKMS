#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate and render a bounded Phase 5.54 route lifecycle control package."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import shlex

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_PLAN = ROOT / "release/phase5.54-lifecycle-attempt1-v1.json"
SHA256 = "0123456789abcdef"


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: pathlib.Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("plan must be an object")
    return value


def validate(plan: dict) -> None:
    assert plan["schemaVersion"] == 1
    assert plan["kind"] == "phase5.54-output-disabled-lifecycle-attempt"
    attempt = plan["attempt"]
    route = plan["route"]
    assert (attempt, route) in {(1, "gpio4"), (2, "gpio20")}
    assert plan["packageVersion"] == "0.0.0~phase5.54-2"
    assert plan["moduleVersion"] == "0.0.0-phase5.54"
    assert plan["authorization"] == "not-authorized-for-target-execution"
    assert plan["preconditions"]["moduleLoaded"] is False
    assert plan["preconditions"]["endpointPresent"] is False
    assert plan["preconditions"]["activeOverlayCount"] == 0
    assert plan["preconditions"]["bootSelectionCount"] == 0
    assert plan["preconditions"]["antennaConnected"] is False
    assert plan["terminalRequirements"]["packageUnchanged"] is True
    if attempt == 2:
        assert plan["predecessorAttemptEvidenceCommit"] == \
            "4018b0ef2334fac759be49a5af1f6d3bd67676d6"
        assert plan["preconditions"]["gpio4AttemptPassed"] is True

    paths = plan["paths"]
    expected = {
        "uapi": "/usr/src/rp1-gpclk-dkms-0.0.0-phase5.54/include/uapi/linux/rp1_gpclk.h",
        "canonicalOverlay": f"/usr/lib/rp1-gpclk-dkms/overlays/rp1-gpclk-{route}.dtbo",
        "bootOverlay": f"/boot/firmware/overlays/rp1-gpclk-{route}.dtbo",
        "endpoint": "/dev/rp1-gpclk",
        "liveOutputParameter": "/sys/module/rp1_gpclk_dkms/parameters/live_output",
    }
    assert set(paths) == set(expected)
    for key, literal in expected.items():
        assert paths[key]["path"] == literal
        if "sha256" in paths[key]:
            value = paths[key]["sha256"]
            assert len(value) == 64 and all(char in SHA256 for char in value)
    assert paths["canonicalOverlay"]["sha256"] == paths["bootOverlay"]["sha256"]
    overlay_hash = {
        "gpio4": "c3e17a685694928468bb18c24f5bb4e25454745d6989e6c9d2c2acf447b908d6",
        "gpio20": "8eaa8afae7f88a665fc9bec6da1b013be049b2a32c909c729caeff9181bcf3aa",
    }
    assert paths["canonicalOverlay"]["sha256"] == overlay_hash[route]

    ids = [step["id"] for step in plan["steps"]]
    assert ids == ["compile-probe", "load-disabled", "verify-disabled",
                   f"apply-{route}-runtime", f"settle-{route}-runtime",
                   "verify-endpoint", "reverify-disabled",
                   "query-acquire-release", "remove-runtime-overlay",
                   "verify-endpoint-absent", "unload", "verify-module-absent"]
    flat = "\n".join(shlex.join(step["argv"]) for step in plan["steps"])
    for prohibited in plan["prohibited"]:
        assert prohibited not in flat
    assert "live_output=0" in flat
    assert f"rp1-gpclk-{route}" in flat
    other = "gpio20" if route == "gpio4" else "gpio4"
    assert other not in flat
    assert "ATTEMPT_OVERLAY_ID" in flat


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("validate", "render"))
    parser.add_argument("--plan", type=pathlib.Path, default=DEFAULT_PLAN)
    args = parser.parse_args()
    plan = load(args.plan)
    validate(plan)
    if args.action == "render":
        for step in plan["steps"]:
            print(f'{step["id"]}: {shlex.join(step["argv"])}')
    else:
        print(f"Phase 5.54 lifecycle attempt-{plan['attempt']} controls: PASS")


if __name__ == "__main__":
    main()
