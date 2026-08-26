#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Enforce the independent 1.1.2 GPIO4/GPIO20 development boundary."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
version = (ROOT / "include/rp1_gpclk/version.h").read_text()
compat = (ROOT / "include/rp1_gpclk/compatibility.h").read_text()
implementation = (ROOT / "src/rp1_gpclk_compatibility.c").read_text()
main = (ROOT / "src/rp1_gpclk_main.c").read_text()
dispatch = (ROOT / "src/rp1_gpclk_uapi_dispatch.c").read_text()
execution = (ROOT / "src/rp1_gpclk_execution.c").read_text()
kernel_api = (ROOT / "src/rp1_gpclk_kernel_api.c").read_text()
resource_header = (ROOT / "include/rp1_gpclk/resource_policy.h").read_text()
rules = (ROOT / "debian/rules").read_text()
route_manager = (ROOT / "scripts/rp1-gpclk-route-manager.py").read_text()

for token in (
    '#define RP1_GPCLK_MODULE_VERSION "1.1.2"',
    '#define RP1_GPCLK_ROUTE_CANDIDATE_KERNEL "6.18.34+rpt-rpi-2712"',
    '#define RP1_GPCLK_ROUTE_CANDIDATE_ARCH "aarch64"',
    '#define RP1_GPCLK_ROUTE_CANDIDATE_VERSION "1.1.2"',
    "v1.1.2-pi5-gpio4-6.18.34-development-candidate-r3",
    "v1.1.2-pi5-gpio20-6.18.34-development-candidate-r3",
):
    assert token in version + compat

gpio4_case = implementation[implementation.index("case RP1_GPCLK_ROUTE_GPIO4:"):]
gpio20_case = gpio4_case[gpio4_case.index("case RP1_GPCLK_ROUTE_GPIO20:"):]
assert gpio20_case.index("return false;") < gpio20_case.index("default:")
assert "Neither route inherits" in implementation
assert 'strcmp(module_version, RP1_GPCLK_ROUTE_CANDIDATE_VERSION)' in implementation
assert "pi5_model_b || !resources_validated" in implementation
for token in (
    'RP1_GPCLK_GPIO4_ENDPOINT_NAME "rp1-gpclk-dkms-gpio4"',
    'RP1_GPCLK_GPIO20_ENDPOINT_NAME "rp1-gpclk-dkms-gpio20"',
):
    assert token in resource_header
assert "rp1_gpclk_route_endpoint_validate(route," in kernel_api

for token in (
    "static bool live_output;",
    "module_param(live_output, bool, 0444)",
    "return live_output && device && device->live_eligible;",
    'of_machine_is_compatible("raspberrypi,5-model-b")',
    "device->clock && device->dma_chan",
    "device->pinctrl",
    "device->tick_dma0 && device->dma_tick0",
    "device->rate_exclusive",
    "if (live_output && !device->live_eligible)",
):
    assert token in main

assert "RP1_GPCLK_COMPAT_EXPERIMENTAL" in dispatch
assert "RP1_GPCLK_COMPAT_QUALIFIED" not in dispatch
for token in (
    "RP1_GPCLK_FIRMWARE_TICK_CTRL 3U",
    "RP1_GPCLK_FIRMWARE_TICK_CYCLES 50U",
    "device->initial_dma_tick0_en || device->initial_dma_tick0_ctrl",
):
    assert token in execution
assert "MODULE_VERSION := 1.1.2" in rules
for prohibited in ("live_output=1", "/dev/mem", "shell=True", "/bin/sh"):
    assert prohibited not in route_manager
for operation in ('"query"', '"preflight"', '"apply-and-reboot"', '"rollback"', '"reconcile"'):
    assert operation in route_manager
assert "submit" not in route_manager.lower()

print("Independent GPIO4/GPIO20 development boundary: PASS")
