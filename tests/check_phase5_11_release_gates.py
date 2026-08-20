#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
document = json.loads((ROOT / "release/release-integration-gates-v1.json").read_text())
ORDER = [
    "debian-package-construction", "inactive-target-installation",
    "gpio4-output-disabled-lifecycle", "gpio20-output-disabled-lifecycle",
    "package-removal-reinstall", "closure-reconciliation",
    "offline-checks-twice", "semantic-version-selection",
    "final-artifact-reproduction", "release-review-and-claim-audit",
    "module-publication", "public-download-verification", "consumer-integration",
]
GATE_KEYS = {"id", "owner", "requires", "status", "evidence", "claimCeiling"}


def validate(value: dict) -> None:
    if value.get("schemaVersion") != 2:
        raise ValueError("invalid Phase 5.54 release-gate schema")
    if value.get("release") != "0.0.0-phase5.54" or value.get("debianVersion") != "0.0.0~phase5.54-2":
        raise ValueError("active Phase 5.54 identity differs")
    if value.get("expectedTag") is not None:
        raise ValueError("semantic release tag has not been selected")
    if value.get("currentClassification") != "validated-development-candidate":
        raise ValueError("development candidate classification differs")
    if value.get("modulePublicationConfirmed") is not False:
        raise ValueError("module publication is not confirmed")
    if value.get("publishedReleaseRequiresPostDownloadVerification") is not True:
        raise ValueError("fresh public-download verification is mandatory")
    if value.get("gateOrder") != ORDER:
        raise ValueError("Phase 5.54 gate order differs")
    gates = value.get("gates")
    if not isinstance(gates, list) or [gate.get("id") for gate in gates] != ORDER:
        raise ValueError("gates are missing duplicated extra or reordered")
    for index, gate in enumerate(gates):
        if set(gate) != GATE_KEYS or gate["status"] not in {"blocked", "passed"}:
            raise ValueError(f"invalid gate {gate.get('id')}")
        if not gate["evidence"] or not all(isinstance(x, str) and x for x in gate["evidence"]):
            raise ValueError(f"missing evidence for {gate['id']}")
        if not gate["claimCeiling"]:
            raise ValueError(f"missing claim ceiling for {gate['id']}")
        required = [] if index == 0 else [ORDER[index - 1]]
        if gate["requires"] != required:
            raise ValueError(f"nonlinear prerequisite for {gate['id']}")
        if index and gate["status"] == "passed" and gates[index - 1]["status"] != "passed":
            raise ValueError(f"gate passed before prerequisite for {gate['id']}")
    snapshot = value["candidateSnapshot"]
    if snapshot["packageSha256"] != "f61286a6e63c2735413a0e86d13c5dc2d91f4581e8a20aab7291234b1991f90b":
        raise ValueError("package digest differs")
    if snapshot["consumableByDependentRelease"] is not False:
        raise ValueError("unpublished candidate cannot be consumed")
    evidence = " ".join(" ".join(g["evidence"]) for g in gates)
    for term in ("GPIO4", "GPIO20", "live_output=0", "SemVer", "fresh location", "module-before-adapter-before-application"):
        if term not in evidence:
            raise ValueError(f"required boundary absent: {term}")


validate(document)
by_id = {gate["id"]: gate for gate in document["gates"]}
for identity in ORDER[:5]:
    assert by_id[identity]["status"] == "passed"
for identity in ORDER[5:]:
    assert by_id[identity]["status"] == "blocked"
assert "phase5.54-lifecycle-attempt1-success.json" in " ".join(by_id["gpio4-output-disabled-lifecycle"]["evidence"])
assert "phase5.54-lifecycle-attempt2-success.json" in " ".join(by_id["gpio20-output-disabled-lifecycle"]["evidence"])
assert "phase5.54-package-removal-reinstall-success.json" in " ".join(by_id["package-removal-reinstall"]["evidence"])

for mutation in (
    lambda value: value.update(expectedTag="v0.1.0"),
    lambda value: value.update(modulePublicationConfirmed=True),
    lambda value: value["gates"].pop(),
    lambda value: value["gates"][6].update(status="passed"),
    lambda value: value["gates"][1].update(requires=[]),
):
    invalid = copy.deepcopy(document)
    mutation(invalid)
    try:
        validate(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid Phase 5.54 release roadmap accepted")

print("Phase 5.54 release and integration gates: PASS")
