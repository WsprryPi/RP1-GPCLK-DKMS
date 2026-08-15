#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Fail-closed semantic validation for the Gate D version pair."""

from __future__ import annotations

import argparse
import json
import pathlib
import re

SHA256 = re.compile(r"[0-9a-f]{64}")
COMMIT = re.compile(r"[0-9a-f]{40}")
VERSION = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+-[0-9A-Za-z][0-9A-Za-z.-]*")


def load(path: pathlib.Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError("version pair must be a real file")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("version pair must be an object")
    return value


def validate(value: dict) -> dict:
    if set(value) != {"SPDX-License-Identifier", "schemaVersion", "kind", "predecessor", "successor", "transition"} or value.get("SPDX-License-Identifier") != "MIT" or value.get("schemaVersion") != 1 or value.get("kind") != "gate-d-version-pair":
        raise ValueError("invalid version-pair identity")
    release_fields = {"version", "sourceCommit", "archive", "archiveSha256", "uapiSha256",
                      "manifestSha256", "gpio4DtboSha256", "gpio20DtboSha256",
                      "packageComplete", "evidence"}
    for label in ("predecessor", "successor"):
        release = value[label]
        if not isinstance(release, dict) or set(release) != release_fields:
            raise ValueError(f"incomplete {label} identity")
        if not VERSION.fullmatch(release["version"]) or not COMMIT.fullmatch(release["sourceCommit"]):
            raise ValueError(f"invalid {label} version or commit")
        expected_archive = f"rp1-gpclk-dkms-{release['version']}.tar.gz"
        if release["archive"] != expected_archive:
            raise ValueError(f"{label} archive name differs from version")
        for field in ("archiveSha256", "uapiSha256", "manifestSha256", "gpio4DtboSha256", "gpio20DtboSha256"):
            if not isinstance(release[field], str) or not SHA256.fullmatch(release[field]):
                raise ValueError(f"invalid {label} {field}")
        if release["packageComplete"] is not True:
            raise ValueError(f"{label} is not a complete restorable package state")
        if not isinstance(release["evidence"], list) or not release["evidence"] or len(release["evidence"]) != len(set(release["evidence"])) or not all(isinstance(item, str) and item for item in release["evidence"]):
            raise ValueError(f"invalid {label} evidence")
    predecessor, successor = value["predecessor"], value["successor"]
    if predecessor["version"] == successor["version"] or predecessor["sourceCommit"] == successor["sourceCommit"] or predecessor["archiveSha256"] == successor["archiveSha256"]:
        raise ValueError("predecessor and successor are not genuinely distinct")
    transition = value["transition"]
    expected = {"upgrade": "predecessor-to-successor", "downgrade": "successor-to-predecessor",
                "rollback": "failed-successor-to-exact-predecessor",
                "interruption": "exactly-one-complete-inactive-version", "outputEnabled": False}
    if transition != expected:
        raise ValueError("transition contract differs")
    return {"valid": True, "predecessor": predecessor["version"],
            "successor": successor["version"], "outputEnabled": False}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pair", type=pathlib.Path)
    args = parser.parse_args()
    print(json.dumps(validate(load(args.pair)), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
