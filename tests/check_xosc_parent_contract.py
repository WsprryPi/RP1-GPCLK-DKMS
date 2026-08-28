#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Enforce deterministic XOSC identity, selection, and cleanup ordering."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = (ROOT / "src/rp1_gpclk_kernel_api.c").read_text()
EXECUTION = (ROOT / "src/rp1_gpclk_execution.c").read_text()
MACHINE = (ROOT / "src/rp1_gpclk_execution_machine.c").read_text()
POLICY = (ROOT / "include/rp1_gpclk/resource_policy.h").read_text()

for token in (
    '#define RP1_GPCLK_XOSC_PROVIDER_COMPATIBLE "fixed-clock"',
    '#define RP1_GPCLK_XOSC_NODE_NAME "clk_xosc"',
    '#define RP1_GPCLK_XOSC_OUTPUT_NAME "xosc"',
    "#define RP1_GPCLK_XOSC_RATE_HZ 50000000U",
):
    assert token in POLICY, token

for token in (
    'of_property_count_strings(device->dev->of_node, "clock-names") != 2',
    'of_count_phandle_with_args(device->dev->of_node, "clocks"',
    'of_node_name_eq(xosc_spec.np, RP1_GPCLK_XOSC_NODE_NAME)',
    'of_property_read_string(xosc_spec.np, "clock-output-names"',
    'clk_get(device->dev, "xosc")',
    "clk_put(device->xosc)",
):
    assert token in API, token

selection = EXECUTION[EXECUTION.index("static int rp1_gpclk_machine_set_rate") :]
selection = selection[: selection.index("static int rp1_gpclk_machine_prepare")]
ordered = [
    selection.index("device->initial_parent = clk_get_parent"),
    selection.index("clk_set_parent(device->clock, device->xosc)"),
    selection.index("clk_is_match(clk_get_parent(device->clock), device->xosc)"),
    selection.index("parent_rate = clk_get_rate(device->xosc)"),
    selection.index("clk_set_rate(device->clock, requested_rate)"),
]
assert ordered == sorted(ordered)

finish = MACHINE[MACHINE.index("int rp1_gpclk_execution_machine_finish") :]
cleanup = [
    finish.index("ops->disable_clock"),
    finish.index("ops->unprepare_clock"),
    finish.index("ops->select_safe"),
    finish.index("ops->restore_parent"),
    finish.index("ops->restore_rate"),
]
assert cleanup == sorted(cleanup)

for route in ("gpio4", "gpio20"):
    overlay = (ROOT / f"overlays/rp1-gpclk-{route}.dts").read_text()
    assert 'clocks = <&rp1_clocks RP1_CLK_GP0>, <&clk_xosc>;' in overlay
    assert 'clock-names = "gpclk", "xosc";' in overlay

print("deterministic XOSC parent contract: PASS")
