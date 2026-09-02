#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Fail-closed Gate D output-disabled lifecycle coordinator.

Planning and validation are offline and read-only.  Execution requires root,
``--execute``, a fully ready execution instance, and an operation document that
binds exact versions, kernels, routes, evidence, deadlines, and safety state.
The coordinator never enables output, edits boot configuration, enrolls keys,
or selects a fallback backend.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import pathlib
import re
import subprocess
import shutil
import sys
import time
from datetime import datetime, timezone
from typing import Callable

PACKAGE = "rp1-gpclk-dkms"
MODULE = "rp1_gpclk_dkms"
ROUTES = {"gpio4", "gpio20"}
OPERATIONS = {
    "output-disabled-cycle", "upgrade", "downgrade", "rollback", "recover",
    "uninstall-version", "remove-all-test-versions", "complete-removal",
    "repeated-removal", "reinstall-after-removal", "refuse-removal",
    "qualification-transition",
}
CHECKPOINTS = (
    "preflight", "retain-predecessor", "dkms-add", "dkms-build", "dkms-install",
    "load-disabled", "query-disabled", "uapi-query-release", "unbind-bind", "unload", "dkms-uninstall", "dkms-remove",
    "owned-residue-remove", "verify-final-state", "commit-state",
)
VERSION = re.compile(r"[0-9A-Za-z][0-9A-Za-z.+_-]*")
SHA256 = re.compile(r"[0-9a-f]{64}")
SAFE_RELATIVE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._+/-]*")
INSTANCE_VALIDATOR_OVERRIDE = None  # offline unit-test dependency injection only


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: pathlib.Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"not a real JSON file: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("JSON document must be an object")
    return value


