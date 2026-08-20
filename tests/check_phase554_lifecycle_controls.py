#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import hashlib
import pathlib
import subprocess
import tarfile
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
validator = ROOT / "scripts/phase554_lifecycle_controls.py"
builder = ROOT / "scripts/build_phase554_lifecycle_bundle.py"

subprocess.run([str(validator), "validate"], check=True)
rendered = subprocess.run([str(validator), "render"], check=True, text=True,
                          stdout=subprocess.PIPE).stdout
assert "live_output=0" in rendered
assert "ATTEMPT_OVERLAY_ID" in rendered
assert "live_output=1" not in rendered and "/dev/mem" not in rendered

with tempfile.TemporaryDirectory() as temporary:
    first = pathlib.Path(temporary) / "first.tar.gz"
    second = pathlib.Path(temporary) / "second.tar.gz"
    subprocess.run([str(builder), str(first)], check=True)
    subprocess.run([str(builder), str(second)], check=True)
    assert first.read_bytes() == second.read_bytes()
    with tarfile.open(first, "r:gz") as archive:
        names = archive.getnames()
        assert names == [
            "rp1-gpclk-dkms-phase5.54-lifecycle-controls/phase5.54-lifecycle-attempt1-v1.json",
            "rp1-gpclk-dkms-phase5.54-lifecycle-controls/phase554_lifecycle_controls.py",
            "rp1-gpclk-dkms-phase5.54-lifecycle-controls/gate_d_uapi_probe.c",
        ]
        assert all(not member.issym() and not member.islnk() for member in archive)
    assert len(hashlib.sha256(first.read_bytes()).hexdigest()) == 64

print("Phase 5.54 lifecycle control bundle: PASS")
