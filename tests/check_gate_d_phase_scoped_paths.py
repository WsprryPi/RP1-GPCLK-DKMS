#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import copy
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import gate_d_attempts


def paths(document: dict) -> set[str]:
    result = {
        document["evidenceDirectory"], document["journal"],
        document["inputs"]["stagingDirectory"], *document["inputs"]["ownedPaths"],
    }
    subordinate = document["inputs"]["subordinateLifecycle"]
    if subordinate:
        for role in ("transition", "recovery"):
            evidence = subordinate[role]["evidenceDirectory"]
            result.update({evidence, f"{evidence}/transaction.json"})
    return result


instance = json.loads((ROOT / "release/gate-d-execution-instance-v1.json").read_text())
plan = json.loads((ROOT / "release/gate-d-target-operation-plan-v1.json").read_text())
candidate = instance["candidate"]
candidate.update(release="0.0.0-phase5.45", sourceCommit="f" * 40)
namespace = "phase5.45-ffffffffffff"
instance["executionPolicy"]["attemptPathNamespace"] = namespace
for row in instance["rows"]:
    row["evidenceDirectory"] = f"gate-d/runs/{namespace}/{row['id']}"

documents = gate_d_attempts.generate(instance, plan)
successor_paths: set[str] = set()
for document in documents:
    current = paths(document)
    assert all(namespace in path for path in current)
    assert not successor_paths & current
    successor_paths.update(current)

historical_paths: set[str] = set()
for phase in ("phase5.42", "phase5.43"):
    directory = ROOT / f"release/gate-d-attempts-{phase}-v1"
    index = json.loads((directory / "index.json").read_text())
    for record in index["attempts"]:
        historical_paths.update(paths(json.loads((directory / record["file"]).read_text())))
retirement = json.loads((
    ROOT / "release/gate-d-phase5.42-first-attempt-evidence-retirement-v1.json").read_text())
historical_paths.add(retirement["destination"]["evidenceDirectory"])

assert not successor_paths & historical_paths

bad = copy.deepcopy(instance)
bad["rows"][0]["evidenceDirectory"] = "gate-d/current-supported-kernel"
try:
    gate_d_attempts.generate(bad, plan)
except ValueError:
    pass
else:
    raise AssertionError("one unscoped successor row was accepted")

print("Gate D phase-scoped path closure: PASS (38 attempts, no historical collisions)")
