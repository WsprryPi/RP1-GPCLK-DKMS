#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Fail if Phase 2A source grows a hardware or registration implementation."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
text = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "src").glob("*.c"))
forbidden = {
    "platform registration": r"platform_driver_register|module_platform_driver",
    "device registration": r"misc_register|register_chrdev|device_create",
    "DMA acquisition": r"dma_request_chan|dmaengine_prep|dma_map_",
    "clock acquisition": r"clk_get|devm_clk_get|clk_prepare|clk_enable",
    "pinctrl acquisition": r"pinctrl_get|pinctrl_select_state",
    "device-tree mapping": r"of_iomap|ioremap|of_address_to_resource",
    "raw physical access": r"/dev/mem|phys_to_virt|readl|writel",
    "private-symbol lookup": r"kallsyms|kprobe",
}
for label, pattern in forbidden.items():
    if re.search(pattern, text):
        raise SystemExit(f"inert skeleton contains {label}")
assert "MODULE_LICENSE(\"Dual MIT/GPL\")" in text
assert text.count("-EOPNOTSUPP") == 6
print("inert skeleton: PASS")
