#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate and render the complete output-disabled Gate D target plan."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re

ROWS = (
    "current-supported-kernel", "prior-supported-kernel-downgrade",
    "signing-not-enforced", "deliberate-build-failure", "interrupted-upgrade",
    "stale-manifest", "corrupted-archive-or-dtbo", "removal-inactive",
    "removal-open-or-active", "reinstall-after-removal",
)
SHA = re.compile(r"[0-9a-f]{64}")
PROHIBITED = ("output_inhibit=0", "/dev/mem", "rpi-update", "force-remove",
              "clock-enable", "dma-submit", "gpio-output", "sdr-operation", "rf")
REQUIRED_ACTIONS = {
    "current-supported-kernel": {"apply-route-runtime-output-disabled", "query-release", "complete-test-owned-removal"},
    "prior-supported-kernel-downgrade": {"select-prior-stock-kernel", "restore-normal-boot-selection", "noticed-reboot-to-prior", "noticed-reboot-to-normal"},
    "signing-not-enforced": {"verify-signing-not-enforced", "verify-signing-policy-unchanged"},
    "deliberate-build-failure": {"inject-compiler-exit-nonzero", "expect-dkms-build-failure", "recover-predecessor"},
    "interrupted-upgrade": {"interrupt-after-durable-checkpoint", "write-immutable-failed-journal", "recover-in-new-attempt"},
    "stale-manifest": {"inject-one-stale-identity", "expect-rejection-before-load"},
    "corrupted-archive-or-dtbo": {"flip-one-byte", "expect-hash-rejection-before-install"},
    "removal-inactive": {"inventory-exact-owned-paths", "verify-package-runtime-overlay-and-residue-absent"},
    "removal-open-or-active": {"start-busy-injector-and-wait-ready", "expect-removal-refusal-without-mutation", "stop-injector-and-verify-release-close"},
    "reinstall-after-removal": {"prove-empty-package-baseline", "verify-second-empty-baseline"},
}
CHECKPOINT_ATTEMPTS = {
    "after-preflight", "after-retain-predecessor", "after-dkms-add", "after-dkms-build",
    "after-dkms-install", "after-load-disabled", "after-query-disabled",
    "after-uapi-query-release", "after-unbind-bind", "after-unload",
    "after-dkms-uninstall", "after-dkms-remove", "after-owned-residue-remove",
    "after-verify-final-state", "after-commit-state",
}
EXPECTED_ENVELOPE = (
    "new-evidence-directory", "capture-live-preflight", "verify-artifacts",
    "snapshot-services", "quiesce-exact-services", "stage-test-owned-source",
    "execute-row-actions", "restore-exact-services", "audit-owned-residue",
    "capture-scoped-kernel-log-delta", "seal-evidence-read-only",
)
ROOT = pathlib.Path(__file__).resolve().parents[1]


