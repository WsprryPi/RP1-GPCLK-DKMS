#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Preserve Phase 4 execution integrity while Phase 5.2 fails closed."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / "src/rp1_gpclk_main.c").read_text(encoding="utf-8")
DISPATCH = (ROOT / "src/rp1_gpclk_uapi_dispatch.c").read_text(encoding="utf-8")
EXECUTION = (ROOT / "src/rp1_gpclk_execution.c").read_text(encoding="utf-8")

for token in (
    'static bool rp1_gpclk_release_identity_allowed',
    'return false;',
    'live_output && device && device->live_eligible',
    'live output rejected: release has no positive compatibility entry',
):
    if token not in MAIN:
        raise SystemExit(f"Phase 5.2 fail-closed release gate missing {token}")

for token in (
    "rp1_gpclk_live_output_eligible(context->device)",
    '"phase5.2-no-positive-release-entry"',
):
    if token not in DISPATCH:
        raise SystemExit(f"truthful Phase 5.2 query/submit gate missing {token}")

for token in (
    "initial_tick_dma0_ctrl", "initial_tick_dma0_cycles",
    "initial_dma_tick0_en", "initial_dma_tick0_ctrl",
    "readback_expected", "readback_observed", "tick_final=",
):
    if token not in EXECUTION:
        raise SystemExit(f"Phase 4D audit/restoration evidence missing {token}")

print("Phase 4 execution and Phase 5.2 release-demotion boundary: PASS")
