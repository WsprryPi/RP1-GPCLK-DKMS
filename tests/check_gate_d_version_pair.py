#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import copy
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("gate_d_version_pair", ROOT / "scripts/gate_d_version_pair.py")
assert spec and spec.loader
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


def release(version: str, marker: str) -> dict:
    return {
        "version": version, "sourceCommit": marker * 40,
        "archive": f"rp1-gpclk-dkms-{version}.tar.gz", "archiveSha256": marker * 64,
        "uapiSha256": "a" * 64, "manifestSha256": "b" * 64,
        "gpio4DtboSha256": "c" * 64, "gpio20DtboSha256": "d" * 64,
        "packageComplete": True, "evidence": [f"evidence-{marker}"],
    }


pair = {
    "SPDX-License-Identifier": "MIT", "schemaVersion": 1, "kind": "gate-d-version-pair",
    "predecessor": release("0.0.0-phase5.2", "1"),
    "successor": release("0.0.0-phase5.13", "2"),
    "transition": {"upgrade": "predecessor-to-successor", "downgrade": "successor-to-predecessor",
                   "rollback": "failed-successor-to-exact-predecessor",
                   "interruption": "exactly-one-complete-inactive-version", "outputEnabled": False},
}
assert tool.validate(pair)["valid"]
actual = ROOT / "release/gate-d-version-pair-v1.json"
if actual.is_file():
    assert tool.validate(tool.load(actual))["valid"]
for mutation in (
    lambda value: value["successor"].update(version=value["predecessor"]["version"], archive=value["predecessor"]["archive"]),
    lambda value: value["successor"].update(sourceCommit=value["predecessor"]["sourceCommit"]),
    lambda value: value["successor"].update(archiveSha256=value["predecessor"]["archiveSha256"]),
    lambda value: value["predecessor"].update(packageComplete=False),
    lambda value: value["transition"].update(outputEnabled=True),
):
    invalid = copy.deepcopy(pair)
    mutation(invalid)
    try:
        tool.validate(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid Gate D version pair accepted")

print("Gate D version pair: PASS")
