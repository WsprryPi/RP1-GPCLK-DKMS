#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Enforce the exact Phase 4D combined-route live-enrollment boundary."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / "src/rp1_gpclk_main.c").read_text(encoding="utf-8")
DISPATCH = (ROOT / "src/rp1_gpclk_uapi_dispatch.c").read_text(encoding="utf-8")
EXECUTION = (ROOT / "src/rp1_gpclk_execution.c").read_text(encoding="utf-8")

for token in (
    'device->route == RP1_GPCLK_ROUTE_GPIO4 ||',
    'device->route == RP1_GPCLK_ROUTE_GPIO20',
    '"6.18.34+rpt-rpi-2712"',
    'of_machine_is_compatible("raspberrypi,5-model-b")',
    'live_output && device && device->live_eligible',
    'live output rejected by exact Phase 4D compatibility allowlist',
):
    if token not in MAIN:
        raise SystemExit(f"exact combined enrollment gate missing {token}")

for token in (
    "rp1_gpclk_live_output_eligible(context->device)",
    '"phase4d-wspr5-combined-6.18.34"',
):
    if token not in DISPATCH:
        raise SystemExit(f"truthful Phase 4D query/submit gate missing {token}")

for token in (
    "initial_tick_dma0_ctrl", "initial_tick_dma0_cycles",
    "initial_dma_tick0_en", "initial_dma_tick0_ctrl",
    "readback_expected", "readback_observed", "tick_final=",
):
    if token not in EXECUTION:
        raise SystemExit(f"Phase 4D audit/restoration evidence missing {token}")

print("Phase 4D combined-route enrollment and restoration boundary: PASS")