def load(path: pathlib.Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError("target plan must be a real file")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("target plan must be an object")
    return value


def validate(value: dict, *, verify_tools: bool = True) -> dict:
    required = {"SPDX-License-Identifier", "schemaVersion", "kind", "hostId", "tooling", "invariants",
                "services", "artifacts", "boot", "attemptEnvelope", "rows"}
    schema = value.get("schemaVersion")
    if schema in {3,4,5}: required.add("qualificationBootstrap")
    if schema in {4,5}: required.add("qualificationRoot")
    if schema == 5: required.add("pythonModules")
    if set(value) != required or value.get("SPDX-License-Identifier") != "MIT" or schema not in {1, 2, 3, 4, 5} or value.get("kind") != "gate-d-output-disabled-target-operation-plan":
        raise ValueError("invalid target-plan identity")
    if schema == 1 and verify_tools:
        raise ValueError("legacy target plan is inspectable but not executable")
    root=ROOT
    if schema in {4,5}:
        scripts=pathlib.Path(__file__).resolve().parent
        if str(scripts) not in __import__("sys").path: __import__("sys").path.insert(0,str(scripts))
        from gate_d_root import validate as validate_root
        root=validate_root(value["qualificationRoot"])
    if schema in {3,4,5}:
        bootstrap=value["qualificationBootstrap"]
        if (not isinstance(bootstrap,dict) or set(bootstrap)!={"path","sha256"} or
                pathlib.PurePosixPath(bootstrap.get("path","")).is_absolute() or
                ".." in pathlib.PurePosixPath(bootstrap.get("path","")).parts or
                not SHA.fullmatch(bootstrap.get("sha256",""))):
            raise ValueError("invalid qualification bootstrap reference")
        path=root/bootstrap["path"]
        if path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=bootstrap["sha256"]:
            raise ValueError("qualification bootstrap identity mismatch")
        scripts = pathlib.Path(__file__).resolve().parent
        if str(scripts) not in __import__("sys").path:
            __import__("sys").path.insert(0, str(scripts))
        from gate_d_bootstrap import validate as validate_bootstrap
        bootstrap_value=json.loads(path.read_text(encoding="utf-8"))
        validate_bootstrap(bootstrap_value)
        if schema in {4,5} and bootstrap_value.get("qualificationRoot")!=value["qualificationRoot"]:
            raise ValueError("target plan and bootstrap qualification roots differ")
    invariants = value["invariants"]
    expected_invariants = {"outputActive": False, "si5351Disconnected": True,
                           "antennaConnected": False, "sdrPermitted": False,
                           "forcedRemoval": False, "trybootMutation": False,
                           "historicalArtifactMutation": False}
    if invariants != expected_invariants:
        raise ValueError("target safety invariants differ")
    tooling = value["tooling"]
    required_tools = {"bootSelector", "targetPlanValidator", "instanceValidator",
                      "lifecycleCoordinator", "platformCoordinator",
                      "permanentExecutor", "busyInjector", "uapiProbe"}
    if schema in {3,4,5}:
        required_tools.add("bootstrapExecutor")
    if schema in {4,5}:
        required_tools.add("rootValidator")
    if not isinstance(tooling, dict) or set(tooling) != required_tools:
        raise ValueError("execution tooling identities are incomplete")
    for name, item in tooling.items():
        keys = ({"sourcePath", "installedPath", "sha256", "candidateArchiveMember"} if schema == 1 else
                {"sourcePath", "installedPath", "sourceSha256", "installedSha256", "installKind", "candidateArchiveMember"})
        if (not isinstance(item, dict) or set(item) != keys or
                not isinstance(item["sourcePath"], str) or pathlib.PurePosixPath(item["sourcePath"]).is_absolute() or
                ".." in pathlib.PurePosixPath(item["sourcePath"]).parts or
                not isinstance(item["installedPath"], str) or not pathlib.PurePosixPath(item["installedPath"]).is_absolute() or
                ".." in pathlib.PurePosixPath(item["installedPath"]).parts or
                type(item["candidateArchiveMember"]) is not bool):
            raise ValueError(f"invalid execution tool identity: {name}")
        source_sha = item.get("sha256") if schema == 1 else item.get("sourceSha256")
        if not isinstance(source_sha, str) or not SHA.fullmatch(source_sha):
            raise ValueError(f"invalid execution tool source identity: {name}")
        if schema in {2, 3, 4, 5}:
            if item.get("installKind") not in {"copied", "target-built"} or not isinstance(item.get("installedSha256"), str) or not SHA.fullmatch(item["installedSha256"]):
                raise ValueError(f"invalid installed execution tool identity: {name}")
            if item["installKind"] == "copied" and item["installedSha256"] != source_sha:
                raise ValueError(f"copied execution tool identities differ: {name}")
            expected_kind = "target-built" if item["sourcePath"].endswith(".c") else "copied"
            if item["installKind"] != expected_kind:
                raise ValueError(f"execution tool install kind differs: {name}")
        path = root / item["sourcePath"]
        if verify_tools and (path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != source_sha):
            raise ValueError(f"execution tool identity mismatch: {name}")
    if schema in {4,5}:
        retained={item["path"]:item["sha256"] for item in bootstrap_value["retainedTools"]}
        root_tool=tooling["rootValidator"]
        if retained.get(root_tool["installedPath"])!=root_tool["installedSha256"]:
            raise ValueError("bootstrap and target-plan root-validator identities differ")
    if schema==5:
        from gate_d_outer import IMPORT_MODULE_PATHS
        modules=value["pythonModules"]
        if not isinstance(modules,dict) or set(modules)!=set(IMPORT_MODULE_PATHS):
            raise ValueError("installed Python import graph is incomplete")
        keys={"sourcePath","installedPath","sourceSha256","installedSha256","installKind","candidateArchiveMember"}
        for name,installed_path in IMPORT_MODULE_PATHS.items():
            module=modules[name]
            if (not isinstance(module,dict) or set(module)!=keys or
                    module.get("sourcePath")!=f"scripts/{name}.py" or module.get("installedPath")!=installed_path or
                    module.get("sourceSha256")!=module.get("installedSha256") or module.get("installKind")!="copied" or
                    module.get("candidateArchiveMember") is not True or not SHA.fullmatch(module.get("sourceSha256",""))):
                raise ValueError(f"invalid installed Python module identity: {name}")
            path=root/module["sourcePath"]
            if verify_tools and (path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=module["sourceSha256"]):
                raise ValueError(f"installed Python module source differs: {name}")
            if retained.get(installed_path)!=module["installedSha256"]:
                raise ValueError(f"bootstrap retained Python module differs: {name}")
        if modules["gate_d_root"]!=tooling["rootValidator"]:
            raise ValueError("root-validator and import-graph identities differ")
    services = value["services"]
    if not isinstance(services, list) or {item.get("name") for item in services} != {
            "wsprrypi", "sdrplay", "sdrconnect-server", "SoapySDRServer"}:
        raise ValueError("named service transaction is incomplete")
    for item in services:
        if set(item) != {"name", "requiredPreState", "action"} or item["action"] not in {"stop-then-restore-exact", "preserve"}:
            raise ValueError("invalid service transaction")
    artifacts = value["artifacts"]
    if set(artifacts) != {"predecessor", "successor", "gpio4", "gpio20"}:
        raise ValueError("artifact identities are incomplete")
    if artifacts["predecessor"].get("version") == artifacts["successor"].get("version"):
        raise ValueError("predecessor and successor are not distinct")
    for artifact in artifacts.values():
        if not SHA.fullmatch(artifact.get("sha256", "")):
            raise ValueError("artifact digest is invalid")
    boot = value["boot"]
    boot_required = {"normalKernel", "priorKernel", "config", "configSha256", "tryboot",
                     "trybootSha256", "priorKernelSource", "priorKernelSha256",
                     "priorInitramfsSource", "priorInitramfsSha256", "selector",
                     "rebootNoticeRequired", "sshReturnSeconds", "automaticRecoverySeconds",
                     "assistanceSeconds"}
    if set(boot) != boot_required or boot["normalKernel"] == boot["priorKernel"] or boot["rebootNoticeRequired"] is not True:
        raise ValueError("boot switch contract is incomplete")
    for field in ("configSha256", "trybootSha256", "priorKernelSha256", "priorInitramfsSha256"):
        if not SHA.fullmatch(boot[field]):
            raise ValueError("boot artifact digest is invalid")
    if boot["tryboot"] != "/boot/firmware/tryboot.txt" or boot["selector"] != "scripts/gate_d_boot.py":
        raise ValueError("unreviewed boot selector")
    if not (0 < boot["sshReturnSeconds"] <= boot["automaticRecoverySeconds"] <= boot["assistanceSeconds"] <= 1800):
        raise ValueError("boot recovery deadlines differ")
    envelope = value["attemptEnvelope"]
    if not isinstance(envelope, list) or tuple(envelope) != EXPECTED_ENVELOPE:
        raise ValueError("attempt evidence/service envelope is incomplete")
    rows = value["rows"]
    if not isinstance(rows, list) or tuple(row.get("id") for row in rows) != ROWS:
        raise ValueError("required target rows are missing or reordered")
    attempts = 0
    for row in rows:
        if set(row) != {"id", "attempts", "actions"} or not isinstance(row["attempts"], list) or not row["attempts"] or len(row["attempts"]) != len(set(row["attempts"])):
            raise ValueError(f"invalid attempts for {row.get('id')}")
        if not isinstance(row["actions"], list) or len(row["actions"]) != len(set(row["actions"])):
            raise ValueError(f"invalid actions for {row['id']}")
        if not REQUIRED_ACTIONS[row["id"]].issubset(row["actions"]):
            raise ValueError(f"incomplete action coverage for {row['id']}")
        flat = " ".join(row["actions"]).lower()
        if any(token in flat for token in PROHIBITED):
            raise ValueError(f"prohibited action in {row['id']}")
        attempts += len(row["attempts"])
    interrupted = next(row for row in rows if row["id"] == "interrupted-upgrade")
    if set(interrupted["attempts"]) != CHECKPOINT_ATTEMPTS:
        raise ValueError("durable checkpoint attempts are incomplete")
    busy = next(row for row in rows if row["id"] == "removal-open-or-active")
    if set(busy["attempts"]) != {"open-gpio4", "owner-gpio4", "open-gpio20", "owner-gpio20"}:
        raise ValueError("busy-state attempts are incomplete")
    return {"valid": True, "readOnly": True, "rowCount": len(rows), "attemptCount": attempts,
            "outputActive": False}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=pathlib.Path)
    parser.add_argument("--row", choices=ROWS)
    args = parser.parse_args()
    value = load(args.plan)
    result = validate(value)
    if args.row:
        result["row"] = next(row for row in value["rows"] if row["id"] == args.row)
        result["attemptEnvelope"] = value["attemptEnvelope"]
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
