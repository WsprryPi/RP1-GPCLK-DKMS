#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Exercise canonical snapshot binding and independent service validation."""
import copy
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import gate_d_attempts
import gate_d_service_contract

load = lambda relative: json.loads((ROOT / relative).read_text())
snapshot = load("docs/evidence/gate-d-live-target-snapshot-wspr5-phase5.47-v1.json")
plan = load("release/gate-d-target-operation-plan-phase5.47-v1.json")
instance = load("release/gate-d-execution-instance-phase5.47-v1.json")
attempt_dir = ROOT / "release/gate-d-attempts-phase5.47-v1"
index = load("release/gate-d-attempts-phase5.47-v1/index.json")
sealed = [json.loads((attempt_dir / item["file"]).read_text()) for item in index["attempts"]]

try:
    gate_d_service_contract.validate(snapshot, sealed)
except ValueError as error:
    assert str(error) == "attempt service contract differs from canonical snapshot"
else:
    raise AssertionError("sealed Phase 5.47 service mismatch was accepted")

bound_plan = gate_d_attempts.bind_services_to_snapshot(plan, snapshot)
expected = [
    {"action": "preserve", "name": item["name"], "requiredPreState": "inactive"}
    for item in plan["services"]
]
assert bound_plan["services"] == expected
assert plan["services"] != bound_plan["services"]
generated = gate_d_attempts.generate(instance, bound_plan)
result = gate_d_service_contract.validate(snapshot, generated)
assert result == {"valid": True, "attemptCount": 38, "serviceCount": 4, "readOnly": True}
for document in generated:
    fake = gate_d_attempts.execute_fake(document)
    assert fake["status"] == "complete" and fake["servicesRestored"] is True
    assert fake["liveOutput"] is False

for mutation in (
    lambda docs: docs[0]["services"][0].update(requiredPreState="active"),
    lambda docs: docs[0]["services"][0].update(action="stop-then-restore-exact"),
    lambda docs: docs[0]["services"].pop(),
    lambda docs: docs[1]["services"][0].update(requiredPreState="active",
                                               action="stop-then-restore-exact"),
    lambda docs: docs[0]["services"].append(copy.deepcopy(docs[0]["services"][0])),
):
    changed = copy.deepcopy(generated)
    mutation(changed)
    try:
        gate_d_service_contract.validate(snapshot, changed)
    except ValueError:
        pass
    else:
        raise AssertionError("mutated service contract was accepted")

bad_snapshot = copy.deepcopy(snapshot)
del bad_snapshot["services"]["wsprrypi.service"]
try:
    gate_d_attempts.bind_services_to_snapshot(plan, bad_snapshot)
except ValueError:
    pass
else:
    raise AssertionError("incomplete snapshot services were accepted")

print("Gate D canonical service-snapshot contract: PASS")
