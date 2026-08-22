#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Preserve Phase 4 integrity around the exact 1.0.1 GPIO4 candidate gate."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / "src/rp1_gpclk_main.c").read_text(encoding="utf-8")
DISPATCH = (ROOT / "src/rp1_gpclk_uapi_dispatch.c").read_text(encoding="utf-8")
EXECUTION = (ROOT / "src/rp1_gpclk_execution.c").read_text(encoding="utf-8")

for token in (
    'static bool rp1_gpclk_release_identity_allowed',
    'rp1_gpclk_route_candidate_allowed',
    'of_machine_is_compatible("raspberrypi,5-model-b")',
    'live_output && device && device->live_eligible',
    'live output rejected by exact route compatibility policy',
):
    if token not in MAIN:
        raise SystemExit(f"exact GPIO4 candidate gate missing {token}")

for token in (
    "rp1_gpclk_live_output_eligible(context->device)",
    "rp1_gpclk_route_candidate_id(route)",
):
    if token not in DISPATCH:
        raise SystemExit(f"truthful candidate query/submit gate missing {token}")

for token in (
    "initial_tick_dma0_ctrl", "initial_tick_dma0_cycles",
    "initial_dma_tick0_en", "initial_dma_tick0_ctrl",
    "readback_expected", "readback_observed", "tick_final=",
):
    if token not in EXECUTION:
        raise SystemExit(f"Phase 4D audit/restoration evidence missing {token}")

print("Phase 4 execution and exact 1.0.1 GPIO4 candidate boundary: PASS")
