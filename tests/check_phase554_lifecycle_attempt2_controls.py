#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import pathlib
import subprocess
import tarfile
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
validator = ROOT / "scripts/phase554_lifecycle_controls.py"
plan = ROOT / "release/phase5.54-lifecycle-attempt2-v1.json"
builder = ROOT / "scripts/build_phase554_lifecycle_attempt2_bundle.py"

subprocess.run([str(validator), "validate", "--plan", str(plan)], check=True)
rendered = subprocess.run(
    [str(validator), "render", "--plan", str(plan)], check=True,
    text=True, stdout=subprocess.PIPE
).stdout
assert "rp1-gpclk-gpio20" in rendered and "gpio4" not in rendered
assert "live_output=0" in rendered and "live_output=1" not in rendered
assert "ATTEMPT_OVERLAY_ID" in rendered

with tempfile.TemporaryDirectory() as temporary:
    first = pathlib.Path(temporary) / "first.tar.gz"
    second = pathlib.Path(temporary) / "second.tar.gz"
    subprocess.run([str(builder), str(first)], check=True)
    subprocess.run([str(builder), str(second)], check=True)
    assert first.read_bytes() == second.read_bytes()
    with tarfile.open(first, "r:gz") as archive:
        assert archive.getnames() == [
            "rp1-gpclk-dkms-phase5.54-lifecycle-attempt2-controls/phase5.54-lifecycle-attempt2-v1.json",
            "rp1-gpclk-dkms-phase5.54-lifecycle-attempt2-controls/phase554_lifecycle_controls.py",
            "rp1-gpclk-dkms-phase5.54-lifecycle-attempt2-controls/gate_d_uapi_probe.c",
        ]
        assert all(member.isfile() for member in archive)

print("Phase 5.54 GPIO20 lifecycle controls: PASS")