def atomic_json(path: pathlib.Path, value: dict) -> None:
    path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(temporary, flags, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            json.dump(value, output, indent=2, sort_keys=True)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _version(value: object, label: str) -> str:
    if not isinstance(value, str) or not VERSION.fullmatch(value):
        raise ValueError(f"invalid {label}")
    return value


def validate_safety(value: object, *, removal_refusal: bool = False) -> dict:
    required_false = {
        "outputActive", "clockEnabled", "clockPrepared", "dmaActive", "gpioOutput",
        "transmitterActive", "sdrActive", "antennaConnected", "moduleLoaded",
        "platformBound", "endpointOpen", "ownerPresent", "workActive",
        "callbackPending", "cleanupLatched",
    }
    required_true = {
        "si5351Disconnected", "ownershipKnown", "routeSelectedInactive", "selectedPinSafe",
        "unselectedPinSafe", "unrelatedBytesPreserved",
    }
    if not isinstance(value, dict) or set(value) != required_false | required_true:
        raise ValueError("safety snapshot fields are incomplete or unknown")
    if any(type(value[field]) is not bool for field in value):
        raise ValueError("safety snapshot values must be booleans")
    blockers = {"moduleLoaded", "platformBound", "endpointOpen", "ownerPresent",
                "workActive", "callbackPending"}
    failed = [field for field in required_false if value[field] and
              not (removal_refusal and field in blockers)]
    failed += [field for field in required_true if not value[field]]
    if failed:
        raise ValueError("unsafe lifecycle precondition: " + ",".join(sorted(failed)))
    if removal_refusal and not any(value[field] for field in blockers):
        raise ValueError("removal refusal requires an exact open or active blocker")
    return value


def validate_operation(value: dict) -> dict:
    required = {
        "schemaVersion", "operationId", "operation", "matrixRow", "hostId",
        "kernelRelease", "route", "deadlineSeconds", "evidenceDirectory",
        "predecessorVersion", "successorVersion", "testVersions", "ownedPaths",
        "safety", "expectedFinalState", "rollbackOnFailure", "priorOperationId",
    }
    if set(value) != required or value.get("schemaVersion") != 1:
        raise ValueError("operation fields are incomplete or unknown")
    if value["operation"] not in OPERATIONS:
        raise ValueError("unsupported lifecycle operation")
    for field in ("operationId", "matrixRow", "hostId", "kernelRelease"):
        if not isinstance(value[field], str) or not value[field]:
            raise ValueError(f"invalid {field}")
    if value["route"] not in ROUTES:
        raise ValueError("route is not allowlisted")
    if not isinstance(value["deadlineSeconds"], int) or isinstance(value["deadlineSeconds"], bool) or not 1 <= value["deadlineSeconds"] <= 1800:
        raise ValueError("deadline must be 1..1800 seconds")
    evidence = value["evidenceDirectory"]
    if not isinstance(evidence, str) or not SAFE_RELATIVE.fullmatch(evidence) or ".." in pathlib.PurePosixPath(evidence).parts:
        raise ValueError("unsafe evidence directory")
    predecessor = value["predecessorVersion"]
    successor = value["successorVersion"]
    if predecessor is not None:
        _version(predecessor, "predecessor version")
    if successor is not None:
        _version(successor, "successor version")
    versions = value["testVersions"]
    if not isinstance(versions, list) or len(versions) != len(set(versions)):
        raise ValueError("test versions must be a unique list")
    for version in versions:
        _version(version, "test version")
    paths = value["ownedPaths"]
    if not isinstance(paths, list):
        raise ValueError("owned paths must be a list")
    seen = set()
    for item in paths:
        if not isinstance(item, dict) or set(item) != {"path", "sha256", "kind"}:
            raise ValueError("owned path record is incomplete")
        path = item["path"]
        if not isinstance(path, str) or not path.startswith("/") or ".." in pathlib.PurePosixPath(path).parts or path in seen:
            raise ValueError("unsafe or duplicate owned path")
        if item["kind"] not in {"file", "symlink", "empty-directory"}:
            raise ValueError("unknown owned path kind")
        if item["kind"] == "empty-directory":
            if item["sha256"] is not None:
                raise ValueError("directory must not have a digest")
        elif not isinstance(item["sha256"], str) or not SHA256.fullmatch(item["sha256"]):
            raise ValueError("owned file digest is invalid")
        seen.add(path)
    validate_safety(value["safety"], removal_refusal=value["operation"] == "refuse-removal")
    if type(value["rollbackOnFailure"]) is not bool:
        raise ValueError("rollbackOnFailure must be boolean")
    if value["priorOperationId"] is not None and (not isinstance(value["priorOperationId"], str) or not value["priorOperationId"]):
        raise ValueError("invalid prior operation identity")
    if value["expectedFinalState"] not in {"predecessor-inactive", "successor-inactive", "package-absent", "installation-retained"}:
        raise ValueError("unknown expected final state")
    expected_by_operation = {
        "output-disabled-cycle": "successor-inactive", "upgrade": "successor-inactive",
        "downgrade": "successor-inactive", "rollback": "predecessor-inactive",
        "recover": "predecessor-inactive", "uninstall-version": "package-absent",
        "remove-all-test-versions": "package-absent", "complete-removal": "package-absent",
        "repeated-removal": "package-absent", "reinstall-after-removal": "package-absent",
        "refuse-removal": "installation-retained",
        "qualification-transition": "predecessor-inactive",
    }
    if value["expectedFinalState"] != expected_by_operation[value["operation"]]:
        raise ValueError("expected final state differs from lifecycle operation")
    if value["operation"] in {"upgrade", "downgrade", "rollback", "recover", "qualification-transition"}:
        if predecessor is None or successor is None or predecessor == successor:
            raise ValueError("transition requires distinct predecessor and successor")
    if value["operation"] == "recover":
        if value["priorOperationId"] is None:
            raise ValueError("recovery requires the failed operation identity")
    elif value["priorOperationId"] is not None:
        raise ValueError("only recovery may name a prior operation")
    if value["operation"] in {"upgrade", "downgrade"}:
        if value["rollbackOnFailure"] is not True:
            raise ValueError("upgrade and downgrade require automatic rollback on ordinary failure")
    elif value["rollbackOnFailure"]:
        raise ValueError("rollbackOnFailure is valid only for upgrade or downgrade")
    if value["operation"] == "output-disabled-cycle" and successor is None:
        raise ValueError("output-disabled cycle requires the exact installed candidate")
    if value["operation"] in {"uninstall-version", "remove-all-test-versions", "complete-removal", "repeated-removal", "reinstall-after-removal", "refuse-removal"} and not versions:
        raise ValueError("removal operation requires exact test versions")
    if value["operation"] == "refuse-removal" and not paths:
        raise ValueError("removal refusal requires an exact retained installation identity")
    return value


def bind_instance(spec: dict, instance: dict, *, validator=None) -> dict:
    scripts = pathlib.Path(__file__).resolve().parent
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    from gate_d_instance import validate as validate_instance

    (validator or INSTANCE_VALIDATOR_OVERRIDE or validate_instance)(instance, require_ready=True)
    rows = {row["id"]: row for row in instance["rows"]}
    row = rows.get(spec["matrixRow"])
    if row is None or row["status"] != "ready":
        raise ValueError("operation row is not ready")
    if spec["hostId"] != row["systemId"] or spec["kernelRelease"] != row["kernel"]:
        raise ValueError("operation target identity differs from execution instance")
    if "route-neutral" not in row["routes"] and spec["route"] not in row["routes"]:
        raise ValueError("operation route differs from execution instance")
    if spec["deadlineSeconds"] > row["deadlineSeconds"]:
        raise ValueError("operation deadline exceeds authorized row deadline")
    base = pathlib.PurePosixPath(row["evidenceDirectory"])
    evidence = pathlib.PurePosixPath(spec["evidenceDirectory"])
    if evidence.parent != base:
        raise ValueError("operation must use one new attempt directory below the row evidence directory")
    release = instance["candidate"]["release"]
    if spec["successorVersion"] is not None and spec["successorVersion"] != release:
        raise ValueError("operation successor differs from frozen candidate")
    return row


def command_runner(command: list[str], deadline: int) -> str:
    result = subprocess.run(command, stdin=subprocess.DEVNULL, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            timeout=deadline, check=True,
                            env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin"})
    return result.stdout


def dispatch_primitive(arguments: list[str], *, runner=command_runner,
                       root: pathlib.Path = pathlib.Path("/"), administrator_uid: int | None = None) -> dict:
    """Execute one outer-executor primitive; never accepts an arbitrary argv."""
    uid = os.geteuid() if administrator_uid is None else administrator_uid
    if not arguments or arguments[-1] != "--execute" or uid != 0:
        raise PermissionError("primitive dispatch requires root and --execute")
    values = arguments[:-1]
    operation = values[0]
    if operation not in {"stage", "dkms-install", "expect-build-failure", "recover",
                         "dkms-remove", "complete-removal"}:
        raise ValueError("unknown lifecycle primitive")
    expected_counts = {"stage": 3, "dkms-install": 4, "expect-build-failure": 4,
                       "recover": 5, "dkms-remove": 4, "complete-removal": 5}
    if len(values) != expected_counts[operation]:
        raise ValueError("lifecycle primitive arguments are incomplete")
    versions = ([values[1]] if operation in {"stage", "dkms-install", "expect-build-failure", "dkms-remove"}
                else values[1:3])
    if not versions or any(not VERSION.fullmatch(value) for value in versions):
        raise ValueError("invalid primitive version")
    staging = pathlib.Path(values[-1])
    if not staging.is_absolute() or ".." in staging.parts:
        raise ValueError("unsafe primitive staging directory")
    commands: list[list[str]] = []

    def staged_source(version: str) -> pathlib.Path:
        matches = []
        for label in ("candidate", "predecessor"):
            base = _rooted(root, str(staging / label))
            roots = list(base.iterdir()) if base.is_dir() and not base.is_symlink() else []
            if len(roots) == 1 and roots[0].name == f"{PACKAGE}-{version}":
                matches.append(roots[0])
        if len(matches) != 1 or matches[0].is_symlink() or not matches[0].is_dir():
            raise ValueError("staged versioned archive root differs")
        return matches[0]

    def ensure_source(version: str) -> None:
        destination = _rooted(root, f"/usr/src/{PACKAGE}-{version}")
        source = staged_source(version)
        if destination.exists() or destination.is_symlink():
            if destination.is_symlink() or not destination.is_dir():
                raise ValueError("DKMS source destination is unsafe")
            return
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, destination, symlinks=False)

    if operation == "stage":
        ensure_source(values[1])
    elif operation == "dkms-install":
        version, kernel = values[1], values[2]
        ensure_source(version)
        commands = [dkms("add", version, kernel), dkms("build", version, kernel),
                    dkms("install", version, kernel)]
    elif operation == "expect-build-failure":
        version, kernel = values[1], values[2]
        ensure_source(version)
        wrapper = _rooted(root, str(staging / "compiler-failure"))
        if wrapper.is_symlink() or not wrapper.is_file():
            raise ValueError("compiler failure wrapper is absent")
        command = dkms("build", version, kernel)
        result = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, timeout=1800,
                                env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin", "LANG": "C",
                                     "LC_ALL": "C", "CC": str(wrapper)}, check=False)
        if result.returncode == 0:
            raise ValueError("deliberate DKMS build unexpectedly succeeded")
        raise SystemExit(1)
    elif operation == "recover":
        predecessor, successor, kernel = values[1], values[2], values[3]
        ensure_source(predecessor)
        commands = [dkms("uninstall", successor, kernel), dkms("remove", successor, kernel),
                    dkms("install", predecessor, kernel)]
    elif operation == "dkms-remove":
        version, kernel = values[1], values[2]
        commands = [dkms("uninstall", version, kernel), dkms("remove", version, kernel)]
    else:
        predecessor, successor, kernel = values[1], values[2], values[3]
        commands = [dkms("uninstall", successor, kernel), dkms("remove", successor, kernel),
                    dkms("uninstall", predecessor, kernel), dkms("remove", predecessor, kernel)]
    outputs = []
    for command in commands:
        try:
            output = runner(command, 1800)
        except subprocess.CalledProcessError as error:
            if command[:2] not in (["dkms", "uninstall"], ["dkms", "remove"]):
                raise
            version = command[command.index("-v") + 1]
            status_command = ["dkms", "status", "-m", PACKAGE, "-v", version]
            if command[1] == "uninstall":
                kernel = command[command.index("-k") + 1]
                status_command += ["-k", kernel]
            status = runner(status_command, 1800)
            outputs.append({"argv": command, "output": (error.stdout or error.output or "")[:65536],
                            "status": error.returncode})
            outputs.append({"argv": status_command, "output": status[:65536], "status": 0})
            if status.strip():
                raise ValueError("DKMS removal failed and the exact scope remains present")
            continue
        outputs.append({"argv": command, "output": output[:65536], "status": 0})
    return {"operation": operation, "commands": outputs, "outputActive": False}


