#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Statically enforce the Phase 2E clock-disabled target boundary."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "\n".join(
    path.read_text(encoding="utf-8")
    for path in (ROOT / "src").glob("*.c")
    if path.name != "rp1_gpclk_execution.c"
)
OVERLAY = (ROOT / "overlays/rp1-gpclk-gpio4.dts").read_text(encoding="utf-8")
FIXTURES = "\n".join(
    path.read_text(encoding="utf-8")
    for path in sorted((ROOT / "overlays/fixtures").glob("*.dts"))
)
RUNNER = (ROOT / "tests/phase2e-target-test.sh").read_text(encoding="utf-8")
DT_CHECK = (ROOT / "tests/phase2e_dt_identity.py").read_text(encoding="utf-8")

forbidden_source = {
    "clock activation": r"\bclk_(?:prepare|enable|prepare_enable|set_rate|set_parent)\s*\(",
    "pinctrl activation": r"\bpinctrl_select_state\s*\(",
    "DMA execution": r"\b(?:dmaengine_prep|dmaengine_submit|dma_async_issue_pending)\b",
    "raw MMIO access": r"\b(?:readl|writel|of_iomap)\s*\(",
    "private symbols": r"\b(?:kallsyms|kprobe)\b",
}
for label, pattern in forbidden_source.items():
    if re.search(pattern, SOURCE):
        raise SystemExit(f"Phase 2E contains forbidden {label}")
if "device->divider_dma = (dma_addr_t)device->divider_phys" not in SOURCE:
    raise SystemExit("DMAengine was not given the validated CPU-physical peripheral address")
for token in ("rp1_gpclk_endpoint_owner", "endpoint resource ownership conflict",
              "rp1_gpclk_endpoint_release(device)",
              "atomic_set_release(&rp1_gpclk_endpoint_owner, 0)"):
    if token not in SOURCE:
        raise SystemExit(f"composite endpoint exclusion is missing {token}")

required_overlay = (
    'compatible = "wsprrypi,rp1-gpclk-dkms-v1"',
    'wsprrypi,route = <1>',
    'function = "gpio"',
    'function = "gpclk0"',
    'pins = "gpio4"',
    'pinctrl-names = "default", "active", "safe"',
    'pinctrl-0 = <&rp1_gpclk_gpio4_safe>',
    'pinctrl-2 = <&rp1_gpclk_gpio4_safe>',
    'clocks = <&rp1_clocks RP1_CLK_GP0>',
    'dmas = <&rp1_dma RP1_DMA_DMA_TICK_TICK0>',
    'dma-names = "tx"',
)
for token in required_overlay:
    if token not in OVERLAY:
        raise SystemExit(f"production overlay is missing {token}")
if re.search(r'pinctrl-[02]\s*=\s*<&rp1_gpclk_gpio4_active>', OVERLAY):
    raise SystemExit("production overlay activates GPCLK in default or safe state")
if 'pins = "gpio20"' in OVERLAY:
    raise SystemExit("GPIO4 production overlay contains GPIO20")

for fixture in ("conflict", "dma-conflict", "missing-active", "bad-dma"):
    if fixture not in FIXTURES:
        raise SystemExit(f"missing negative fixture {fixture}")
for token in (
    "[[ $(hostname) == wspr5 ]]",
    "assert_safe baseline",
    "assert_safe final-cleanup",
    "assert_absent explicit-final-state",
    "GPIO4 = input",
    "clk_prepare_count",
    "clk_enable_count",
    "trap cleanup EXIT HUP INT TERM",
    "linux-headers-phase2e-missing",
    "phase2e_uapi_client\" expect-busy",
    "phase2e_dt_identity.py",
    "EXPECTED_FAILURE_STATUS",
    "holder-sigkill-wait",
    "clk_protect_count",
    "phase2e_check_dmesg.py",
    "phase2e_dmesg_delta.py",
    "rp1-gpclk-phase2e-manifest",
    "find -L",
    "modinfo -n",
):
    if token not in RUNNER:
        raise SystemExit(f"target runner is missing {token}")
for forbidden in ("clk_prepare", "clk_enable", "pinctrl set", "pinctrl_select", "dmaengine_submit"):
    if forbidden in RUNNER and forbidden not in ("clk_prepare", "clk_enable"):
        raise SystemExit(f"target runner contains forbidden action {forbidden}")
for token in (
    "clock[1] != 33",
    "dma[1] != 0x30",
    "raspberrypi,rp1-clocks",
    "snps,axi-dma-1.01a",
    "divider_target=0x",
):
    if token not in DT_CHECK:
        raise SystemExit(f"runtime DT checker is missing {token}")

print("Phase 2E clock-disabled target assets: PASS")
