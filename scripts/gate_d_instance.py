#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate a concrete Gate D representative-system execution instance."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import hashlib

ROWS = (
    "current-supported-kernel", "prior-supported-kernel-downgrade", "newer-unknown-kernel",
    "signing-not-enforced", "signing-enforced-enrolled-key", "deliberate-build-failure",
    "deliberate-signature-rejection", "missing-headers", "overlay-or-resource-conflict",
    "interrupted-upgrade", "stale-manifest", "corrupted-archive-or-dtbo",
    "removal-inactive", "removal-open-or-active", "reinstall-after-removal",
)
POSITIVE_ROUTE_ROWS = {
    "current-supported-kernel", "prior-supported-kernel-downgrade",
    "signing-not-enforced", "deliberate-build-failure", "interrupted-upgrade",
    "removal-inactive", "removal-open-or-active", "reinstall-after-removal",
}
ROUTES = {"gpio4", "gpio20", "route-neutral"}
STATUSES = {"ready", "blocked-input-required", "deferred-environmental"}
SHA256 = re.compile(r"[0-9a-f]{64}")
ROOT = pathlib.Path(__file__).resolve().parents[1]


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: pathlib.Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError("execution instance must be a real file")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("execution instance must be an object")
    return value


def validate(value: dict, *, require_ready: bool = False) -> dict:
    required = {"SPDX-License-Identifier", "schemaVersion", "kind", "matrixRelease",
                "executionPolicy", "candidate", "authorization", "systems", "recovery",
                "rows", "inputsReady", "executionReady"}
    if set(value) != required or value.get("SPDX-License-Identifier") != "MIT" or value.get("schemaVersion") != 1 or value.get("kind") != "gate-d-representative-system-execution-instance":
        raise ValueError("invalid execution-instance identity")
    policy_ref = value["executionPolicy"]
    policy_fields = {"matrixPolicy", "matrixPolicySha256", "routeDecision",
                     "routeDecisionSha256", "environmentalCoverageComplete"}
    if not isinstance(policy_ref, dict) or set(policy_ref) != policy_fields:
        raise ValueError("execution-policy references are incomplete")
    for path_field, hash_field in (("matrixPolicy", "matrixPolicySha256"),
                                   ("routeDecision", "routeDecisionSha256")):
        relative = policy_ref[path_field]
        if (not isinstance(relative, str) or pathlib.PurePosixPath(relative).is_absolute() or
                ".." in pathlib.PurePosixPath(relative).parts):
            raise ValueError("unsafe execution-policy path")
        path = ROOT / relative
        if not path.is_file() or path.is_symlink() or sha256(path) != policy_ref[hash_field]:
            raise ValueError("execution-policy identity mismatch")
    matrix_policy = json.loads((ROOT / policy_ref["matrixPolicy"]).read_text(encoding="utf-8"))
    if (matrix_policy.get("schemaVersion") != 2 or
            [row.get("id") for row in matrix_policy.get("rows", [])] != list(ROWS)):
        raise ValueError("matrix execution policy is incomplete")
    classifications = {row["id"]: row.get("classification") for row in matrix_policy["rows"]}
    if not set(classifications.values()).issubset({"required-executable", "deferred-environmental"}):
        raise ValueError("unknown matrix execution classification")
    route_decision = json.loads((ROOT / policy_ref["routeDecision"]).read_text(encoding="utf-8"))
    if (route_decision.get("kind") != "gate-d-route-compatibility-decision" or
            route_decision.get("candidate", {}).get("release") != value.get("candidate", {}).get("release") or
            route_decision.get("candidate", {}).get("sourceCommit") != value.get("candidate", {}).get("sourceCommit")):
        raise ValueError("route decision differs from candidate")
    route_entries = route_decision.get("routes")
    if (not isinstance(route_entries, list) or
            {entry.get("route") for entry in route_entries} != {"GPIO4", "GPIO20"} or
            any(entry.get("liveEligible") is not False for entry in route_entries)):
        raise ValueError("route decision is incomplete or live-enabled")
    positive_routes = {entry["route"].lower() for entry in route_entries
                       if entry.get("state") == "Compatible-unqualified"}
    boundary = route_decision.get("decisionBoundary", {})
    if bool(positive_routes) != (boundary.get("positiveExecutionCompatibilityDecisionEstablished") is True):
        raise ValueError("route decision positive-entry boundary disagrees with entries")
    candidate = value["candidate"]
    candidate_fields = {"status", "sourceCommit", "release", "archiveSha256", "uapiSha256",
                        "manifestSha256", "gpio4DtboSha256", "gpio20DtboSha256"}
    if not isinstance(candidate, dict) or set(candidate) != candidate_fields:
        raise ValueError("candidate identity fields are incomplete")
    if candidate["status"] not in {"unfrozen", "frozen"}:
        raise ValueError("unknown candidate status")
    identity_fields = candidate_fields - {"status", "release"}
    if candidate["status"] == "frozen":
        if not isinstance(candidate["release"], str) or not candidate["release"]:
            raise ValueError("frozen candidate lacks release")
        if any(not isinstance(candidate[field], str) or not SHA256.fullmatch(candidate[field])
               for field in identity_fields - {"sourceCommit"}):
            raise ValueError("frozen candidate lacks exact hashes")
        if not isinstance(candidate["sourceCommit"], str) or not re.fullmatch(r"[0-9a-f]{40}", candidate["sourceCommit"]):
            raise ValueError("frozen candidate lacks exact commit")
    elif any(candidate[field] is not None for field in candidate_fields - {"status"}):
        raise ValueError("unfrozen candidate must not carry provisional identities")
    authorization = value["authorization"]
    auth_fields = {"approved", "targetExecutionApproved", "approvalScope", "administrator", "connection", "serviceChanges", "packagePrerequisites",
                   "dkms", "moduleAdministration", "overlayAdministration", "kernelSwitching",
                   "reboot", "failureInjection", "cleanup", "prohibitions"}
    if not isinstance(authorization, dict) or set(authorization) != auth_fields or authorization["approved"] is not True:
        raise ValueError("authorization fields are incomplete or unapproved")
    if type(authorization["targetExecutionApproved"]) is not bool or not isinstance(authorization["approvalScope"], str) or not authorization["approvalScope"]:
        raise ValueError("target execution authorization is ambiguous")
    if not isinstance(authorization["prohibitions"], list) or not authorization["prohibitions"]:
        raise ValueError("authorization prohibitions are absent")
    required_prohibitions = {"active-pinctrl", "clock-enable", "dma-submit", "gpio-output",
                             "si5351-operation", "transmitter-keying", "sdr-operation",
                             "antenna-connection", "rf", "devmem-fallback",
                             "custom-kernel-qualification", "forced-removal",
                             "general-upgrade", "unreviewed-persistent-boot-change"}
    if not required_prohibitions.issubset(set(authorization["prohibitions"])):
        raise ValueError("mandatory Gate D prohibition is absent")
    systems = value["systems"]
    if not isinstance(systems, list) or not systems:
        raise ValueError("systems are absent")
    system_ids = set()
    for system in systems:
        fields = {"id", "role", "host", "model", "revision", "architecture", "os", "kernels",
                  "signingEnforced", "headers", "compiler", "routes", "stableIdentifier"}
        if not isinstance(system, dict) or set(system) != fields or system["id"] in system_ids:
            raise ValueError("system fields are incomplete or duplicated")
        system_ids.add(system["id"])
        if system["routes"] and not set(system["routes"]).issubset({"gpio4", "gpio20"}):
            raise ValueError("system has an arbitrary route")
    recovery = value["recovery"]
    recovery_fields = {"rescueHost", "bootOrder", "rootSource", "bootSource", "nvmeVisibleUnmounted",
                       "sshReturnSeconds", "automaticRecoverySeconds", "assistanceSeconds", "validated"}
    if not isinstance(recovery, dict) or set(recovery) != recovery_fields or recovery["validated"] is not True:
        raise ValueError("recovery contract is incomplete or unvalidated")
    if not (0 < recovery["sshReturnSeconds"] <= recovery["automaticRecoverySeconds"] <= recovery["assistanceSeconds"] <= 1800):
        raise ValueError("recovery deadlines are invalid")
    rows = value["rows"]
    if not isinstance(rows, list) or tuple(row.get("id") for row in rows) != ROWS:
        raise ValueError("matrix rows are missing, duplicated, or reordered")
    evidence = set()
    blocked = []
    deferred = []
    for row in rows:
        fields = {"id", "status", "systemId", "kernel", "routes", "deadlineSeconds",
                  "evidenceDirectory", "failureInjection", "expectedFinalState", "blockers"}
        if not isinstance(row, dict) or set(row) != fields or row["status"] not in STATUSES:
            raise ValueError(f"invalid row contract: {row.get('id')}")
        if row["systemId"] is not None and row["systemId"] not in system_ids:
            raise ValueError(f"unknown system for {row['id']}")
        routes = row["routes"]
        if (not isinstance(routes, list) or not routes or len(routes) != len(set(routes)) or
                not set(routes).issubset(ROUTES) or
                ("route-neutral" in routes and len(routes) != 1) or
                not isinstance(row["deadlineSeconds"], int) or not 1 <= row["deadlineSeconds"] <= 1800):
            raise ValueError(f"invalid route or deadline for {row['id']}")
        directory = row["evidenceDirectory"]
        if not isinstance(directory, str) or not directory or directory in evidence or ".." in pathlib.PurePosixPath(directory).parts or pathlib.PurePosixPath(directory).is_absolute():
            raise ValueError(f"unsafe or duplicate evidence directory for {row['id']}")
        evidence.add(directory)
        if not isinstance(row["blockers"], list):
            raise ValueError(f"invalid blockers for {row['id']}")
        if row["status"] == "ready" and row["blockers"]:
            raise ValueError(f"ready row retains blockers: {row['id']}")
        if row["status"] == "ready" and (row["systemId"] is None or row["kernel"] is None):
            raise ValueError(f"ready row lacks exact system or kernel: {row['id']}")
        required_routes = set(row["routes"]) - {"route-neutral"}
        if (row["status"] == "ready" and row["id"] in POSITIVE_ROUTE_ROWS and
                not required_routes.issubset(positive_routes)):
            raise ValueError(f"ready row lacks positive non-live route decision: {row['id']}")
        if row["status"] != "ready" and not row["blockers"]:
            raise ValueError(f"blocked row lacks blockers: {row['id']}")
        classification = classifications[row["id"]]
        if row["status"] == "deferred-environmental":
            if classification != "deferred-environmental":
                raise ValueError(f"non-environmental row deferred: {row['id']}")
            deferred.append(row["id"])
        elif classification == "deferred-environmental":
            raise ValueError(f"environmental row is not deferred: {row['id']}")
        elif row["status"] != "ready":
            blocked.append(row["id"])
    expected_inputs = candidate["status"] == "frozen" and not blocked
    if value["inputsReady"] is not expected_inputs:
        raise ValueError("inputsReady disagrees with candidate and required rows")
    expected_ready = expected_inputs and authorization["targetExecutionApproved"]
    if value["executionReady"] is not expected_ready:
        raise ValueError("executionReady disagrees with candidate and rows")
    if require_ready and not expected_ready:
        raise ValueError("execution instance is blocked-input-required")
    expected_environmental = not deferred
    if policy_ref["environmentalCoverageComplete"] is not expected_environmental:
        raise ValueError("environmentalCoverageComplete disagrees with deferred rows")
    return {"valid": True, "inputsReady": expected_inputs, "executionReady": expected_ready,
            "environmentalCoverageComplete": expected_environmental,
            "blockedRows": blocked, "deferredRows": deferred, "readOnly": True}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("instance", type=pathlib.Path)
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    print(json.dumps(validate(load(args.instance), require_ready=args.require_ready), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
