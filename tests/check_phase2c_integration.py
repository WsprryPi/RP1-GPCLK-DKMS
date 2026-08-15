#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Enforce the clock-disabled Phase 2C source boundary."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
main = (ROOT / "src/rp1_gpclk_main.c").read_text(encoding="utf-8")
api = (ROOT / "src/rp1_gpclk_kernel_api.c").read_text(encoding="utf-8")
dispatch = (ROOT / "src/rp1_gpclk_uapi_dispatch.c").read_text(encoding="utf-8")
policy = (ROOT / "include/rp1_gpclk/resource_policy.h").read_text(encoding="utf-8")
all_source = "\n".join(
    path.read_text(encoding="utf-8")
    for path in (ROOT / "src").glob("*.c")
    if path.name != "rp1_gpclk_execution.c"
)

required = {
    "platform driver": "module_platform_driver(rp1_gpclk_driver)",
    "misc registration": "misc_register(&device->miscdev)",
    "restrictive mode": "device->miscdev.mode = 0600",
    "clock phandle validation": "of_parse_phandle_with_args",
    "provider resource translation": "of_address_to_resource",
    "rate exclusion": "clk_rate_exclusive_get",
    "DMA channel": "dma_request_chan(device->dev, \"tx\")",
    "DMA resource translation": "dma_map_resource",
    "pinctrl states": "pinctrl_lookup_state",
    "dead-open guard": "rp1_gpclk_lifetime_get_live(device)",
}
for label, token in required.items():
    if token not in main + api:
        raise SystemExit(f"missing {label}")

if "RP1_GPCLK_CLOCK_ID 33U" not in policy or "0x17cU" not in policy:
    raise SystemExit("reviewed GPCLK0 identity is absent")
if "default:" not in dispatch or "return -EOPNOTSUPP" not in dispatch:
    raise SystemExit("runtime dispatcher does not reject unsupported commands")

forbidden = {
    "clock prepare or enable": r"clk_prepare|clk_enable|clk_prepare_enable",
    "clock rate change": r"clk_set_rate|clk_set_parent",
    "pinctrl selection": r"pinctrl_select_state",
    "DMA descriptor": r"dmaengine_prep|dmaengine_submit|dma_async_issue_pending",
    "DMA termination": r"dmaengine_terminate|dmaengine_synchronize",
    "raw MMIO write": r"\b(?:readl|writel|of_iomap)\b",
    "private symbol": r"kallsyms|kprobe",
}
for label, pattern in forbidden.items():
    if re.search(pattern, all_source):
        raise SystemExit(f"Phase 2C contains {label}")

for token in ("static bool live_output;",
              "module_param(live_output, bool, 0444)",
              "rp1_gpclk_live_output_enabled"):
    if token not in main:
        raise SystemExit(f"Phase 4A output-inhibit gate is missing {token}")

release = api[api.index("void rp1_gpclk_resources_release"):]
ordered = ["dma_unmap_resource", "dma_release_channel",
           "pinctrl_put", "clk_rate_exclusive_put", "clk_put"]
positions = [release.index(token) for token in ordered]
if positions != sorted(positions):
    raise SystemExit("resources are not released in reverse acquisition order")

print("Phase 2C integration boundary: PASS")
