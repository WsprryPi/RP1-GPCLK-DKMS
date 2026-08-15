#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import copy
import importlib.util
import json
import pathlib
import tempfile
import hashlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("gate_d_attempts", ROOT / "scripts/gate_d_attempts.py")
assert spec and spec.loader
attempts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(attempts)

instance = json.loads((ROOT / "release/gate-d-execution-instance-v1.json").read_text())
plan = json.loads((ROOT / "release/gate-d-target-operation-plan-v1.json").read_text())
documents = attempts.generate(instance, plan)
assert len(documents) == 38
assert len({document["operationId"] for document in documents}) == 38
assert len({document["evidenceDirectory"] for document in documents}) == 38
assert sum(document["matrixRow"] == "interrupted-upgrade" for document in documents) == 15
assert sum(document["matrixRow"] == "removal-open-or-active" for document in documents) == 4

checked = ROOT / "release/gate-d-attempts-v1"
index = json.loads((checked / "index.json").read_text())
assert index["attemptCount"] == 38
assert set(index["executors"]) == {"attemptGenerator", "permanentExecutor"}
for executor in index["executors"].values():
    assert executor["sha256"] == hashlib.sha256(
        (ROOT / executor["path"]).read_bytes()).hexdigest()
assert len(index["attempts"]) == 38
for record, generated in zip(index["attempts"], documents):
    path = checked / record["file"]
    assert path.is_file() and not path.is_symlink()
    assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]
    assert json.loads(path.read_text()) == generated

for document in documents:
    result = attempts.execute_fake(document)
    assert result["status"] == "complete" and result["evidenceSealed"]
    assert result["servicesRestored"] and result["liveOutput"] is False
    assert result["commands"] == [[item["operation"]] for item in document["steps"]]

with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
    first_path = pathlib.Path(first) / "bundle"
    second_path = pathlib.Path(second) / "bundle"
    index_one = attempts.write_bundle(first_path, documents, ROOT / "scripts/gate_d_attempts.py")
    index_two = attempts.write_bundle(second_path, documents, ROOT / "scripts/gate_d_attempts.py")
    assert index_one == index_two
    assert [(path.name, path.read_bytes()) for path in sorted(first_path.iterdir())] == [
        (path.name, path.read_bytes()) for path in sorted(second_path.iterdir())]

base = documents[0]
mutations = (
    lambda value: value["steps"][0].update(operation="arbitrary-command"),
    lambda value: value["steps"][0]["action"]["argv"].append("${UNRESOLVED}"),
    lambda value: value["steps"][0]["action"]["argv"].append("*"),
    lambda value: value.update(evidenceDirectory="/var/lib/rp1-gpclk-dkms/gate-d/../escape"),
    lambda value: value["inputs"].update(candidateArchive="/tmp/../escape"),
    lambda value: value["inputs"].pop("tooling"),
    lambda value: value["steps"].pop(),
)
for mutation in mutations:
    bad = copy.deepcopy(base)
    mutation(bad)
    try:
        attempts.validate_document(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("unsafe or incomplete executable attempt accepted")

state = attempts.FakeSystem(base)
state.dispatch("create-evidence")
state.services["wsprrypi"] = "inactive"
for operation in ("capture-preflight", "verify-input-hashes", "snapshot-services"):
    state.dispatch(operation)
try:
    state.dispatch("quiesce-services")
except ValueError:
    pass
else:
    raise AssertionError("service pre-state drift was accepted")

sealed = attempts.FakeSystem(base)
sealed.evidence_created = True
sealed.dispatch("seal-evidence")
try:
    sealed.dispatch("capture-preflight")
except ValueError:
    pass
else:
    raise AssertionError("sealed evidence accepted further mutation")

deadline = copy.deepcopy(base)
deadline["deadlineSeconds"] = 1
attempts.validate_document(deadline)
try:
    attempts.execute_fake(deadline)
except TimeoutError:
    pass
else:
    raise AssertionError("attempt-total deadline was reset between steps")

print("Gate D executable attempt bundle and stateful fake system: PASS (38 attempts)")
