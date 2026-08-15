#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
layout = json.loads((ROOT / "release/release-layout-v1.json").read_text())
release = layout["release"]

assert re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+-[0-9A-Za-z][0-9A-Za-z.-]*", release)
assert layout["expectedTag"] == f"v{release}"
assert f'PACKAGE_VERSION="{release}"' in (ROOT / "dkms.conf").read_text()
assert f'RP1_GPCLK_MODULE_VERSION "{release}"' in (ROOT / "include/rp1_gpclk/version.h").read_text()
assert release in (ROOT / f"docs/releases/{release}-security.md").read_text()
assert release in (ROOT / f"docs/releases/{release}-behavior.md").read_text()

artifact_ids = [item["id"] for item in layout["artifacts"]]
assert len(artifact_ids) == len(set(artifact_ids))
required_ids = {"source-archive", "module-source", "module-headers", "kbuild", "makefile", "dkms-conf", "kernel-module",
                "canonical-uapi", "gpio4-overlay-source", "gpio20-overlay-source", "gpio4-dtbo", "gpio20-dtbo",
                "compatibility-schema", "compatibility-manifest", "provenance", "checksums", "release-metadata",
                "lifecycle-tool", "diagnostic-tool", "operator-docs", "security-notes", "behavioral-notes", "signing-guidance"}
assert required_ids == set(artifact_ids)
for item in layout["artifacts"]:
    assert item["destination"] and item["owner"] and item["group"]
    assert item["mode"] in {"0600", "0644", "0755"}
    assert item["replacement"] and item["removalOwner"]

lifecycle = (ROOT / "scripts/rp1-gpclk-lifecycle.sh").read_text()
for required in ("live_output=0", "dkms add", "dkms build", "dkms install", "dkms uninstall", "dkms remove", "sign-file", "overlay-build", "gpio4|gpio20"):
    assert required in lifecycle, f"lifecycle tool missing {required}"
for prohibited in ("/dev/mem", "gpio write", "live_output=1"):
    assert prohibited not in lifecycle, f"lifecycle tool contains prohibited operation {prohibited}"

diagnostics = (ROOT / "scripts/rp1-gpclk-diagnostics.py").read_text()
for prohibited in ("sudo", "modprobe", "dtoverlay", "dkms install", "dkms remove"):
    assert prohibited not in diagnostics, f"diagnostics contain mutating operation {prohibited}"

module_main = (ROOT / "src/rp1_gpclk_main.c").read_text()
release_gate = module_main[module_main.index("static bool rp1_gpclk_release_identity_allowed"):]
release_gate = release_gate[:release_gate.index("\n}")]
assert "return false;" in release_gate, "Phase 5.2 must remain live-ineligible without an exact manifest entry"

with tempfile.TemporaryDirectory() as tools_dir, tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
    fake_dtc = pathlib.Path(tools_dir) / "dtc"
    fake_dtc.write_text("""#!/bin/sh
if [ "$1" = "--version" ]; then echo 'Version: deterministic-test-dtc 1'; exit 0; fi
out=
input=
while [ "$#" -gt 0 ]; do
  if [ "$1" = "-o" ]; then shift; out=$1; else input=$1; fi
  shift
done
sha256sum "$input" | awk '{print $1}' >"$out"
""")
    fake_dtc.chmod(0o755)
    environment = dict(os.environ)
    environment["PATH"] = f"{tools_dir}:{environment['PATH']}"
    for destination in (first, second):
        subprocess.run([str(ROOT / "scripts/build_release.py"), destination, "--development"], check=True, env=environment)
        subprocess.run([str(ROOT / "scripts/validate_release.py"), destination, "--allow-development"], check=True, env=environment)
    names = sorted(path.name for path in pathlib.Path(first).iterdir())
    assert names == sorted(path.name for path in pathlib.Path(second).iterdir())
    for name in names:
        left = hashlib.sha256((pathlib.Path(first) / name).read_bytes()).hexdigest()
        right = hashlib.sha256((pathlib.Path(second) / name).read_bytes()).hexdigest()
        assert left == right, f"release artifact is not reproducible: {name}"
    metadata = json.loads((pathlib.Path(first) / "release-metadata.json").read_text())
    expected_dirty = bool(subprocess.check_output(["git", "-C", str(ROOT), "status", "--porcelain", "--untracked-files=all"], text=True))
    assert metadata["publishable"] is False and metadata["tagPresent"] is False
    assert metadata["dirtySource"] is expected_dirty
    checksum = pathlib.Path(first) / "SHA256SUMS"
    checksum.write_text(checksum.read_text().replace("0", "1", 1))
    result = subprocess.run([str(ROOT / "scripts/validate_release.py"), first, "--allow-development"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    assert result.returncode != 0, "tampered checksum unexpectedly passed"

print("Phase 5.2 release-unit contracts: PASS")
