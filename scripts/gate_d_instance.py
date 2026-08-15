#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate a concrete Gate D representative-system execution instance."""

from __future__ import annotations

import argparse
import json
import pathlib
import re

ROWS = (
    "current-supported-kernel", "prior-supported-kernel-downgrade", "newer-unknown-kernel",
    "signing-not-enforced", "signing-enforced-enrolled-key", "deliberate-build-failure",
    "deliberate-signature-rejection", "missing-headers", "overlay-or-resource-conflict",
    "interrupted-upgrade", "stale-manifest", "corrupted-archive-or-dtbo",
    "removal-inactive", "removal-open-or-active", "reinstall-after-removal",
)
ROUTES = {"gpio4", "gpio20", "route-neutral"}
STATUSES = {"ready", "blocked-input-required"}
SHA256 = re.compile(r"[0-9a-f]{64}")


def load(path: pathlib.Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError("execution instance must be a real file")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("execution instance must be an object")
    return value


def validate(value: dict, *, require_ready: bool = False) -> dict:
    required = {"SPDX-License-Identifier", "schemaVersion", "kind", "matrixRelease",
                "candidate", "authorization", "systems", "recovery", "rows", "executionReady"}
    if set(value) != required or value.get("SPDX-License-Identifier") != "MIT" or value.get("schemaVersion") != 1 or value.get("kind") != "gate-d-representative-system-execution-instance":
        raise ValueError("invalid execution-instance identity")
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
    auth_fields = {"approved", "administrator", "connection", "serviceChanges", "packagePrerequisites",
                   "dkms", "moduleAdministration", "overlayAdministration", "kernelSwitching",
                   "reboot", "failureInjection", "cleanup", "prohibitions"}
    if not isinstance(authorization, dict) or set(authorization) != auth_fields or authorization["approved"] is not True:
        raise ValueError("authorization fields are incomplete or unapproved")
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
        if row["status"] != "ready" and not row["blockers"]:
            raise ValueError(f"blocked row lacks blockers: {row['id']}")
        if row["status"] != "ready":
            blocked.append(row["id"])
    expected_ready = candidate["status"] == "frozen" and not blocked
    if value["executionReady"] is not expected_ready:
        raise ValueError("executionReady disagrees with candidate and rows")
    if require_ready and not expected_ready:
        raise ValueError("execution instance is blocked-input-required")
    return {"valid": True, "executionReady": expected_ready, "blockedRows": blocked, "readOnly": True}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("instance", type=pathlib.Path)
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    print(json.dumps(validate(load(args.instance), require_ready=args.require_ready), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