def dkms(action: str, version: str, kernel: str) -> list[str]:
    command = ["dkms", action, "-m", PACKAGE, "-v", version]
    if action in {"build", "install", "uninstall"}:
        command += ["-k", kernel]
    if action == "remove":
        command += ["--all"]
    return command


def operation_commands(spec: dict) -> list[tuple[str, list[str]]]:
    operation = spec["operation"]
    kernel = spec["kernelRelease"]
    predecessor = spec["predecessorVersion"]
    successor = spec["successorVersion"]
    commands: list[tuple[str, list[str]]] = []
    install_sequence = lambda version: [
        ("dkms-add", dkms("add", version, kernel)),
        ("dkms-build", dkms("build", version, kernel)),
        ("dkms-install", dkms("install", version, kernel)),
        ("load-disabled", ["modprobe", MODULE, "output_inhibit=1"]),
        ("query-disabled", ["cat", f"/sys/module/{MODULE}/parameters/output_inhibit"]),
        ("uapi-query-release", ["/usr/libexec/rp1-gpclk-dkms/gate-d-uapi-probe",
                                spec["route"], version]),
        ("unbind-bind", ["/usr/libexec/rp1-gpclk-dkms/gate-d-platform",
                         "unbind-bind-cycle", "--execute"]),
        ("uapi-query-release", ["/usr/libexec/rp1-gpclk-dkms/gate-d-uapi-probe",
                                spec["route"], version]),
        ("unload", ["modprobe", "-r", MODULE]),
    ]
    remove_sequence = lambda version: [
        ("dkms-uninstall", dkms("uninstall", version, kernel)),
        ("dkms-remove", dkms("remove", version, kernel)),
    ]
    if operation == "output-disabled-cycle":
        commands += install_sequence(successor)[3:] if successor else [
            ("load-disabled", ["modprobe", MODULE, "output_inhibit=1"]),
            ("query-disabled", ["cat", f"/sys/module/{MODULE}/parameters/output_inhibit"]),
            ("uapi-query-release", ["/usr/libexec/rp1-gpclk-dkms/gate-d-uapi-probe",
                                    spec["route"], successor or "installed"]),
            ("unbind-bind", ["/usr/libexec/rp1-gpclk-dkms/gate-d-platform",
                             "unbind-bind-cycle", "--execute"]),
            ("unload", ["modprobe", "-r", MODULE]),
        ]
    elif operation in {"upgrade", "downgrade"}:
        commands += install_sequence(successor)
    elif operation in {"rollback", "recover"}:
        commands += remove_sequence(successor)
        commands += [("dkms-install", dkms("install", predecessor, kernel)),
                     ("load-disabled", ["modprobe", MODULE, "output_inhibit=1"]),
                     ("query-disabled", ["cat", f"/sys/module/{MODULE}/parameters/output_inhibit"]),
                     ("uapi-query-release", ["/usr/libexec/rp1-gpclk-dkms/gate-d-uapi-probe",
                                             spec["route"], predecessor]),
                     ("unbind-bind", ["/usr/libexec/rp1-gpclk-dkms/gate-d-platform",
                                      "unbind-bind-cycle", "--execute"]),
                     ("uapi-query-release", ["/usr/libexec/rp1-gpclk-dkms/gate-d-uapi-probe",
                                             spec["route"], predecessor]),
                     ("unload", ["modprobe", "-r", MODULE])]
    elif operation == "uninstall-version":
        commands += remove_sequence(spec["testVersions"][0])
    elif operation in {"remove-all-test-versions", "complete-removal", "repeated-removal"}:
        for version in spec["testVersions"]:
            commands += remove_sequence(version)
    elif operation == "reinstall-after-removal":
        version = spec["testVersions"][0]
        commands += install_sequence(version) + remove_sequence(version)
    elif operation == "qualification-transition":
        commands += [
            ("dkms-add", dkms("add", successor, kernel)),
            ("dkms-build", dkms("build", successor, kernel)),
            ("dkms-install", dkms("install", successor, kernel)),
            ("load-disabled", ["modprobe", MODULE, "output_inhibit=1"]),
            ("query-disabled", ["cat", f"/sys/module/{MODULE}/parameters/output_inhibit"]),
            ("uapi-query-release", ["/usr/libexec/rp1-gpclk-dkms/gate-d-uapi-probe",
                                    spec["route"], successor]),
            ("unbind-bind", ["/usr/libexec/rp1-gpclk-dkms/gate-d-platform",
                             "unbind-bind-cycle", "--execute"]),
            ("unload", ["modprobe", "-r", MODULE]),
            ("dkms-uninstall", dkms("uninstall", successor, kernel)),
            ("dkms-remove", dkms("remove", successor, kernel)),
        ]
    return commands


