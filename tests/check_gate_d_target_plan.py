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
assert tool.validate(plan) == result

for mutation in (
    lambda value: value["invariants"].update(liveOutput=True),
    lambda value: value["boot"].update(tryboot="/boot/firmware/config.txt"),
    lambda value: value["services"].pop(),
    lambda value: value["tooling"]["bootSelector"].update(sha256="0" * 63),
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

print("Gate D complete target operation plan: PASS")
