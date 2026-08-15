#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the bound Phase 2E runtime DT identity without exposing it by UAPI."""

from pathlib import Path
import struct
import sys


def cells(path: Path) -> tuple[int, ...]:
    raw = path.read_bytes()
    if not raw or len(raw) % 4:
        raise SystemExit(f"invalid cells: {path}")
    return struct.unpack(f">{len(raw) // 4}I", raw)


def strings(path: Path) -> list[str]:
    return [item.decode("ascii") for item in path.read_bytes().rstrip(b"\0").split(b"\0")]


def resolve_phandle(value: int) -> Path:
    root = Path("/proc/device-tree")
    for candidate in root.rglob("phandle"):
        if cells(candidate) == (value,):
            return candidate.parent
    raise SystemExit(f"unresolved phandle: {value}")


def platform_device_for_node(node: Path) -> Path:
    for candidate in Path("/sys/bus/platform/devices").iterdir():
        of_node = candidate / "of_node"
        if of_node.exists() and of_node.resolve() == node.resolve():
            return candidate
    raise SystemExit(f"no platform device for {node}")


if len(sys.argv) != 4:
    raise SystemExit(f"usage: {sys.argv[0]} OF_NODE EXPECTED_ROUTE EXPECTED_PIN")
node = Path(sys.argv[1]).resolve()
expected_route = int(sys.argv[2])
expected_pin = int(sys.argv[3])
if (expected_route, expected_pin) not in ((1, 4), (2, 20)):
    raise SystemExit("expected route/pin pair is not allowlisted")
if strings(node / "compatible") != ["wsprrypi,rp1-gpclk-dkms-v1"]:
    raise SystemExit("unexpected consumer compatible")
if cells(node / "wsprrypi,route") != (expected_route,):
    raise SystemExit("unexpected route")
if cells(node / "wsprrypi,pin") != (expected_pin,):
    raise SystemExit("unexpected pin")
if strings(node / "clock-names") != ["gpclk"]:
    raise SystemExit("unexpected clock name")
if strings(node / "dma-names") != ["tx"]:
    raise SystemExit("unexpected DMA name")
if strings(node / "reg-names") != ["tick-dma0", "dma-tick0"]:
    raise SystemExit("unexpected DMA-tick resource names")
if cells(node / "reg") != (
    0xC0, 0x40174024, 0, 8,
    0xC0, 0x40158000, 0, 8,
):
    raise SystemExit("unexpected DMA-tick resource identity")
if strings(node / "pinctrl-names") != ["default", "active", "safe"]:
    raise SystemExit("unexpected pinctrl states")
clock = cells(node / "clocks")
dma = cells(node / "dmas")
if len(clock) != 2 or clock[1] != 33:
    raise SystemExit("unexpected GPCLK0 specifier")
if len(dma) != 2 or dma[1] != 0x30:
    raise SystemExit("unexpected DMA tick request")
clock_provider = resolve_phandle(clock[0])
dma_provider = resolve_phandle(dma[0])
if "raspberrypi,rp1-clocks" not in strings(clock_provider / "compatible"):
    raise SystemExit("unexpected clock provider")
if strings(dma_provider / "compatible") != ["snps,axi-dma-1.01a"]:
    raise SystemExit("unexpected DMA provider")
if clock_provider.parent != dma_provider.parent:
    raise SystemExit("clock and DMA providers are not in the same RP1")
clock_reg = cells(clock_provider / "reg")
if len(clock_reg) < 4:
    raise SystemExit("clock provider resource is truncated")
resource_size = (clock_reg[2] << 32) | clock_reg[3]
if resource_size < 0x180:
    raise SystemExit("clock provider resource does not contain DIV_FRAC")
clock_device = platform_device_for_node(clock_provider)
try:
    resource_start = int(clock_device.name.split(".", 1)[0], 16)
except ValueError as error:
    raise SystemExit("clock platform device lacks translated resource identity") from error
divider_target = resource_start + 0x17C
print(
    "runtime DT identity: PASS "
    f"route=GPIO{expected_pin} pin={expected_pin} clock=GPCLK0(33) "
    f"clock_provider={clock_provider} "
    f"resource_start=0x{resource_start:x} resource_size=0x{resource_size:x} "
    f"divider_target=0x{divider_target:x} dma_map=proved-by-bound-endpoint "
    f"dma_request=0x30 dma_provider={dma_provider} "
    "tick_dma0=rp1+0x174024 dma_tick0=rp1+0x158000"
)
