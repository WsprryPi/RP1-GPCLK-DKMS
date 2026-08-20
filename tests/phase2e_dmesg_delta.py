#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Extract a dmesg suffix only when the baseline remains an exact prefix."""

from pathlib import Path
import sys

if len(sys.argv) != 4:
    raise SystemExit(f"usage: {sys.argv[0]} BASELINE FINAL DELTA")
baseline = Path(sys.argv[1]).read_bytes().splitlines(keepends=True)
final = Path(sys.argv[2]).read_bytes().splitlines(keepends=True)
if len(final) < len(baseline) or final[: len(baseline)] != baseline:
    raise SystemExit("dmesg baseline is not an intact prefix; attribution unavailable")
Path(sys.argv[3]).write_bytes(b"".join(final[len(baseline) :]))
print(f"dmesg delta: PASS ({len(final) - len(baseline)} new lines)")
