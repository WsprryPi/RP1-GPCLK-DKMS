#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Reject unexpected warning-or-higher diagnostics from Phase 3B."""

from pathlib import Path
import re
import sys

if len(sys.argv) != 2:
    raise SystemExit(f"usage: {sys.argv[0]} DMESG_FILE")

lines = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
severe = re.compile(
    r"(?:BUG:|Oops:|Call Trace:|kernel panic|general protection fault|"
    r"use-after-free|KASAN:|UBSAN:|refcount_t:|WARNING:)", re.IGNORECASE
)
allowed = (
    re.compile(r"rp1_gpclk_dkms: loading out-of-tree module taints kernel\.$"),
    re.compile(r"rp1-gpclk-missing-active.*error -ENODEV: "
               r"pinctrl resource acquisition failed$"),
    re.compile(r"pinctrl-rp1 .*: pin gpio(?:4|20) already requested by "
               r".*rp1-gpclk-dkms; cannot claim for .*rp1-gpclk-conflict$"),
    re.compile(r"pinctrl-rp1 .*: error -EINVAL: pin-(?:4|20) "
               r".*rp1-gpclk-conflict.*$"),
    re.compile(r"pinctrl-rp1 .*: error -EINVAL: could not request pin "
               r"(?:4|20) \(gpio(?:4|20)\) from group gpio(?:4|20) "
               r"on device pinctrl-rp1$"),
    re.compile(r"rp1-gpclk-conflict: Error applying setting, "
               r"reverse things back$"),
    re.compile(r"rp1-gpclk-dma-conflict.*error -EBUSY: "
               r"endpoint resource ownership conflict$"),
    re.compile(r"rp1-gpclk-dma-conflict.*probe with driver "
               r"rp1-gpclk-dkms failed with error -16$"),
    re.compile(r"rp1-gpclk-bad-dma.*error -ENOENT: "
               r"device-tree identity validation failed$"),
    re.compile(r"rp1-gpclk-bad-dma.*probe with driver "
               r"rp1-gpclk-dkms failed with error -2$"),
    re.compile(r"rp1-gpclk-(?:invalid-route|gpio20-route-mismatch).*"
               r"error -EINVAL: device-tree identity validation failed$"),
    re.compile(r"rp1-gpclk-(?:invalid-route|gpio20-route-mismatch).*"
               r"probe with driver rp1-gpclk-dkms failed with error -22$"),
)

for line in lines:
    if severe.search(line):
        raise SystemExit(f"severe kernel diagnostic: {line}")
    if not any(pattern.search(line) for pattern in allowed):
        raise SystemExit(f"unclassified kernel diagnostic: {line}")

expected_counts = (0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2)
for pattern, expected in zip(allowed, expected_counts, strict=True):
    count = sum(bool(pattern.search(line)) for line in lines)
    if count != expected:
        raise SystemExit(
            f"expected {expected} matches, found {count}: {pattern.pattern}"
        )
if len(lines) != 22:
    raise SystemExit(f"expected exact 22-line diagnostic set, found {len(lines)}")

required = (
    "pin gpio4 already requested",
    "pin gpio20 already requested",
    "pinctrl resource acquisition failed",
    "endpoint resource ownership conflict",
    "device-tree identity validation failed",
)
for token in required:
    if not any(token in line for line in lines):
        raise SystemExit(f"missing expected Phase 3B diagnostic: {token}")

print(f"Phase 3B kernel warning classification: PASS ({len(lines)} expected lines)")
