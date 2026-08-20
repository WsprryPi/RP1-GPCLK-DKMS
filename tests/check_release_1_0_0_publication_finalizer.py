#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import finalize_release_publication as finalizer

SOURCE = ROOT / "dist/release-1.0.0"

with tempfile.TemporaryDirectory() as temporary:
    release = Path(temporary) / "release"
    shutil.copytree(SOURCE, release)
    finalizer.finalize(release, "1" * 40)
    metadata = json.loads((release / "release-metadata.json").read_text())
    assert metadata["tagPresent"] is True
    assert metadata["publishable"] is True
    assert metadata["releaseDecisionCommit"] == "1" * 40
    checksums = {}
    for line in (release / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split("  ", 1)
        checksums[name] = digest
    assert set(checksums) == set(finalizer.FILES)
    for name, digest in checksums.items():
        assert finalizer.sha256(release / name) == digest
    assert finalizer.sha256(release / finalizer.PRODUCT) == finalizer.PRODUCT_SHA256
    assert finalizer.sha256(release / finalizer.QUALIFICATION) == finalizer.QUALIFICATION_SHA256
    try:
        finalizer.finalize(release, "2" * 40)
    except ValueError:
        pass
    else:
        raise AssertionError("already finalized sidecars accepted")

print("Release 1.0.0 publication finalizer: PASS")
