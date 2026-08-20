#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Reject unexpected warning-or-higher diagnostics from a Phase 2E run."""

from pathlib import Path
import re
import sys

if len(sys.argv) != 2:
    raise SystemExit(f"usage: {sys.argv[0]} DMESG_FILE")
lines = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
severe = re.compile(
    r"(?:BUG:|Oops:|Call Trace:|kernel panic|general protection fault|"
    r"use-after-free|KASAN:|UBSAN:|refcount_t:|WARNING:)",
    re.IGNORECASE,
)
allowed = (
    re.compile(r"rp1_gpclk_dkms: loading out-of-tree module taints kernel\.$"),
    re.compile(
        r"rp1-gpclk-missing-active.*error -ENODEV: "
        r"pinctrl resource acquisition failed$"
    ),
    re.compile(
        r"pinctrl-rp1 .*: pin gpio4 already requested by .*rp1-gpclk-dkms; "
        r"cannot claim for .*rp1-gpclk-conflict$"
    ),
    re.compile(r"pinctrl-rp1 .*: error -EINVAL: pin-4 .*rp1-gpclk-conflict.*$"),
    re.compile(
        r"pinctrl-rp1 .*: error -EINVAL: could not request pin 4 \(gpio4\) "
        r"from group gpio4 on device pinctrl-rp1$"
    ),
    re.compile(r"rp1-gpclk-conflict: Error applying setting, reverse things back$"),
    re.compile(
        r"rp1-gpclk-dma-conflict.*error -EBUSY: "
        r"endpoint resource ownership conflict$"
    ),
    re.compile(
        r"rp1-gpclk-dma-conflict.*probe with driver rp1-gpclk-dkms "
        r"failed with error -16$"
    ),
    re.compile(
        r"rp1-gpclk-bad-dma.*error -ENOENT: device-tree identity validation failed$"
    ),
    re.compile(r"rp1-gpclk-bad-dma.*probe with driver rp1-gpclk-dkms failed with error -2$"),
)
for line in lines:
    if severe.search(line):
        raise SystemExit(f"severe kernel diagnostic: {line}")
    if not any(pattern.search(line) for pattern in allowed):
        raise SystemExit(f"unclassified kernel diagnostic: {line}")
for pattern in allowed[1:]:
    matches = sum(bool(pattern.search(line)) for line in lines)
    if matches != 1:
        raise SystemExit(
            f"expected exactly one fixture diagnostic, found {matches}: {pattern.pattern}"
        )
required = (
    "pinctrl resource acquisition failed",
    "endpoint resource ownership conflict",
    "device-tree identity validation failed",
)
for token in required:
    if not any(token in line for line in lines):
        raise SystemExit(f"missing expected diagnostic: {token}")
print(f"kernel warning classification: PASS ({len(lines)} expected lines)")
