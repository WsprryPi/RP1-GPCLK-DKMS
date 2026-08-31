#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Finalize tag-dependent outer sidecars without changing sealed artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

TAG = "v1.0.0"
PRODUCT = "rp1-gpclk-dkms_1.0.0-1_all.deb"
QUALIFICATION = "rp1-gpclk-dkms-qualification-1.0.0.tar.gz"
PRODUCT_SHA256 = "951289ee5d0e44cff41b59756f00161aba16f43f1450715ba57c4a3679a2e6b8"
QUALIFICATION_SHA256 = "c05f2f2adc20b9e99bf37d775c4bddd6cafd27e5da5e9c62410784fb835727d2"
FILES = (
    "COMPATIBILITY.json", "PRODUCT-INVENTORY.json", "QUALIFICATION.json",
    "TARGET-VERIFICATION.json", "release-metadata.json", QUALIFICATION, PRODUCT,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def finalize(root: Path, decision_commit: str) -> None:
    if not root.is_dir() or root.is_symlink():
        raise ValueError("release directory must be a real directory")
    if set(path.name for path in root.iterdir()) != set(FILES) | {"SHA256SUMS"}:
        raise ValueError("release directory inventory differs")
    if sha256(root / PRODUCT) != PRODUCT_SHA256:
        raise ValueError("sealed product identity differs")
    if sha256(root / QUALIFICATION) != QUALIFICATION_SHA256:
        raise ValueError("sealed qualification identity differs")
    metadata_path = root / "release-metadata.json"
    metadata = json.loads(metadata_path.read_text())
    if metadata.get("release") != "1.0.0" or metadata.get("expectedTag") != TAG:
        raise ValueError("release identity differs")
    if metadata.get("productPackageSha256") != PRODUCT_SHA256:
        raise ValueError("metadata product identity differs")
    if metadata.get("qualificationArchiveSha256") != QUALIFICATION_SHA256:
        raise ValueError("metadata qualification identity differs")
    if metadata.get("tagPresent") is not False or metadata.get("publishable") is not False:
        raise ValueError("candidate sidecars are not in the expected prepublication state")
    metadata["releaseDecisionCommit"] = decision_commit
    metadata["tagPresent"] = True
    metadata["publishable"] = True
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    (root / "SHA256SUMS").write_text(
        "".join(f"{sha256(root / name)}  {name}\n" for name in sorted(FILES))
    )


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("release_directory", type=Path)
    args = parser.parse_args()
    raise SystemExit("historical release pipeline disabled for the 0.9.0 development baseline; see docs/contracts/development-identity.md; Step 12 review required")
    if git("status", "--porcelain", "--untracked-files=all"):
        raise SystemExit("refusing publication finalization from a dirty worktree")
    decision_commit = git("rev-parse", "HEAD")
    if TAG not in git("tag", "--points-at", "HEAD").splitlines():
        raise SystemExit(f"HEAD lacks exact release tag {TAG}")
    finalize(args.release_directory.resolve(), decision_commit)
    print(f"Release 1.0.0 publication sidecars: PASS ({decision_commit})")


if __name__ == "__main__":
    main()