def _rooted(root: pathlib.Path, absolute: str) -> pathlib.Path:
    if not absolute.startswith("/") or ".." in pathlib.PurePosixPath(absolute).parts:
        raise ValueError("unsafe owned path")
    path = root / absolute.lstrip("/")
    current = root
    for part in pathlib.PurePosixPath(absolute).parts[1:]:
        current /= part
        if current.is_symlink() and current != path:
            raise ValueError(f"symlink parent in owned path: {absolute}")
    return path


def remove_owned_paths(spec: dict, root: pathlib.Path) -> None:
    for item in reversed(spec["ownedPaths"]):
        path = _rooted(root, item["path"])
        if item["kind"] == "empty-directory":
            if path.exists():
                if path.is_symlink() or not path.is_dir():
                    raise ValueError(f"owned directory identity changed: {item['path']}")
                path.rmdir()
        elif item["kind"] == "symlink":
            if path.is_symlink():
                if hashlib.sha256(os.readlink(path).encode()).hexdigest() != item["sha256"]:
                    raise ValueError(f"owned symlink changed: {item['path']}")
                path.unlink()
            elif path.exists():
                raise ValueError(f"owned symlink replaced: {item['path']}")
        elif path.exists() or path.is_symlink():
            if path.is_symlink() or not path.is_file() or digest(path) != item["sha256"]:
                raise ValueError(f"owned file changed: {item['path']}")
            path.unlink()


