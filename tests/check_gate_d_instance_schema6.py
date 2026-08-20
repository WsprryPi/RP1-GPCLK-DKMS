#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Exercise schema-6 attempt-version and preauthorization semantics."""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import gate_d_instance
import gate_d_root

base = json.loads((ROOT / "release/gate-d-execution-instance-phase5.48-v1.json").read_text())
base["schemaVersion"] = 6
base["executionPolicy"]["attemptSchemaVersion"] = 2
base["authorization"]["approved"] = False
base["authorization"]["targetExecutionApproved"] = False
base["authorization"]["approvalScope"] = \
    "Offline construction only; target execution is not authorized."
base["executionReady"] = False

original = gate_d_root.validate
gate_d_root.validate = lambda reference, verify=True: ROOT
try:
    result = gate_d_instance.validate(
        base, validate_attempt_bundle=False, enforce_candidate_status=False)
    assert result["inputsReady"] is True and result["executionReady"] is False
    try:
        gate_d_instance.validate(
            base, require_ready=True, validate_attempt_bundle=False,
            enforce_candidate_status=False)
    except ValueError as error:
        assert str(error) == "fresh target-execution authorization is required"
    else:
        raise AssertionError("unapproved schema-6 instance became ready")

    authorized = copy.deepcopy(base)
    authorized["authorization"]["approved"] = True
    authorized["authorization"]["targetExecutionApproved"] = True
    authorized["executionReady"] = True
    assert gate_d_instance.validate(
        authorized, require_ready=True, validate_attempt_bundle=False,
        enforce_candidate_status=False)["executionReady"] is True

    for mutation in (
        lambda value: value["executionPolicy"].update(attemptSchemaVersion=1),
        lambda value: value["executionPolicy"].pop("attemptSchemaVersion"),
        lambda value: value["authorization"].update(approved=True),
        lambda value: value.update(executionReady=True),
    ):
        bad = copy.deepcopy(base)
        mutation(bad)
        try:
            gate_d_instance.validate(
                bad, validate_attempt_bundle=False, enforce_candidate_status=False)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid schema-6 instance accepted")
finally:
    gate_d_root.validate = original

print("Gate D execution-instance schema 6: PASS")
