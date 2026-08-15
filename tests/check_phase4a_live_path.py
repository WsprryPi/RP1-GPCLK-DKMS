#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Enforce Phase 4A stock-kernel live-path and output-inhibit invariants."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / "src/rp1_gpclk_main.c").read_text(encoding="utf-8")
DISPATCH = (ROOT / "src/rp1_gpclk_uapi_dispatch.c").read_text(encoding="utf-8")
EXECUTION = (ROOT / "src/rp1_gpclk_execution.c").read_text(encoding="utf-8")
KERNEL_API = (ROOT / "src/rp1_gpclk_kernel_api.c").read_text(encoding="utf-8")
POLICY = (ROOT / "include/rp1_gpclk/resource_policy.h").read_text(encoding="utf-8")
GPIO4 = (ROOT / "overlays/rp1-gpclk-gpio4.dts").read_text(encoding="utf-8")
GPIO20 = (ROOT / "overlays/rp1-gpclk-gpio20.dts").read_text(encoding="utf-8")
RUNNER = (ROOT / "tests/phase4a-target-test.sh").read_text(encoding="utf-8")

for token in ("static bool live_output;",
              "module_param(live_output, bool, 0444)",
              "rp1_gpclk_live_output_enabled"):
    if token not in MAIN:
        raise SystemExit(f"output-inhibit gate missing {token}")

for function in ("rp1_gpclk_submit_wspr", "rp1_gpclk_submit_events"):
    start = DISPATCH.index(f"static long {function}")
    end = DISPATCH.index("\n}\n", start)
    body = DISPATCH[start:end]
    gate = body.index("!rp1_gpclk_live_output_enabled()")
    copy = body.index("memdup_user")
    execute = body.index("rp1_gpclk_execution_submit")
    if not gate < copy < execute:
        raise SystemExit(f"{function} does not fail closed before plan copy")
    copy_back = body.index("copy_to_user")
    activate = body.index("rp1_gpclk_execution_activate")
    if not execute < copy_back < activate:
        raise SystemExit(f"{function} can activate before generation copyout")

for token in (
    "dmaengine_prep_slave_single",
    "DMA_MEM_TO_DEV",
    "DMA_DEV_TO_MEM",
    "device->divider_dma",
    "rp1_gpclk_execution_fill_words",
    "rp1_gpclk_execution_event_writes",
    "dmaengine_terminate_sync",
    "dmaengine_synchronize",
    "pinctrl_select_state(device->pinctrl, device->pins_active)",
    "pinctrl_select_state(device->pinctrl, device->pins_safe)",
    "clk_prepare(device->clock)",
    "clk_enable(device->clock)",
    "clk_disable(device->clock)",
    "clk_unprepare(device->clock)",
    "rp1_gpclk_core_cleanup_failed",
    "complete_all(&device->execution_done)",
):
    if token not in EXECUTION:
        raise SystemExit(f"live execution missing {token}")

for forbidden in (r"/dev/mem", r"\bkprobe", r"\bkallsyms",
                  r"rp1_gpclk_dma_lease", r"0x1f[0-9a-fA-F]+"):
    if re.search(forbidden, EXECUTION + KERNEL_API):
        raise SystemExit(f"forbidden production dependency {forbidden}")

for token in ("RP1_GPCLK_TICK_DMA0_OFFSET 0x174024U",
              "RP1_GPCLK_DMA_TICK0_OFFSET 0x158000U",
              "check_add_overflow(device->rp1_phys_start",
              "resource_overlaps(cycles, tick)",
              "DMA_BIDIRECTIONAL"):
    if token not in POLICY + KERNEL_API:
        raise SystemExit(f"DT-derived pacing resource check missing {token}")

shared = ('reg-names = "tick-dma0", "dma-tick0"',
          '<0xc0 0x40174024 0x0 0x8>', '<0xc0 0x40158000 0x0 0x8>')
for label, overlay in (("GPIO4", GPIO4), ("GPIO20", GPIO20)):
    for token in shared:
        if token not in overlay:
            raise SystemExit(f"{label} overlay missing {token}")

for token in ("RP1_GPCLK_TARGET_MODULE_PARAMETERS=live_output=0",
              "RP1_GPCLK_TARGET_RUN_INERT=1"):
    if token not in RUNNER:
        raise SystemExit(f"Phase 4A runner missing {token}")

print("Phase 4A live-path static boundary: PASS")
