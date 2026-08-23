#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Keep the installed-module verifier bound to the normative policy."""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
source = (ROOT / "scripts/verify_module_identity.py").read_text()
manifest = (ROOT / "release/compatibility-decisions-v1.json").read_text()

for token in (
    'ENTRY = "v1.0.1-wspr5-gpio4-6.18.34"',
    'subprocess.run([strip, "--strip-debug", str(installed)], check=True)',
    'build["moduleUnsignedSha256"]',
    'build["moduleInstalledSha256"]',
):
    assert token in source
assert '"moduleInstalledSha256":"1979d2dfdbe6a38d03be2c4b2a9acc29109a89ed56f4d860a0e65435af81133f"' in manifest
assert '"moduleInstalledTransform":"strip --strip-debug; hash uncompressed ELF before filesystem compression"' in manifest

print("installed-module identity verifier contract: PASS")