def verify_final_state(spec: dict, root: pathlib.Path,
                       runner: Callable[[list[str], int], str]) -> None:
    operation = spec["operation"]
    removal = {"uninstall-version", "remove-all-test-versions", "complete-removal",
               "repeated-removal", "reinstall-after-removal"}
    if operation in removal:
        for version in spec["testVersions"]:
            if runner(["dkms", "status", "-m", PACKAGE, "-v", version],
                      spec["deadlineSeconds"]).strip():
                raise ValueError(f"test DKMS version remains installed: {version}")
    if operation == "qualification-transition":
        successor = spec["successorVersion"]
        predecessor = spec["predecessorVersion"]
        if runner(["dkms", "status", "-m", PACKAGE, "-v", successor],
                  spec["deadlineSeconds"]).strip():
            raise ValueError("transition successor remains present")
        if not runner(["dkms", "status", "-m", PACKAGE, "-v", predecessor],
                      spec["deadlineSeconds"]).strip():
            raise ValueError("retained predecessor is absent")
    module = root / f"sys/module/{MODULE}"
    endpoint = root / "dev/rp1-gpclk"
    if operation != "refuse-removal" and (module.exists() or module.is_symlink() or
                                           endpoint.exists() or endpoint.is_symlink()):
        raise ValueError("runtime residue remains after inactive final state")
    if operation in removal:
        driver = root / "sys/bus/platform/drivers/rp1-gpclk-dkms"
        if driver.is_dir() and any(item.is_symlink() for item in driver.iterdir()):
            raise ValueError("bound platform device remains after removal")
    if operation == "refuse-removal":
        for item in spec["ownedPaths"]:
            path = _rooted(root, item["path"])
            if item["kind"] == "file":
                retained = path.is_file() and not path.is_symlink() and digest(path) == item["sha256"]
            elif item["kind"] == "symlink":
                retained = path.is_symlink() and hashlib.sha256(os.readlink(path).encode()).hexdigest() == item["sha256"]
            else:
                retained = path.is_dir() and not path.is_symlink() and not any(path.iterdir())
            if not retained:
                raise ValueError("refused removal did not retain exact owned path")


