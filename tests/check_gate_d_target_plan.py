#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import copy
import importlib.util
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("gate_d_target_plan", ROOT / "scripts/gate_d_target_plan.py")
assert spec and spec.loader
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
plan = json.loads((ROOT / "release/gate-d-target-operation-plan-v1.json").read_text())
result = tool.validate(plan, verify_tools=False)
assert result == {"valid": True, "readOnly": True, "rowCount": 10, "attemptCount": 38, "liveOutput": False}
try:
    tool.validate(plan)
except ValueError as error:
    assert "legacy target plan" in str(error)
else:
    raise AssertionError("superseded Phase 5.14 plan was accepted for execution")
assert plan["artifacts"]["successor"] == {
    "version": "0.0.0-phase5.14",
    "archive": "/home/pi/gate-d-inputs/phase5.14-7bbdfe1b5c83/rp1-gpclk-dkms-0.0.0-phase5.14.tar.gz",
    "sha256": "d0c17f2842716052bb49b1a4fc079d3d48a5674bae8610eee2ab9d17ac548bea",
}

for mutation in (
    lambda value: value["invariants"].update(liveOutput=True),
    lambda value: value["boot"].update(tryboot="/boot/firmware/config.txt"),
    lambda value: value["services"].pop(),
    lambda value: value["tooling"]["bootSelector"].update(sha256="0" * 63),
    lambda value: value["artifacts"]["successor"].update(version="0.0.0-phase5.2"),
    lambda value: value["rows"][4]["attempts"].pop(),
    lambda value: value["rows"][8]["actions"].remove("start-busy-injector-and-wait-ready"),
    lambda value: value["rows"][0]["actions"].append("live_output=1"),
):
    bad = copy.deepcopy(plan)
    mutation(bad)
    try:
        tool.validate(bad, verify_tools=False)
    except ValueError:
        pass
    else:
        raise AssertionError("unsafe or incomplete Gate D target plan accepted")

# Schema 2 separates immutable source bytes from installed executable bytes.
current = copy.deepcopy(plan)
current["schemaVersion"] = 2
for item in current["tooling"].values():
    source_sha = __import__("hashlib").sha256((ROOT / item["sourcePath"]).read_bytes()).hexdigest()
    item.pop("sha256")
    item["sourceSha256"] = source_sha
    item["installKind"] = "target-built" if item["sourcePath"].endswith(".c") else "copied"
    item["installedSha256"] = "a" * 64 if item["installKind"] == "target-built" else source_sha
assert tool.validate(current)["attemptCount"] == 38
for mutation in (
    lambda value: value["tooling"]["bootSelector"].pop("sourceSha256"),
    lambda value: value["tooling"]["bootSelector"].pop("installedSha256"),
    lambda value: value["tooling"]["bootSelector"].update(installKind="target-built"),
    lambda value: value["tooling"]["busyInjector"].update(installKind="copied"),
    lambda value: value["tooling"]["bootSelector"].update(installedSha256="b" * 64),
    lambda value: value["tooling"]["bootSelector"].update(sourceSha256="c" * 64,
                                                               installedSha256="c" * 64),
):
    bad = copy.deepcopy(current)
    mutation(bad)
    try:
        tool.validate(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("split tooling identity mutation accepted")

print("Gate D complete target operation plan: PASS")
