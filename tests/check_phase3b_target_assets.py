#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Statically enforce the Phase 3B clock-disabled target boundary."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
RUNNER = (ROOT / "tests/phase3b-target-test.sh").read_text(encoding="utf-8")
CLIENT = (ROOT / "tests/phase3b_uapi_client.c").read_text(encoding="utf-8")
DT_CHECK = (ROOT / "tests/phase3b_dt_identity.py").read_text(encoding="utf-8")
SOURCE = "\n".join(
    p.read_text(encoding="utf-8") for p in (ROOT / "src").glob("*.c")
    if p.name != "rp1_gpclk_execution.c"
)
PROMPT = (ROOT / "docs/contracts/phase3b-clock-disabled-route-closure-execution-prompt.md").read_text(encoding="utf-8")

for asset in (
    "overlays/rp1-gpclk-gpio4.dts",
    "overlays/rp1-gpclk-gpio20.dts",
    "overlays/fixtures/rp1-gpclk-gpio20-conflict.dts",
    "overlays/fixtures/rp1-gpclk-gpio20-dma-conflict.dts",
    "overlays/fixtures/rp1-gpclk-gpio20-missing-active.dts",
    "overlays/fixtures/rp1-gpclk-gpio20-bad-dma.dts",
):
    if not (ROOT / asset).is_file():
        raise SystemExit(f"missing Phase 3B asset {asset}")

for token in (
    "[[ $(hostname) == wspr5 ]]",
    "pinctrl get 4",
    "pinctrl get 20",
    "clk_prepare_count",
    "clk_enable_count",
    "clk_protect_count",
    "route_matrix 1 4 20",
    "route_matrix 2 20 4",
    "for cycle in 1 2 3",
    "expect-mismatch",
    "expect_overlay_failure",
    "open_lifetime_matrix 1 4",
    "open_lifetime_matrix 2 20",
    "new-open-after-unbind",
    "open-unload-after-unbind",
    "installed -eq 0",
    "-z $bound",
    "source-archive-sha256.txt",
    "trap cleanup EXIT HUP INT TERM",
    "dmesg-warning-baseline",
    "SHA256SUMS",
):
    if token not in RUNNER:
        raise SystemExit(f"Phase 3B runner missing {token}")

for pattern in (
    r"\bclk_(?:prepare|enable|prepare_enable|set_rate|set_parent)\s*\(",
    r"\bpinctrl_select_state\s*\(",
    r"\b(?:dmaengine_prep|dmaengine_submit|dma_async_issue_pending)\b",
):
    if re.search(pattern, SOURCE):
        raise SystemExit("Phase 3B source crossed the clock-disabled boundary")
for forbidden in ("pinctrl set", "pinctrl_select", "dmaengine_submit"):
    if forbidden in RUNNER:
        raise SystemExit(f"Phase 3B runner contains forbidden {forbidden}")

for token in ("expect-mismatch", "route != RP1_GPCLK_ROUTE_GPIO20",
              '"0.0.0-phase3b"'):
    if token not in CLIENT:
        raise SystemExit(f"Phase 3B client missing {token}")
for token in ("expected_route", "expected_pin", "wsprrypi,pin", "clock[1] != 33",
              "dma[1] != 0x30", '"tick-dma0", "dma-tick0"',
              "0x40174024", "0x40158000"):
    if token not in DT_CHECK:
        raise SystemExit(f"Phase 3B DT checker missing {token}")
if "No findings yet" in PROMPT:
    raise SystemExit("Phase 3B findings were not reinjected")
if "phase2e-gpio4-clock-disabled" in SOURCE:
    raise SystemExit("runtime retains GPIO4-only compatibility identity")

print("Phase 3B target assets: PASS")
