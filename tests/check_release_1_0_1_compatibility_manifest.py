#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Cross-check the normative manifest against the compiled GPIO4 candidate."""

import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
decisions = json.loads(
    (ROOT / "release/compatibility-decisions-v1.json").read_text()
)
header = (ROOT / "include/rp1_gpclk/compatibility.h").read_text()
source = (ROOT / "src/rp1_gpclk_compatibility.c").read_text()
main = (ROOT / "src/rp1_gpclk_main.c").read_text()
uapi = ROOT / "include/uapi/linux/rp1_gpclk.h"
gpio4_dts = ROOT / "overlays/rp1-gpclk-gpio4.dts"
evidence = ROOT / "docs/evidence/release-1.0.0-repaired-target-verification-success.json"


def macro(name):
    match = re.search(rf'^#define {name} "([^"]+)"$', header, re.MULTILINE)
    assert match, name
    return match.group(1)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


gpio4 = next(entry for entry in decisions["entries"] if entry["route"] == "GPIO4")
gpio20 = next(entry for entry in decisions["entries"] if entry["route"] == "GPIO20")

assert gpio4["id"] == macro("RP1_GPCLK_GPIO4_CANDIDATE_ID")
assert gpio4["build"]["kernelRelease"] == macro(
    "RP1_GPCLK_GPIO4_CANDIDATE_KERNEL"
)
assert gpio4["build"]["runtimeArchitecture"] == macro("RP1_GPCLK_GPIO4_CANDIDATE_ARCH")
assert gpio4["build"]["moduleVersion"] == macro(
    "RP1_GPCLK_GPIO4_CANDIDATE_VERSION"
)
assert gpio4["uapiHeaderSha256"] == sha256(uapi)
assert gpio4["overlay"]["sourceSha256"] == sha256(gpio4_dts)
assert gpio4["state"] == "Experimental" and gpio4["liveEligible"] is True
assert gpio4["runtime"]["piModel"].startswith("Raspberry Pi 5 Model B")
assert gpio4["build"]["kernelRelease"] == "6.18.34+rpt-rpi-2712"
assert gpio4["build"]["architecture"] == "arm64"
assert gpio4["build"]["runtimeArchitecture"] == "aarch64"
assert gpio4["build"]["moduleUnsignedSha256"] == \
    "8673a62be85289dc5faec68976be0b02bc16478a2d7f107e96177618d31b4160"
assert gpio4["build"]["moduleInstalledSha256"] == \
    "1979d2dfdbe6a38d03be2c4b2a9acc29109a89ed56f4d860a0e65435af81133f"
assert gpio4["build"]["moduleInstalledSha256"] != \
    gpio4["build"]["moduleUnsignedSha256"]
assert gpio4["build"]["moduleInstalledTransform"] == \
    "strip --strip-debug; hash uncompressed ELF before filesystem compression"
assert gpio4["evidence"] == [{
    "id": "release-1.0.0-repaired-inactive-gpio4",
    "sha256": sha256(evidence),
    "routes": ["GPIO4"],
    "modes": ["QRSS", "FSKCW", "DFCW", "WSPR"],
    "classes": ["build", "clock-disabled", "cleanup", "recovery"],
}]

assert gpio20["state"] == "Unavailable"
assert gpio20["liveEligible"] is False
assert sum(entry["liveEligible"] for entry in decisions["entries"]) == 1
assert all(
    evidence_item["routes"] == [entry["route"]]
    for entry in decisions["entries"]
    for evidence_item in entry["evidence"]
)

for required in (
    "route == RP1_GPCLK_ROUTE_GPIO4",
    "RP1_GPCLK_GPIO4_CANDIDATE_KERNEL",
    "RP1_GPCLK_GPIO4_CANDIDATE_ARCH",
    "RP1_GPCLK_GPIO4_CANDIDATE_VERSION",
    "pi5_model_b && resources_validated",
):
    assert required in source
for required in (
    'of_machine_is_compatible("raspberrypi,5-model-b")',
    "device->clock && device->dma_chan",
    "device->pinctrl",
    "device->tick_dma0 && device->dma_tick0",
    "device->rate_exclusive",
):
    assert required in main
for prohibited in ("strstr(", "strncmp(", "RP1_GPCLK_ROUTE_GPIO20"):
    assert prohibited not in source

print("1.0.1 compatibility manifest/runtime cross-contract: PASS")
