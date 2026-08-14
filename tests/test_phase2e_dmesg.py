#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Exercise positive and adversarial Phase 2E dmesg classifications."""

from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tests/phase2e_check_dmesg.py"
EXPECTED = """\
[1.0] rp1_gpclk_dkms: loading out-of-tree module taints kernel.
[2.0] rp1-gpclk-missing-active: error -ENODEV: pinctrl resource acquisition failed
[3.0] pinctrl-rp1 1f000d0000.gpio: pin gpio4 already requested by target:rp1-gpclk-dkms; cannot claim for target:rp1-gpclk-conflict
[3.1] pinctrl-rp1 1f000d0000.gpio: error -EINVAL: pin-4 (target:rp1-gpclk-conflict)
[3.2] pinctrl-rp1 1f000d0000.gpio: error -EINVAL: could not request pin 4 (gpio4) from group gpio4 on device pinctrl-rp1
[3.3] target:rp1-gpclk-conflict: Error applying setting, reverse things back
[4.0] rp1-gpclk-dma-conflict: error -EBUSY: endpoint resource ownership conflict
[4.1] rp1-gpclk-dma-conflict: probe with driver rp1-gpclk-dkms failed with error -16
[5.0] rp1-gpclk-bad-dma: error -ENOENT: device-tree identity validation failed
[5.1] rp1-gpclk-bad-dma: probe with driver rp1-gpclk-dkms failed with error -2
"""


def run(text: str) -> subprocess.CompletedProcess[str]:
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as evidence:
        evidence.write(text)
        evidence.flush()
        return subprocess.run(
            [str(CHECKER), evidence.name],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )


if run(EXPECTED).returncode != 0:
    raise SystemExit("expected diagnostics were rejected")
for dangerous in (
    "WARNING: pin 4 busy",
    "BUG: rp1-gpclk pin 4 busy",
    "Oops: rp1_gpclk pin 4 busy",
    "Call Trace: rp1-gpclk pin 4 busy",
    "rp1-gpclk: cleanup failed",
    "pinctrl-rp1: pin gpio4 already requested by unrelated; cannot claim for stranger",
):
    if run(EXPECTED + dangerous + "\n").returncode == 0:
        raise SystemExit(f"dangerous diagnostic passed: {dangerous}")
print("Phase 2E dmesg classifier: PASS")