def execute(spec: dict, instance: dict, journal: pathlib.Path, *, root: pathlib.Path = pathlib.Path("/"),
            runner: Callable[[list[str], int], str] = command_runner,
            stop_after: str | None = None,
            recover_from: pathlib.Path | None = None, instance_validator=None) -> dict:
    validate_operation(spec)
    bind_instance(spec, instance, validator=instance_validator)
    if stop_after is not None and stop_after not in CHECKPOINTS:
        raise ValueError("unknown interruption checkpoint")
    if journal.exists() or journal.is_symlink():
        raise ValueError("journal already exists; evidence directories are immutable")
    prior = None
    if spec["operation"] == "recover":
        if recover_from is None:
            raise ValueError("recovery requires an immutable failed journal")
        prior = load_json(recover_from)
        if (prior.get("status") != "inactive-recovery-required" or
                prior.get("outputActive") is not False or
                prior.get("operationId") != spec["priorOperationId"]):
            raise ValueError("recovery requires the matching inactive failed journal")
    elif recover_from is not None:
        raise ValueError("only recovery may name a failed journal")
    state = {"schemaVersion": 1, "operationId": spec["operationId"],
             "operation": spec["operation"], "status": "inactive-in-progress",
             "outputActive": False, "checkpoint": "preflight", "commands": [],
             "recoveryRequired": True,
             "startedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}
    operation_started_ns = time.monotonic_ns()
    if prior is not None:
        state["recovers"] = {"operationId": prior.get("operationId"),
                             "operation": prior.get("operation"),
                             "checkpoint": prior.get("checkpoint"),
                             "failure": prior.get("failure")}
    atomic_json(journal, state)

    def run(command: list[str], checkpoint: str) -> str:
        elapsed = (time.monotonic_ns() - operation_started_ns) / 1_000_000_000
        remaining = math.ceil(spec["deadlineSeconds"] - elapsed)
        if remaining <= 0:
            raise TimeoutError("operation deadline exhausted before command dispatch")
        record = {"command": command, "checkpoint": checkpoint,
                  "deadlineSeconds": remaining, "status": "pending",
                  "startUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                  "startMonotonicNs": time.monotonic_ns()}
        state["commands"].append(record)
        atomic_json(journal, state)
        try:
            output = runner(command, remaining)
        except subprocess.CalledProcessError as error:
            record["status"] = error.returncode
            output = error.stdout or error.output or ""
            record["stdout"] = output[:65536]
            record["stdoutTruncated"] = len(output) > 65536
            record["endUtc"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            record["endMonotonicNs"] = time.monotonic_ns()
            atomic_json(journal, state)
            raise
        record["status"] = 0
        record["stdout"] = output[:65536]
        record["stdoutTruncated"] = len(output) > 65536
        record["endUtc"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        record["endMonotonicNs"] = time.monotonic_ns()
        atomic_json(journal, state)
        return output

    def rollback_after_failure() -> None:
        successor = spec["successorVersion"]
        predecessor = spec["predecessorVersion"]
        rollback = operation_commands({**spec, "operation": "rollback"})
        state["rollback"] = {"status": "in-progress", "from": successor, "to": predecessor}
        atomic_json(journal, state)
        for checkpoint, command in rollback:
            state["checkpoint"] = f"rollback-{checkpoint}"
            try:
                run(command, state["checkpoint"])
            except subprocess.CalledProcessError:
                if command[:2] not in (["dkms", "uninstall"], ["dkms", "remove"]):
                    raise
                version = command[command.index("-v") + 1]
                if run(["dkms", "status", "-m", PACKAGE, "-v", version],
                       "rollback-verify-absent").strip():
                    raise
        state["rollback"]["status"] = "complete"
        state.update({"status": "inactive-rolled-back", "recoveryRequired": False,
                      "finalState": "predecessor-inactive"})
        atomic_json(journal, state)
    try:
        if stop_after == "preflight":
            raise InterruptedError("preflight")
        if spec["operation"] in {"upgrade", "downgrade", "qualification-transition"}:
            state["checkpoint"] = "retain-predecessor"
            atomic_json(journal, state)
            if stop_after == "retain-predecessor":
                raise InterruptedError("retain-predecessor")
        for checkpoint, command in operation_commands(spec):
            state["checkpoint"] = checkpoint
            atomic_json(journal, state)
            try:
                output = run(command, checkpoint)
            except subprocess.CalledProcessError:
                if (spec["operation"] == "recover" and command[:2] == ["dkms", "install"]):
                    version = command[command.index("-v") + 1]
                    status = run(["dkms", "status", "-m", PACKAGE, "-v", version],
                                 "verify-predecessor-after-install-error")
                    if status.strip():
                        output = "already installed"
                        continue
                if (spec["operation"] not in {"recover", "repeated-removal"} or
                        len(command) < 2 or command[0] != "dkms" or
                        command[1] not in {"uninstall", "remove"}):
                    raise
                version = command[command.index("-v") + 1]
                status = run(["dkms", "status", "-m", PACKAGE, "-v", version],
                             "verify-absent-after-removal-error")
                if status.strip():
                    raise ValueError("DKMS removal failed and exact version remains")
                output = "already absent"
            if checkpoint == "query-disabled" and output.strip() not in {"Y", "1", "true", "True"}:
                raise ValueError("immutable output-disabled gate verification failed")
            if checkpoint == "uapi-query-release" and "output_inhibit_supported=1 released=1" not in output:
                raise ValueError("output-disabled UAPI query/acquire/release verification failed")
            if checkpoint == "unbind-bind" and '"unbindBind": true' not in output and "unbind_bind=1" not in output:
                raise ValueError("output-disabled unbind/rebind verification failed")
            if stop_after == checkpoint:
                raise InterruptedError(checkpoint)
        if spec["operation"] in {"complete-removal", "repeated-removal", "reinstall-after-removal", "qualification-transition"}:
            state["checkpoint"] = "owned-residue-remove"
            atomic_json(journal, state)
            remove_owned_paths(spec, root)
            if stop_after == "owned-residue-remove":
                raise InterruptedError("owned-residue-remove")
        state["checkpoint"] = "verify-final-state"
        atomic_json(journal, state)
        validate_safety(spec["safety"], removal_refusal=spec["operation"] == "refuse-removal")
        verify_final_state(spec, root,
                           lambda command, deadline: run(command, "verify-final-state"))
        if stop_after == "verify-final-state":
            raise InterruptedError("verify-final-state")
        state["checkpoint"] = "commit-state"
        atomic_json(journal, state)
        if stop_after == "commit-state":
            raise InterruptedError("commit-state")
        state.update({"status": "complete", "checkpoint": "commit-state",
                      "recoveryRequired": False,
                      "completedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")})
        atomic_json(journal, state)
        return state
    except InterruptedError as error:
        state.update({"status": "inactive-recovery-required", "recoveryRequired": True,
                      "failure": type(error).__name__})
        atomic_json(journal, state)
        raise
    except BaseException as error:
        state["failure"] = type(error).__name__
        if spec["rollbackOnFailure"]:
            try:
                rollback_after_failure()
            except BaseException as rollback_error:
                state.update({"status": "inactive-recovery-required", "recoveryRequired": True,
                              "rollbackFailure": type(rollback_error).__name__})
                atomic_json(journal, state)
            raise
        state.update({"status": "inactive-recovery-required", "recoveryRequired": True})
        atomic_json(journal, state)
        raise


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "dispatch":
        print(json.dumps(dispatch_primitive(sys.argv[2:]), indent=2, sort_keys=True))
        return
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("validate", "plan", "execute"))
    parser.add_argument("operation", type=pathlib.Path)
    parser.add_argument("--instance", type=pathlib.Path)
    parser.add_argument("--journal", type=pathlib.Path)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--stop-after", choices=CHECKPOINTS)
    parser.add_argument("--recover-from", type=pathlib.Path)
    args = parser.parse_args()
    spec = validate_operation(load_json(args.operation))
    if args.action == "validate":
        result = {"valid": True, "operationId": spec["operationId"], "readOnly": True}
    elif args.action == "plan":
        result = {"operationId": spec["operationId"], "commands": operation_commands(spec),
                  "outputActive": False, "readOnly": True}
    else:
        if not args.execute or os.geteuid() != 0 or args.journal is None or args.instance is None:
            raise SystemExit("execution requires root, --execute, --instance, and --journal")
        result = execute(spec, load_json(args.instance), args.journal, stop_after=args.stop_after,
                         recover_from=args.recover_from)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
