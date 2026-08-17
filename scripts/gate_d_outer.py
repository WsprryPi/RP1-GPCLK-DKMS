#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Permanent fail-closed transaction engine for Gate D qualification.

The engine owns validation, ordering, deadlines, durable journals, bounded
subprocess capture, and immutable evidence.  Qualification documents remain
external data.  Target mutation requires root and ``--execute``; ordinary
planning and the filesystem-backed fake backend are offline and unprivileged.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import pathlib
import re
import stat
import subprocess
import tarfile
import shutil
import sys
import time
import types
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

VERSION = 1
MAX_OUTPUT = 65536
FIXED_ENV = {"PATH": "/usr/sbin:/usr/bin:/sbin:/bin", "LANG": "C", "LC_ALL": "C"}
SAFE_ID = re.compile(r"[a-z0-9][a-z0-9._-]+")
SHA256 = re.compile(r"[0-9a-f]{64}")
PROHIBITED = ("live_output=1", "/dev/mem", "rpi-update", "--force", "force-remove")


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_json(path: pathlib.Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"not a real JSON file: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("JSON document must be an object")
    return value


IMPORT_MODULE_PATHS = {
    "gate_d_root": "/usr/libexec/rp1-gpclk-dkms/gate_d_root.py",
    "gate_d_bootstrap": "/usr/libexec/rp1-gpclk-dkms/gate_d_bootstrap.py",
    "gate_d_target_plan": "/usr/libexec/rp1-gpclk-dkms/gate_d_target_plan.py",
    "gate_d_lifecycle": "/usr/libexec/rp1-gpclk-dkms/gate_d_lifecycle.py",
    "gate_d_outer": "/usr/libexec/rp1-gpclk-dkms/gate_d_outer.py",
    "gate_d_attempts": "/usr/libexec/rp1-gpclk-dkms/gate_d_attempts.py",
    "gate_d_instance": "/usr/libexec/rp1-gpclk-dkms/gate_d_instance.py",
    "gate_d_preroot": "/usr/libexec/rp1-gpclk-dkms/gate_d_preroot.py",
}
IMPORT_ORDER = tuple(IMPORT_MODULE_PATHS)


def bootstrap_root_validator(instance_path: pathlib.Path, *, installed_root: pathlib.Path = pathlib.Path("/"),
                             current_executor_override: pathlib.Path | None = None) -> tuple[dict, pathlib.Path]:
    """Authenticate and load the complete Gate D import graph."""
    instance=load_json(instance_path)
    instance_schema=instance.get("schemaVersion")
    if instance_schema not in {3,4,5} or instance.get("kind")!="gate-d-representative-system-execution-instance":
        raise ValueError("installed trust bootstrap requires execution-instance schema 3, 4, or 5")
    reference=instance.get("qualificationRoot")
    if (not isinstance(reference,dict) or set(reference)!={"path","identityFile","identitySha256","ownerUid","mode"} or
            not isinstance(reference.get("path"),str) or not pathlib.PurePosixPath(reference["path"]).is_absolute() or
            reference["path"] in {"/","/usr","/var","/home"} or ".." in pathlib.PurePosixPath(reference["path"]).parts or
            not isinstance(reference.get("identityFile"),str) or pathlib.PurePosixPath(reference["identityFile"]).name!=reference["identityFile"] or
            reference["identityFile"] in {".",".."} or not SHA256.fullmatch(reference.get("identitySha256","")) or
            type(reference.get("ownerUid")) is not int or reference["ownerUid"]<0 or reference.get("mode")!="0700"):
        raise ValueError("invalid qualification-root trust preamble")
    root=pathlib.Path(reference["path"])
    def trusted_relative(relative: str) -> pathlib.Path:
        pure=pathlib.PurePosixPath(relative)
        if not isinstance(relative,str) or pure.is_absolute() or not pure.parts or ".." in pure.parts:
            raise ValueError("unsafe qualification-root trust path")
        path=root.joinpath(*pure.parts); component=root
        for part in pure.parts:
            component=component/part
            if component.exists() and component.is_symlink(): raise ValueError("qualification-root child trust path is symlinked")
        return path
    current=pathlib.Path(root.anchor)
    for part in root.parts[1:]:
        current=current/part
        if current.exists() and current.is_symlink(): raise ValueError("qualification-root trust path is symlinked")
    metadata=root.stat()
    if root.is_symlink() or not root.is_dir() or metadata.st_uid!=reference["ownerUid"] or stat.S_IMODE(metadata.st_mode)!=0o700:
        raise ValueError("qualification-root trust identity differs")
    marker=trusted_relative(reference["identityFile"])
    if marker.is_symlink() or not marker.is_file():
        raise ValueError("qualification-root trust marker differs")
    marker_bytes=marker.read_bytes()
    if hashlib.sha256(marker_bytes).hexdigest()!=reference["identitySha256"]: raise ValueError("qualification-root trust marker differs")
    marker_value=json.loads(marker_bytes)
    if (not isinstance(marker_value,dict) or set(marker_value)!={"SPDX-License-Identifier","schemaVersion","kind","rootPath","candidateRelease","sourceCommit"} or
            marker_value.get("SPDX-License-Identifier")!="MIT" or marker_value.get("schemaVersion")!=1 or marker_value.get("kind")!="gate-d-qualification-root-identity" or
            marker_value.get("rootPath")!=reference["path"] or not isinstance(marker_value.get("candidateRelease"),str) or not re.fullmatch(r"[0-9a-f]{40}",marker_value.get("sourceCommit",""))):
        raise ValueError("qualification-root trust marker identity is invalid")
    policy=instance.get("executionPolicy")
    if not isinstance(policy,dict): raise ValueError("execution policy trust preamble is absent")
    relative=policy.get("targetPlan")
    if not isinstance(relative,str) or pathlib.PurePosixPath(relative).is_absolute() or ".." in pathlib.PurePosixPath(relative).parts or not SHA256.fullmatch(policy.get("targetPlanSha256","")):
        raise ValueError("target-plan trust preamble is invalid")
    plan_path=trusted_relative(relative)
    if plan_path.is_symlink() or not plan_path.is_file():
        raise ValueError("target-plan trust identity differs")
    plan_bytes=plan_path.read_bytes()
    if hashlib.sha256(plan_bytes).hexdigest()!=policy["targetPlanSha256"]: raise ValueError("target-plan trust identity differs")
    plan=json.loads(plan_bytes); tooling=plan.get("tooling")
    expected_plan_schema={3:4,4:5,5:5}[instance_schema]
    if plan.get("schemaVersion")!=expected_plan_schema or plan.get("qualificationRoot")!=reference or not isinstance(tooling,dict):
        raise ValueError("target-plan root trust binding differs")
    item=tooling.get("rootValidator"); executor=tooling.get("permanentExecutor")
    keys={"sourcePath","installedPath","sourceSha256","installedSha256","installKind","candidateArchiveMember"}
    if (not isinstance(item,dict) or set(item)!=keys or item.get("installKind")!="copied" or item.get("candidateArchiveMember") is not True or
            item.get("sourceSha256")!=item.get("installedSha256") or not SHA256.fullmatch(item.get("sourceSha256","")) or
            item.get("installedPath")!="/usr/libexec/rp1-gpclk-dkms/gate_d_root.py"):
        raise ValueError("root-validator trust identity is invalid")
    current_executor=(current_executor_override.resolve() if current_executor_override is not None
                      else pathlib.Path(__file__).resolve())
    installed_executor=pathlib.Path(executor.get("installedPath","")) if isinstance(executor,dict) else pathlib.Path()
    if current_executor==installed_executor:
        validator=installed_root/item["installedPath"].lstrip("/"); expected=item["installedSha256"]
    else:
        validator=trusted_relative(item["sourcePath"]); expected=item["sourceSha256"]
        expected_executor=trusted_relative(executor.get("sourcePath","")) if isinstance(executor,dict) else pathlib.Path()
        if current_executor!=expected_executor: raise ValueError("staged executor trust identity differs")
    if instance_schema==3:
        if validator.is_symlink() or not validator.is_file(): raise ValueError("root validator is absent or symlinked")
        source=validator.read_bytes()
        if hashlib.sha256(source).hexdigest()!=expected: raise ValueError("root-validator bytes differ")
        module=types.ModuleType("gate_d_root"); module.__file__=str(validator)
        exec(compile(source,str(validator),"exec"),module.__dict__)
        sys.modules["gate_d_root"]=module
        return instance,root
    graph=plan.get("pythonModules")
    if not isinstance(graph,dict) or set(graph)!=set(IMPORT_MODULE_PATHS):
        raise ValueError("installed Python import graph is incomplete")
    graph_keys={"sourcePath","installedPath","sourceSha256","installedSha256","installKind","candidateArchiveMember"}
    payloads={}
    for name in IMPORT_ORDER:
        graph_item=graph[name]
        if (not isinstance(graph_item,dict) or set(graph_item)!=graph_keys or
                graph_item.get("sourcePath")!=f"scripts/{name}.py" or
                graph_item.get("installedPath")!=IMPORT_MODULE_PATHS[name] or
                graph_item.get("installKind")!="copied" or graph_item.get("candidateArchiveMember") is not True or
                graph_item.get("sourceSha256")!=graph_item.get("installedSha256") or
                not SHA256.fullmatch(graph_item.get("sourceSha256",""))):
            raise ValueError(f"invalid installed Python module identity: {name}")
        selected=(installed_root/graph_item["installedPath"].lstrip("/") if current_executor==installed_executor
                  else trusted_relative(graph_item["sourcePath"]))
        expected_sha=(graph_item["installedSha256"] if current_executor==installed_executor
                      else graph_item["sourceSha256"])
        if selected.is_symlink() or not selected.is_file():
            raise ValueError(f"installed Python module is absent or symlinked: {name}")
        metadata=selected.stat()
        expected_uid=0 if installed_root==pathlib.Path("/") else os.getuid()
        if metadata.st_uid!=expected_uid or stat.S_IMODE(metadata.st_mode)&0o022:
            raise ValueError(f"installed Python module ownership or mode differs: {name}")
        payload=selected.read_bytes()
        if hashlib.sha256(payload).hexdigest()!=expected_sha:
            raise ValueError(f"installed Python module bytes differ: {name}")
        tree=ast.parse(payload,filename=str(selected))
        local_imports=set()
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):
                local_imports.update(alias.name for alias in node.names if alias.name.startswith("gate_d_"))
            elif isinstance(node,ast.ImportFrom) and node.module and node.module.startswith("gate_d_"):
                local_imports.add(node.module)
        unknown=local_imports-set(IMPORT_MODULE_PATHS)
        if unknown:
            raise ValueError(f"unbound Python module import in {name}: {sorted(unknown)}")
        payloads[name]=(selected,payload)
    if graph["gate_d_root"]!=item:
        raise ValueError("root-validator and import-graph identities differ")
    previous={name:sys.modules.get(name) for name in IMPORT_ORDER}
    added=[]
    try:
        for name in IMPORT_ORDER:
            selected,payload=payloads[name]
            module=types.ModuleType(name); module.__file__=str(selected); module.__package__=""
            sys.modules[name]=module; added.append(name)
            exec(compile(payload,str(selected),"exec"),module.__dict__)
    except BaseException:
        for name in added:
            if previous[name] is None: sys.modules.pop(name,None)
            else: sys.modules[name]=previous[name]
        raise
    return instance,root


def _fsync_directory(path: pathlib.Path) -> None:
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_json(path: pathlib.Path, value: dict) -> None:
    if path.is_symlink():
        raise ValueError("journal path is a symlink")
    path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            json.dump(value, output, indent=2, sort_keys=True)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
        _fsync_directory(path.parent)
    finally:
        temporary.unlink(missing_ok=True)


def rooted(root: pathlib.Path, absolute: str) -> pathlib.Path:
    pure = pathlib.PurePosixPath(absolute)
    if not pure.is_absolute() or ".." in pure.parts:
        raise ValueError("unsafe absolute path")
    current = root
    for part in pure.parts[1:]:
        current /= part
        if current.is_symlink():
            raise ValueError(f"symlink in controlled path: {absolute}")
    return current


def device_tree_resource(root: pathlib.Path, name: str) -> pathlib.Path:
    """Resolve one fixed resource below the canonical kernel DT filesystem."""
    if not re.fullmatch(r"[a-z0-9][a-z0-9,._+-]*", name):
        raise ValueError("unsafe device-tree resource name")
    alias = root / "proc/device-tree"
    if not alias.is_symlink() or os.readlink(alias) != "/sys/firmware/devicetree/base":
        raise ValueError("canonical /proc/device-tree alias differs")
    canonical = rooted(root, "/sys/firmware/devicetree/base")
    expected_uid = 0 if root == pathlib.Path("/") else os.getuid()
    if (canonical.is_symlink() or not canonical.is_dir() or
            canonical.stat().st_uid != expected_uid or
            stat.S_IMODE(canonical.stat().st_mode) & 0o022):
        raise ValueError("canonical device-tree root identity differs")
    resource = rooted(root, f"/sys/firmware/devicetree/base/{name}")
    if resource.exists():
        if not resource.is_dir():
            raise ValueError("device-tree resource is not a direct directory")
        for descendant in resource.rglob("*"):
            if descendant.is_symlink():
                raise ValueError("symlink below canonical device-tree resource")
    return resource


def module_signing_policy(root: pathlib.Path, kernel_release: str) -> dict:
    config = rooted(root, f"/boot/config-{kernel_release}")
    if config.is_symlink() or not config.is_file():
        raise ValueError("exact kernel signing configuration is unavailable")
    lines = config.read_text(encoding="utf-8").splitlines()
    enabled = "CONFIG_MODULE_SIG=y" in lines
    disabled = "# CONFIG_MODULE_SIG is not set" in lines
    if enabled == disabled:
        raise ValueError("exact kernel signing configuration is ambiguous")

    cmdline_path = rooted(root, "/proc/cmdline")
    if cmdline_path.is_symlink() or not cmdline_path.is_file():
        raise ValueError("kernel command line is unavailable")
    cmdline = cmdline_path.read_text(encoding="ascii").strip().split()
    command_line_enforced = "module.sig_enforce=1" in cmdline

    sysctl = rooted(root, "/proc/sys/kernel/module_sig_enforce")
    if sysctl.exists() or sysctl.is_symlink():
        if sysctl.is_symlink() or not sysctl.is_file():
            raise ValueError("module signature enforcement sysctl is unsafe")
        value = sysctl.read_text(encoding="ascii").strip()
        if value not in {"0", "1"}:
            raise ValueError("module signature enforcement sysctl is malformed")
        sysctl_value: str | None = value
    else:
        sysctl_value = None

    lockdown = rooted(root, "/sys/kernel/security/lockdown")
    if lockdown.exists() or lockdown.is_symlink():
        if lockdown.is_symlink() or not lockdown.is_file():
            raise ValueError("kernel lockdown policy is unsafe")
        lockdown_value: str | None = lockdown.read_text(encoding="ascii").strip()
        if "[none]" not in lockdown_value:
            raise ValueError("kernel lockdown policy differs from reviewed non-enforcing row")
    else:
        lockdown_value = None

    if disabled:
        if sysctl_value is not None or command_line_enforced:
            raise ValueError("disabled module-signing configuration contradicts runtime policy")
        enforced = False
        source = "config-disabled-sysctl-absent"
    else:
        if sysctl_value is None:
            raise ValueError("enabled module-signing configuration requires runtime policy evidence")
        forced = "CONFIG_MODULE_SIG_FORCE=y" in lines
        enforced = forced or command_line_enforced or sysctl_value == "1"
        source = "config-enabled"
    return {"enforced": enforced, "source": source, "sysctl": sysctl_value,
            "configPath": f"/boot/config-{kernel_release}",
            "commandLineEnforced": command_line_enforced, "lockdown": lockdown_value}


def safe_extract(archive: pathlib.Path, destination: pathlib.Path) -> None:
    if archive.is_symlink() or not archive.is_file():
        raise ValueError("archive is absent or unsafe")
    destination.mkdir(parents=True, mode=0o700, exist_ok=False)
    with tarfile.open(archive, "r:gz") as source:
        members = source.getmembers()
        names: set[str] = set()
        roots: set[str] = set()
        for member in members:
            pure = pathlib.PurePosixPath(member.name)
            if (pure.is_absolute() or ".." in pure.parts or not pure.parts or
                    member.name in names or member.issym() or member.islnk() or
                    not (member.isfile() or member.isdir())):
                raise ValueError("archive contains an unsafe member")
            names.add(member.name)
            roots.add(pure.parts[0])
        if len(roots) != 1:
            raise ValueError("archive must contain one versioned root")
        for member in members:
            target = destination.joinpath(*pathlib.PurePosixPath(member.name).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            if member.isdir():
                target.mkdir(exist_ok=True)
            else:
                stream = source.extractfile(member)
                if stream is None:
                    raise ValueError("archive file has no content")
                fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), member.mode & 0o777)
                with os.fdopen(fd, "wb") as output:
                    while True:
                        block = stream.read(65536)
                        if not block:
                            break
                        output.write(block)
                    output.flush()
                    os.fsync(output.fileno())
        _fsync_directory(destination)


@dataclass(frozen=True)
class Action:
    kind: str
    name: str
    argv: tuple[str, ...] = ()
    expected: tuple[int, ...] = (0,)

    def as_json(self) -> dict:
        return {"kind": self.kind, "name": self.name, "argv": list(self.argv),
                "expectedStatus": list(self.expected)}


class ClosedDispatcher:
    """Candidate-neutral mapping from reviewed operations to fixed handlers."""

    INTERNAL = {
        "create-evidence", "capture-preflight", "verify-input-hashes",
        "snapshot-services", "stage-source", "verify-final-safety",
        "audit-residue", "capture-kernel-log-delta", "seal-evidence",
        "copy-candidate", "inject-stale-identity", "expect-preload-rejection",
        "copy-artifact", "flip-byte", "expect-preinstall-rejection",
        "remove-injected-copy", "verify-baseline-unchanged", "prove-inactive",
        "inventory-owned-paths", "verify-empty-package-state",
        "prove-empty-package-state", "inject-build-failure",
        "interrupt-after-checkpoint", "freeze-failed-journal",
        "verify-one-inactive-version",
        "remove-attempt-residue", "verify-signing-off", "verify-signing-unchanged",
        "start-busy-injector", "expect-removal-refusal", "stop-busy-injector",
    }
    COMMAND = {
        "quiesce-services", "restore-services", "install-successor",
        "install-predecessor", "stage-successor", "expect-build-failure",
        "recover-predecessor", "remove-failed-successor", "apply-route",
        "load-disabled", "query-release", "unbind-rebind", "unload",
        "remove-route", "remove-test-state", "select-prior-kernel",
        "pause-reboot-prior", "verify-prior-kernel", "restore-normal-boot",
        "pause-reboot-normal", "verify-normal-kernel",
        "run-to-checkpoint", "recover-new-journal",
    }
    OPERATIONS = INTERNAL | COMMAND

    def __init__(self, document: dict):
        self.document = document

    def action(self, operation: str) -> Action:
        if operation in self.INTERNAL:
            return Action("internal", operation)
        if operation not in self.COMMAND:
            raise ValueError(f"operation has no permanent handler: {operation}")
        values = self.document["inputs"]
        candidate = values["candidateRelease"]
        predecessor = values["predecessorVersion"]
        kernel = self.document["kernelRelease"]
        route = self.document["route"]
        staging = values["stagingDirectory"]
        dtbo = values.get(f"{route}Dtbo") if route in {"gpio4", "gpio20"} else None
        dtbo_path = pathlib.PurePosixPath(dtbo or "/invalid/route-neutral.dtbo")
        subordinate = values.get("subordinateLifecycle")
        transition_path = f"{staging}/transition-operation.json"
        recovery_path = f"{staging}/recovery-operation.json"
        instance_path = f"{staging}/execution-instance.json"
        transition_journal = (f"{self.document['evidenceDirectory']}/transition/transaction.json")
        recovery_journal = (f"{self.document['evidenceDirectory']}/recovery/transaction.json")
        table: dict[str, tuple[str, ...]] = {
            "install-successor": ("/usr/libexec/rp1-gpclk-dkms/gate-d-lifecycle", "dispatch", "dkms-install", candidate, kernel, staging, "--execute"),
            "install-predecessor": ("/usr/libexec/rp1-gpclk-dkms/gate-d-lifecycle", "dispatch", "dkms-install", predecessor, kernel, staging, "--execute"),
            "stage-successor": ("/usr/libexec/rp1-gpclk-dkms/gate-d-lifecycle", "dispatch", "stage", candidate, staging, "--execute"),
            "expect-build-failure": ("/usr/libexec/rp1-gpclk-dkms/gate-d-lifecycle", "dispatch", "expect-build-failure", candidate, kernel, staging, "--execute"),
            "recover-predecessor": ("/usr/libexec/rp1-gpclk-dkms/gate-d-lifecycle", "dispatch", "recover", predecessor, candidate, kernel, staging, "--execute"),
            "remove-failed-successor": ("/usr/libexec/rp1-gpclk-dkms/gate-d-lifecycle", "dispatch", "dkms-remove", candidate, kernel, staging, "--execute"),
            "apply-route": ("/usr/bin/dtoverlay", "-d", str(dtbo_path.parent), dtbo_path.stem),
            "load-disabled": ("/usr/sbin/modprobe", "rp1_gpclk_dkms", "live_output=0"),
            "query-release": ("/usr/libexec/rp1-gpclk-dkms/gate-d-uapi-probe", route, candidate),
            "unbind-rebind": ("/usr/libexec/rp1-gpclk-dkms/gate-d-platform", "unbind-bind-cycle", "--execute"),
            "unload": ("/usr/sbin/modprobe", "-r", "rp1_gpclk_dkms"),
            "remove-route": ("/usr/bin/dtoverlay", "-r", dtbo_path.stem),
            "remove-test-state": ("/usr/libexec/rp1-gpclk-dkms/gate-d-lifecycle", "dispatch", "complete-removal", predecessor, candidate, kernel, staging, "--execute"),
            "select-prior-kernel": ("/usr/libexec/rp1-gpclk-dkms/gate-d-boot", "select", f"{staging}/boot-operation.json", "--execute"),
            "pause-reboot-prior": ("/usr/bin/systemctl", "reboot"),
            "verify-prior-kernel": ("/usr/libexec/rp1-gpclk-dkms/gate-d-boot", "verify-running", values["boot"]["priorKernel"]),
            "restore-normal-boot": ("/usr/libexec/rp1-gpclk-dkms/gate-d-boot", "restore", f"{staging}/boot-operation.json", "--execute"),
            "pause-reboot-normal": ("/usr/bin/systemctl", "reboot"),
            "verify-normal-kernel": ("/usr/libexec/rp1-gpclk-dkms/gate-d-boot", "verify-running", values["boot"]["normalKernel"]),
            "run-to-checkpoint": ("/usr/libexec/rp1-gpclk-dkms/gate-d-lifecycle", "execute",
                                  transition_path, "--instance", instance_path, "--journal",
                                  transition_journal, "--stop-after",
                                  subordinate["checkpoint"] if subordinate else "preflight", "--execute"),
            "recover-new-journal": ("/usr/libexec/rp1-gpclk-dkms/gate-d-lifecycle", "execute",
                                     recovery_path, "--instance", instance_path, "--journal",
                                     recovery_journal, "--recover-from", transition_journal, "--execute"),
        }
        if operation in {"quiesce-services", "restore-services"}:
            return Action("service-transaction", operation)
        argv = table[operation]
        flat = " ".join(argv).lower()
        if any(token in flat for token in PROHIBITED) or any("${" in item or "*" in item for item in argv):
            raise ValueError("prohibited command construction")
        expected = (1,) if operation in {"expect-build-failure", "run-to-checkpoint"} else (0,)
        return Action("command", operation, argv, expected)

    def plan(self) -> list[dict]:
        return [self.action(step["operation"]).as_json() for step in self.document["steps"]]


def validate_document(document: dict) -> None:
    scripts = pathlib.Path(__file__).resolve().parent
    import sys
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    from gate_d_attempts import validate_document as validate_attempt
    validate_attempt(document)
    operations = [step["operation"] for step in document["steps"]]
    if not set(operations).issubset(ClosedDispatcher.OPERATIONS):
        raise ValueError("attempt contains an operation without a permanent handler")
    dispatcher = ClosedDispatcher(document)
    plan = dispatcher.plan()
    if [step["action"] for step in document["steps"]] != plan:
        raise ValueError("attempt action plan differs from permanent dispatcher")


class Runner:
    def __call__(self, argv: list[str], timeout: int) -> tuple[int, str]:
        result = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, timeout=timeout,
                                env=FIXED_ENV, check=False)
        return result.returncode, result.stdout


class FakeRunner:
    def __init__(self, statuses: dict[str, int] | None = None, *, seconds: int = 1):
        self.statuses = statuses or {}
        self.seconds = seconds
        self.commands: list[list[str]] = []

    def __call__(self, argv: list[str], timeout: int) -> tuple[int, str]:
        if timeout < self.seconds:
            raise TimeoutError("fake command exceeded remaining total deadline")
        self.commands.append(list(argv))
        joined = " ".join(argv)
        default = 1 if any(item in argv for item in ("expect-build-failure", "expect-removal-refusal")) else 0
        return self.statuses.get(joined, default), "fake-output"


class FilesystemFake:
    """Stateful offline target used to exercise complete qualification plans."""

    def __init__(self, root: pathlib.Path, document: dict):
        self.root = root
        self.document = document
        self.services = {item["name"]: item["requiredPreState"] for item in document["services"]}
        self.original_services = dict(self.services)
        self.dkms: dict[str, set[str]] = {}
        self.dkms_phase: dict[tuple[str, str], str] = {}
        self.module_loaded = False
        self.overlay: str | None = None
        self.endpoint = False
        self.owner = False
        self.open_descriptor = False
        self.kernel = document["inputs"]["boot"]["normalKernel"]
        self.injected: str | None = None
        self.command_log: list[list[str]] = []

    def run(self, argv: list[str], timeout: int) -> tuple[int, str]:
        if timeout <= 0:
            raise TimeoutError("no fake deadline remains")
        self.command_log.append(list(argv))
        operation = argv[2] if len(argv) > 2 and argv[0].endswith("gate-d-lifecycle") and argv[1] == "dispatch" else None
        if argv[0].endswith("gate-d-lifecycle") and len(argv) > 2 and argv[1] == "execute":
            journal = pathlib.Path(argv[argv.index("--journal") + 1])
            journal_path = rooted(self.root, str(journal))
            subordinate = self.document["inputs"]["subordinateLifecycle"]
            if "--stop-after" in argv:
                checkpoint = argv[argv.index("--stop-after") + 1]
                successor = self.document["inputs"]["candidateRelease"]
                kernel = self.document["kernelRelease"]
                order = ["preflight", "retain-predecessor", "dkms-add", "dkms-build",
                         "dkms-install", "load-disabled", "query-disabled",
                         "uapi-query-release", "unbind-bind", "unload", "dkms-uninstall",
                         "dkms-remove", "owned-residue-remove", "verify-final-state", "commit-state"]
                reached = set(order[:order.index(checkpoint) + 1])
                if "dkms-add" in reached:
                    self.dkms.setdefault(successor, set()).add(kernel)
                    self.dkms_phase[(successor, kernel)] = "registered"
                if "dkms-build" in reached:
                    self.dkms_phase[(successor, kernel)] = "built"
                if "dkms-install" in reached:
                    self.dkms_phase[(successor, kernel)] = "installed"
                if "load-disabled" in reached and "unload" not in reached:
                    self.module_loaded = self.endpoint = True
                if "unload" in reached:
                    self.module_loaded = self.endpoint = False
                if "dkms-uninstall" in reached:
                    self.dkms_phase[(successor, kernel)] = "built"
                if "dkms-remove" in reached:
                    self.dkms.pop(successor, None)
                    self.dkms_phase.pop((successor, kernel), None)
                atomic_json(journal_path, {"status": "inactive-recovery-required",
                            "operationId": subordinate["transition"]["operationId"],
                            "checkpoint": checkpoint, "liveOutput": False,
                            "phase": self.dkms_phase.get((successor, kernel), "absent"),
                            "moduleLoaded": self.module_loaded, "endpointOpen": self.endpoint,
                            "overlay": self.overlay})
                return 1, "intentional checkpoint interruption"
            predecessor = self.document["inputs"]["predecessorVersion"]
            successor = self.document["inputs"]["candidateRelease"]
            kernel = self.document["kernelRelease"]
            self.dkms.pop(successor, None)
            self.dkms_phase.pop((successor, kernel), None)
            self.dkms = {predecessor: {kernel}}
            self.dkms_phase[(predecessor, kernel)] = "installed"
            self.module_loaded = self.endpoint = False
            atomic_json(journal_path, {"status": "complete", "operationId": subordinate["recovery"]["operationId"],
                        "recovers": subordinate["transition"]["operationId"], "liveOutput": False})
            return 0, "recovered"
        if operation == "dkms-install":
            self.dkms.setdefault(argv[3], set()).add(argv[4])
            self.dkms_phase[(argv[3], argv[4])] = "installed"
        elif operation in {"dkms-remove", "complete-removal"}:
            if self.owner or self.open_descriptor:
                return 1, "busy"
            versions = [argv[3]] if operation == "dkms-remove" else argv[3:5]
            for version in versions:
                self.dkms.pop(version, None)
                for key in [key for key in self.dkms_phase if key[0] == version]:
                    self.dkms_phase.pop(key)
        elif operation == "expect-build-failure":
            if self.injected != "compiler-wrapper":
                return 0, "failure injection absent"
            return 1, "bounded compiler failure"
        elif operation == "recover":
            self.dkms.pop(argv[4], None)
            self.dkms.setdefault(argv[3], set()).add(argv[5])
            self.dkms_phase[(argv[3], argv[5])] = "installed"
            self.module_loaded = self.endpoint = False
            self.overlay = None
        elif argv[0].endswith("dtoverlay") and argv[1] == "-d":
            selected = "gpio20" if "gpio20" in argv[3] else "gpio4"
            if self.overlay is not None:
                return 2, "route conflict"
            self.overlay = selected
        elif argv[0].endswith("dtoverlay") and argv[1] == "-r":
            if self.module_loaded:
                return 2, "module loaded"
            self.overlay = None
        elif argv[0].endswith("modprobe") and argv[1:] == ["rp1_gpclk_dkms", "live_output=0"]:
            if not self.overlay or not self.dkms:
                return 2, "load precondition"
            self.module_loaded = self.endpoint = True
        elif argv[0].endswith("modprobe") and argv[1:] == ["-r", "rp1_gpclk_dkms"]:
            if self.owner or self.open_descriptor:
                return 2, "busy"
            self.module_loaded = self.endpoint = False
        elif argv[0].endswith("gate-d-uapi-probe"):
            if not self.module_loaded or not self.endpoint:
                return 2, "endpoint absent"
            return 0, "live_eligible=0 released=1"
        elif argv[0].endswith("gate-d-boot") and argv[1] == "verify-running":
            return (0, "verified") if self.kernel == argv[2] else (2, "wrong kernel")
        elif argv[0].endswith("gate-d-boot") and argv[1] == "select":
            self.kernel = self.document["inputs"]["boot"]["priorKernel"]
        elif argv[0].endswith("gate-d-boot") and argv[1] == "restore":
            self.kernel = self.document["inputs"]["boot"]["normalKernel"]
        elif argv == ["/usr/bin/systemctl", "reboot"]:
            pass
        elif argv[0].endswith("gate-d-busy-injector") and argv[1] == "start":
            self.owner = self.document["attempt"].startswith("owner-")
            self.open_descriptor = not self.owner
        elif argv[0].endswith("gate-d-busy-injector") and argv[1] == "stop":
            self.owner = self.open_descriptor = False
        return 0, "fake-output"

    def internal(self, operation: str, document: dict, root: pathlib.Path) -> None:
        if operation in {"create-evidence", "verify-input-hashes", "stage-source", "seal-evidence"}:
            default_internal(operation, document, root)
            return
        if operation in {"copy-candidate", "inject-stale-identity", "expect-preload-rejection",
                         "copy-artifact", "flip-byte", "expect-preinstall-rejection",
                         "remove-injected-copy"}:
            default_internal(operation, document, root)
            if operation in {"inject-stale-identity", "flip-byte"}:
                self.injected = document["attempt"]
            elif operation == "remove-injected-copy":
                self.injected = None
            return
        evidence = rooted(root, document["evidenceDirectory"])
        if operation == "capture-preflight" and (self.module_loaded or self.overlay or self.owner or self.open_descriptor):
            raise ValueError("unsafe fake preflight")
        elif operation == "snapshot-services":
            atomic_json(evidence / "services-before.json", self.services)
        elif operation == "quiesce-services":
            for item in document["services"]:
                if self.services[item["name"]] != item["requiredPreState"]:
                    raise ValueError("service pre-state drift")
                if item["action"] == "stop-then-restore-exact":
                    self.services[item["name"]] = "inactive"
        elif operation == "restore-services":
            self.services = dict(self.original_services)
        elif operation == "inject-build-failure":
            self.injected = "compiler-wrapper"
        elif operation == "start-busy-injector":
            self.owner = document["attempt"].startswith("owner-")
            self.open_descriptor = not self.owner
            atomic_json(evidence / "busy-state.json", {"ready": True,
                        "mode": "owner" if self.owner else "open",
                        "route": document["route"], "liveOutput": False})
        elif operation == "expect-removal-refusal":
            if not (self.owner or self.open_descriptor):
                raise ValueError("busy readiness is absent")
        elif operation == "stop-busy-injector":
            self.owner = self.open_descriptor = False
        elif operation == "inject-stale-identity":
            self.injected = document["attempt"]
        elif operation == "flip-byte":
            self.injected = document["attempt"]
        elif operation in {"expect-preload-rejection", "expect-preinstall-rejection"}:
            if self.injected != document["attempt"] or self.module_loaded or self.dkms:
                raise ValueError("injected identity was not rejected before mutation")
        elif operation == "remove-injected-copy":
            self.injected = None
        elif operation == "interrupt-after-checkpoint":
            state = load_json(evidence / "transition/transaction.json")
            if state.get("checkpoint") != document["attempt"].removeprefix("after-"):
                raise ValueError("fake subordinate checkpoint differs")
        elif operation == "freeze-failed-journal":
            failed = evidence / "transition/transaction.json"
            failed.chmod(0o400)
            failed.parent.chmod(0o500)
            if stat.S_IMODE(failed.stat().st_mode) & 0o222:
                raise ValueError("failed journal remains mutable")
        elif operation == "verify-one-inactive-version":
            expected = {document["inputs"]["predecessorVersion"]: {document["kernelRelease"]}}
            if self.dkms != expected or self.module_loaded or self.endpoint:
                raise ValueError("mixed recovered version state")
        elif operation in {"verify-baseline-unchanged", "verify-empty-package-state", "prove-empty-package-state"}:
            if self.dkms or self.module_loaded or self.overlay or self.owner or self.open_descriptor:
                raise ValueError("fake baseline differs")
        elif operation in {"prove-inactive", "verify-final-safety", "audit-residue"}:
            if self.module_loaded or self.overlay or self.owner or self.open_descriptor:
                raise ValueError("fake runtime residue")
            if operation == "verify-final-safety" and self.services != self.original_services:
                raise ValueError("services were not restored")
            if (operation == "audit-residue" and document.get("schemaVersion") == 2 and
                    rooted(root, document["inputs"]["stagingDirectory"]).exists()):
                raise ValueError("attempt staging residue remains")
        elif operation == "remove-attempt-residue":
            default_internal(operation, document, root)
            return
        marker = evidence / f"{operation}.json"
        if not marker.exists():
            atomic_json(marker, {"operation": operation, "liveOutput": False})


def _journal_identity(document: dict, document_sha256: str, index_sha256: str) -> dict:
    return {"schemaVersion": VERSION, "operationId": document["operationId"],
            "documentSha256": document_sha256, "indexSha256": index_sha256,
            "executorSha256": digest(pathlib.Path(__file__).resolve()),
            "status": "inactive-in-progress", "liveOutput": False,
            "nextStep": 0, "records": [], "startedUtc": utc(),
            "startedMonotonicNs": time.monotonic_ns(), "recoveryRequired": True,
            "deadlineEpochSeconds": time.time(),
            "sealed": False}


def seal_directory(evidence: pathlib.Path) -> None:
    manifest = evidence / "SHA256SUMS"
    if manifest.exists() or manifest.is_symlink():
        raise ValueError("evidence checksum manifest already exists")
    lines = []
    for path in sorted(evidence.rglob("*")):
        if path.is_symlink():
            raise ValueError("evidence contains a symlink")
        if path.is_file():
            lines.append(f"{digest(path)}  {path.relative_to(evidence).as_posix()}\n")
    fd = os.open(manifest, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o400)
    with os.fdopen(fd, "w", encoding="ascii") as output:
        output.writelines(lines)
        output.flush()
        os.fsync(output.fileno())
    for path in sorted(evidence.rglob("*"), reverse=True):
        if path.is_file() and not path.is_symlink():
            path.chmod(0o400)
        elif path.is_dir() and not path.is_symlink():
            path.chmod(0o500)
    evidence.chmod(0o500)
    _fsync_directory(evidence.parent)


def verify_sealed_directory(evidence: pathlib.Path) -> None:
    manifest = evidence / "SHA256SUMS"
    if evidence.is_symlink() or not evidence.is_dir() or manifest.is_symlink() or not manifest.is_file():
        raise ValueError("sealed evidence identity is absent")
    expected = {}
    for line in manifest.read_text(encoding="ascii").splitlines():
        if "  " not in line:
            raise ValueError("malformed evidence checksum line")
        sha, relative = line.split("  ", 1)
        if not SHA256.fullmatch(sha) or pathlib.PurePosixPath(relative).is_absolute() or ".." in pathlib.PurePosixPath(relative).parts:
            raise ValueError("unsafe evidence checksum entry")
        expected[relative] = sha
    actual = {}
    for path in evidence.rglob("*"):
        if path.is_symlink():
            raise ValueError("sealed evidence contains a symlink")
        if path.is_file() and path != manifest:
            actual[path.relative_to(evidence).as_posix()] = digest(path)
        if stat.S_IMODE(path.stat().st_mode) & 0o222:
            raise ValueError("sealed evidence remains writable")
    if actual != expected or stat.S_IMODE(evidence.stat().st_mode) & 0o222:
        raise ValueError("sealed evidence checksum or mode differs")


def execute(document: dict, *, document_sha256: str, index_sha256: str,
            root: pathlib.Path, runner: Callable[[list[str], int], tuple[int, str]],
            internal: Callable[[str, dict, pathlib.Path], None], stop_after: str | None = None,
            recover_from: pathlib.Path | None = None, resume: bool = False) -> dict:
    validate_document(document)
    evidence = rooted(root, document["evidenceDirectory"])
    journal_path = rooted(root, document["journal"])
    if resume:
        if evidence.is_symlink() or not evidence.is_dir() or journal_path.is_symlink() or not journal_path.is_file():
            raise ValueError("resumable evidence is absent or unsafe")
        state = load_json(journal_path)
        if (state.get("status") != "reboot-required" or state.get("operationId") != document["operationId"] or
                state.get("documentSha256") != document_sha256 or state.get("indexSha256") != index_sha256 or
                state.get("executorSha256") != digest(pathlib.Path(__file__).resolve()) or state.get("sealed") is not False):
            raise ValueError("reboot-resume journal identity differs")
    else:
        if evidence.exists() or evidence.is_symlink():
            raise ValueError("evidence directory already exists")
        evidence.mkdir(parents=True, mode=0o700)
        state = _journal_identity(document, document_sha256, index_sha256)
        state["deadlineEpochSeconds"] = time.time() + document["deadlineSeconds"]
        atomic_json(journal_path, state)
    if recover_from is not None:
        prior_path = rooted(root, str(recover_from))
        verify_sealed_directory(prior_path.parent)
        prior = load_json(prior_path)
        if (prior.get("status") != "inactive-recovery-required" or
                prior.get("liveOutput") is not False or prior.get("sealed") is not True or
                stat.S_IMODE(prior_path.stat().st_mode) & 0o222):
            raise ValueError("recovery source is not an immutable inactive failed journal")
        if prior.get("operationId") == document["operationId"]:
            raise ValueError("recovery requires a new operation identity")
        state["recovers"] = {"operationId": prior["operationId"],
                             "journalSha256": digest(prior_path)}
    started_ns = state["startedMonotonicNs"]
    dispatcher = ClosedDispatcher(document)
    try:
        for number, step in enumerate(document["steps"][state["nextStep"]:], start=state["nextStep"]):
            action = dispatcher.action(step["operation"])
            elapsed = (time.monotonic_ns() - started_ns) / 1_000_000_000
            remaining = min(math.ceil(document["deadlineSeconds"] - elapsed),
                            math.ceil(state["deadlineEpochSeconds"] - time.time()))
            if remaining <= 0:
                raise TimeoutError("attempt total deadline exhausted")
            record = {"step": number, "stepId": step["id"], "operation": step["operation"],
                      "action": action.as_json(), "status": "pending", "startUtc": utc(),
                      "startMonotonicNs": time.monotonic_ns(), "remainingDeadlineSeconds": remaining}
            state["records"].append(record)
            atomic_json(journal_path, state)
            if action.kind == "command":
                status, output = runner(list(action.argv), remaining)
                record.update({"status": status, "output": output[:MAX_OUTPUT],
                               "outputTruncated": len(output) > MAX_OUTPUT})
                if status not in action.expected:
                    raise subprocess.CalledProcessError(status, action.argv, output=output)
            else:
                internal(action.name, document, root)
                record.update({"status": 0, "output": "", "outputTruncated": False})
            record.update({"endUtc": utc(), "endMonotonicNs": time.monotonic_ns()})
            state["nextStep"] = number + 1
            atomic_json(journal_path, state)
            if step["operation"] in {"pause-reboot-prior", "pause-reboot-normal"}:
                state.update({"status": "reboot-required", "recoveryRequired": True,
                              "expectedKernel": (document["inputs"]["boot"]["priorKernel"]
                                                 if step["operation"] == "pause-reboot-prior"
                                                 else document["inputs"]["boot"]["normalKernel"]),
                              "rebootRequestedUtc": utc()})
                atomic_json(journal_path, state)
                return state
            if stop_after == step["operation"]:
                raise InterruptedError(step["operation"])
        state.update({"status": "complete", "recoveryRequired": False,
                      "completedUtc": utc(), "sealed": True})
        atomic_json(journal_path, state)
        seal_directory(evidence)
        return state
    except BaseException as error:
        completed_operations = {record["operation"] for record in state["records"]
                                if record.get("status") in {0, 1}}
        cleanup = []
        for operation, required in (("stop-busy-injector", "start-busy-injector"),
                                    ("unload", "load-disabled"),
                                    ("remove-route", "apply-route"),
                                    ("restore-services", "quiesce-services")):
            if required not in completed_operations or operation in completed_operations:
                continue
            action = dispatcher.action(operation)
            item = {"operation": operation, "action": action.as_json(), "status": "pending"}
            cleanup.append(item)
            try:
                if action.kind == "command":
                    status, output = runner(list(action.argv), max(1, document["deadlineSeconds"]))
                    item.update({"status": status, "output": output[:MAX_OUTPUT]})
                    if status not in action.expected:
                        raise subprocess.CalledProcessError(status, action.argv, output=output)
                else:
                    internal(operation, document, root)
                    item["status"] = 0
            except BaseException as cleanup_error:
                item.update({"status": "failed", "failure": type(cleanup_error).__name__})
        if cleanup:
            state["compensation"] = cleanup
        state.update({"status": "inactive-recovery-required", "recoveryRequired": True,
                      "failure": type(error).__name__, "failedUtc": utc(), "sealed": True})
        atomic_json(journal_path, state)
        seal_directory(evidence)
        raise


def default_internal(operation: str, document: dict, root: pathlib.Path) -> None:
    """Target internal primitives; deliberately excludes hardware operations."""
    evidence = rooted(root, document["evidenceDirectory"])
    staging = rooted(root, document["inputs"]["stagingDirectory"])
    if operation == "create-evidence":
        return
    def command(argv: list[str], *, accepted: tuple[int, ...] = (0,), timeout: int = 30) -> str:
        result = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, timeout=timeout,
                                env=FIXED_ENV, check=False)
        if result.returncode not in accepted:
            raise subprocess.CalledProcessError(result.returncode, argv, output=result.stdout)
        return result.stdout
    if operation == "capture-preflight":
        if rooted(root, "/sys/module/rp1_gpclk_dkms").exists() or rooted(root, "/dev/rp1-gpclk").exists():
            raise ValueError("candidate runtime is already present")
        inputs = document["inputs"]
        running_kernel = command(["/usr/bin/uname", "-r"]).strip()
        if running_kernel != document["kernelRelease"]:
            raise ValueError("running kernel differs from attempt")
        boot_id_path = rooted(root, "/proc/sys/kernel/random/boot_id")
        if boot_id_path.is_symlink() or not boot_id_path.is_file():
            raise ValueError("boot identity is unavailable")
        boot_id = boot_id_path.read_text(encoding="ascii").strip()
        if not re.fullmatch(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", boot_id):
            raise ValueError("boot identity is malformed")
        signing = module_signing_policy(root, running_kernel)
        if signing["enforced"] is not False:
            raise ValueError("signing policy differs from reviewed non-enforcing row")
        overlays = command(["/usr/bin/dtoverlay", "-l"], accepted=(0, 1))
        if "rp1-gpclk-gpio4" in overlays or "rp1-gpclk-gpio20" in overlays:
            raise ValueError("a Gate D route overlay is already active")
        resource = device_tree_resource(root, "rp1-gpclk")
        if resource.exists():
            raise ValueError("foreign or stale RP1 GPCLK resource exists")
        tool_hashes = {}
        for name, item in inputs["tooling"].items():
            required_tool_keys = {"sourcePath", "installedPath", "sourceSha256", "installedSha256",
                                  "installKind", "candidateArchiveMember"}
            if set(item) != required_tool_keys or item["installKind"] not in {"copied", "target-built"}:
                raise ValueError(f"legacy or malformed permanent tool identity: {name}")
            if item["installKind"] == "copied" and item["sourceSha256"] != item["installedSha256"]:
                raise ValueError(f"copied permanent tool identities differ: {name}")
            expected_kind = "target-built" if item["sourcePath"].endswith(".c") else "copied"
            if item["installKind"] != expected_kind:
                raise ValueError(f"permanent tool install kind differs: {name}")
            installed = rooted(root, item["installedPath"])
            if installed.is_symlink() or not installed.is_file() or digest(installed) != item["installedSha256"]:
                raise ValueError(f"installed permanent tool differs: {name}")
            tool_hashes[name] = {"path": item["installedPath"], "sha256": item["installedSha256"],
                                 "installKind": item["installKind"]}
        atomic_json(evidence / "preflight.json", {"hostId": document["hostId"],
                    "runningKernel": running_kernel, "bootId": boot_id,
                    "moduleSigningPolicy": signing, "activeOverlays": overlays.splitlines(),
                    "resourceConflict": False, "installedTools": tool_hashes,
                    "liveOutput": False})
        return
    if operation == "snapshot-services":
        states = {}
        for item in document["services"]:
            status = subprocess.run(["/usr/bin/systemctl", "is-active", item["name"]],
                                    stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, timeout=10,
                                    env=FIXED_ENV, check=False)
            state = status.stdout.strip()
            if state != item["requiredPreState"]:
                raise ValueError(f"service pre-state drift: {item['name']}")
            states[item["name"]] = state
        atomic_json(evidence / "services-before.json", states)
        return
    if operation == "quiesce-services":
        states = load_json(evidence / "services-before.json")
        for item in document["services"]:
            if item["action"] == "stop-then-restore-exact" and states[item["name"]] == "active":
                command(["/usr/bin/systemctl", "stop", item["name"]])
        return
    if operation == "restore-services":
        states = load_json(evidence / "services-before.json")
        for item in document["services"]:
            if item["action"] == "stop-then-restore-exact" and states[item["name"]] == "active":
                command(["/usr/bin/systemctl", "start", item["name"]])
        return
    if operation == "verify-input-hashes":
        inputs = document["inputs"]
        for path_field, hash_field in (("candidateArchive", "candidateArchiveSha256"),
                                       ("predecessorArchive", "predecessorArchiveSha256"),
                                       ("gpio4Dtbo", "gpio4DtboSha256"),
                                       ("gpio20Dtbo", "gpio20DtboSha256")):
            path = rooted(root, inputs[path_field])
            if path.is_symlink() or not path.is_file() or digest(path) != inputs[hash_field]:
                raise ValueError(f"input identity mismatch: {path_field}")
        return
    if operation == "stage-source":
        staging.mkdir(parents=True, mode=0o700, exist_ok=False)
        inputs = document["inputs"]
        safe_extract(rooted(root, inputs["candidateArchive"]), staging / "candidate")
        safe_extract(rooted(root, inputs["predecessorArchive"]), staging / "predecessor")
        subordinate = inputs.get("subordinateLifecycle")
        if subordinate is not None:
            atomic_json(staging / "transition-operation.json", subordinate["transition"])
            atomic_json(staging / "recovery-operation.json", subordinate["recovery"])
        return
    if operation == "inject-build-failure":
        wrapper = staging / "compiler-failure"
        fd = os.open(wrapper, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o700)
        with os.fdopen(fd, "w", encoding="ascii") as output:
            output.write("#!/bin/sh\nexit 73\n")
            output.flush()
            os.fsync(output.fileno())
        return
    if operation == "copy-candidate":
        injection = staging / "injection"
        injection.mkdir(mode=0o700, exist_ok=False)
        identities = {"release": document["inputs"]["candidateRelease"],
                      "kernel": document["kernelRelease"],
                      "uapi": document["inputs"]["uapiSha256"],
                      "gpio4-overlay": document["inputs"]["gpio4DtboSha256"],
                      "gpio20-overlay": document["inputs"]["gpio20DtboSha256"],
                      "enrollment": "signing-not-enforced"}
        atomic_json(injection / "identities.json", identities)
        atomic_json(injection / "original-identities.json", identities)
        return
    if operation == "inject-stale-identity":
        path = staging / "injection/identities.json"
        identities = load_json(path)
        selected = document["attempt"]
        if selected not in identities:
            raise ValueError("unknown stale identity selector")
        identities[selected] = "stale-" + str(identities[selected])
        atomic_json(path, identities)
        return
    if operation == "expect-preload-rejection":
        original = load_json(staging / "injection/original-identities.json")
        injected = load_json(staging / "injection/identities.json")
        changed = [key for key in original if original[key] != injected.get(key)]
        if changed != [document["attempt"]]:
            raise ValueError("stale injection did not alter exactly one identity")
        return
    if operation == "copy-artifact":
        injection = staging / "injection"
        injection.mkdir(mode=0o700, exist_ok=False)
        source_field = {"archive": "candidateArchive", "gpio4-dtbo": "gpio4Dtbo",
                        "gpio20-dtbo": "gpio20Dtbo"}.get(document["attempt"])
        if source_field is None:
            raise ValueError("unknown corrupt artifact selector")
        source = rooted(root, document["inputs"][source_field])
        target = injection / source.name
        target.write_bytes(source.read_bytes())
        atomic_json(injection / "artifact.json", {"sourceField": source_field,
                    "originalSha256": digest(target), "copy": str(target)})
        return
    if operation == "flip-byte":
        record = load_json(staging / "injection/artifact.json")
        path = pathlib.Path(record["copy"])
        data = path.read_bytes()
        if not data:
            raise ValueError("cannot corrupt an empty artifact")
        path.write_bytes(bytes([data[0] ^ 1]) + data[1:])
        return
    if operation == "expect-preinstall-rejection":
        record = load_json(staging / "injection/artifact.json")
        if digest(pathlib.Path(record["copy"])) == record["originalSha256"]:
            raise ValueError("artifact corruption is absent")
        return
    if operation == "remove-injected-copy":
        injection = staging / "injection"
        if injection.is_symlink() or not injection.is_dir():
            raise ValueError("injection directory is absent or unsafe")
        for path in sorted(injection.iterdir(), reverse=True):
            if path.is_symlink() or not path.is_file():
                raise ValueError("unexpected injection member")
            path.unlink()
        injection.rmdir()
        return
    if operation == "start-busy-injector":
        mode, route = document["attempt"].split("-", 1)
        log = staging / "busy.jsonl"
        ready = staging / "busy.ready.json"
        output = log.open("xb")
        process = subprocess.Popen(["/usr/libexec/rp1-gpclk-dkms/gate-d-busy-injector",
                                    mode, route, document["inputs"]["candidateRelease"],
                                    str(min(900, document["deadlineSeconds"]))],
                                   stdin=subprocess.DEVNULL, stdout=output,
                                   stderr=subprocess.STDOUT, env=FIXED_ENV)
        output.close()
        deadline = time.monotonic() + 10
        parsed = None
        while time.monotonic() < deadline and process.poll() is None:
            for line in log.read_text(errors="replace").splitlines() if log.exists() else []:
                try:
                    value = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if value.get("event") == "ready":
                    parsed = value
                    break
            if parsed:
                break
            time.sleep(0.05)
        if parsed != {"event": "ready", "mode": mode, "route": route,
                      "liveEligible": False, "acquired": mode == "owner"}:
            process.terminate()
            process.wait(timeout=5)
            raise ValueError("busy injector readiness is absent or malformed")
        atomic_json(ready, {**parsed, "pid": process.pid})
        return
    if operation == "expect-removal-refusal":
        ready = load_json(staging / "busy.ready.json")
        try:
            os.kill(ready["pid"], 0)
        except (ProcessLookupError, PermissionError, TypeError):
            raise ValueError("busy injector is not alive")
        return
    if operation == "stop-busy-injector":
        ready = load_json(staging / "busy.ready.json")
        try:
            os.kill(ready["pid"], 15)
        except ProcessLookupError:
            raise ValueError("busy injector exited before controlled stop")
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            try:
                os.kill(ready["pid"], 0)
            except ProcessLookupError:
                return
            time.sleep(0.05)
        raise TimeoutError("busy injector did not stop")
    if operation == "interrupt-after-checkpoint":
        subordinate = document["inputs"]["subordinateLifecycle"]
        journal = evidence / "transition/transaction.json"
        state = load_json(journal)
        if (state.get("status") != "inactive-recovery-required" or
                state.get("checkpoint") != subordinate["checkpoint"] or
                state.get("liveOutput") is not False):
            raise ValueError("subordinate interruption journal differs")
        return
    if operation == "freeze-failed-journal":
        directory = evidence / "transition"
        journal = directory / "transaction.json"
        if journal.is_symlink() or not journal.is_file():
            raise ValueError("subordinate failed journal is absent")
        journal.chmod(0o400)
        directory.chmod(0o500)
        return
    if operation == "verify-one-inactive-version":
        values = document["inputs"]
        predecessor = command(["/usr/sbin/dkms", "status", "-m", "rp1-gpclk-dkms",
                               "-v", values["predecessorVersion"]], accepted=(0, 3))
        successor = command(["/usr/sbin/dkms", "status", "-m", "rp1-gpclk-dkms",
                             "-v", values["candidateRelease"]], accepted=(0, 3))
        if not predecessor.strip() or successor.strip():
            raise ValueError("recovery did not establish one inactive predecessor")
        if rooted(root, "/sys/module/rp1_gpclk_dkms").exists() or rooted(root, "/dev/rp1-gpclk").exists():
            raise ValueError("runtime remains after subordinate recovery")
        return
    if operation == "remove-attempt-residue":
        if staging.is_symlink() or not staging.is_dir():
            raise ValueError("attempt staging identity differs")
        for path in staging.rglob("*"):
            if path.is_symlink():
                raise ValueError("symlink in attempt staging")
        shutil.rmtree(staging)
        return
    if operation == "audit-residue" and document.get("schemaVersion") == 2:
        try:
            os.lstat(staging)
        except FileNotFoundError:
            pass
        except PermissionError as error:
            raise ValueError("attempt staging absence is not observable") from error
        else:
            raise ValueError("attempt staging residue remains")
    if operation == "seal-evidence":
        return
    marker = evidence / f"{operation}.json"
    if marker.exists() or marker.is_symlink():
        raise ValueError("internal operation marker already exists")
    atomic_json(marker, {"operation": operation, "operationId": document["operationId"],
                         "liveOutput": False})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("validate", "plan", "execute", "bootstrap", "pre-root-bootstrap"))
    parser.add_argument("document", type=pathlib.Path)
    parser.add_argument("--index", type=pathlib.Path)
    parser.add_argument("--instance", type=pathlib.Path)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--recover-from", type=pathlib.Path)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--envelope-sha256")
    args = parser.parse_args()
    document = load_json(args.document)
    if args.action == "pre-root-bootstrap":
        if not SHA256.fullmatch(args.envelope_sha256 or "") or digest(args.document) != args.envelope_sha256:
            raise SystemExit("pre-root envelope identity differs")
        executor = document.get("stagedExecutor", {})
        module_identity = document.get("preRootModule", {})
        current = pathlib.Path(__file__).resolve()
        if (current != pathlib.Path(executor.get("path", "")).resolve() or
                current.is_symlink() or digest(current) != executor.get("sha256")):
            raise SystemExit("staged pre-root executor identity differs")
        module_path = pathlib.Path(module_identity.get("path", ""))
        if module_path.is_symlink() or not module_path.is_file():
            raise SystemExit("pre-root module is absent or symlinked")
        payload = module_path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != module_identity.get("sha256"):
            raise SystemExit("pre-root module bytes differ")
        module = types.ModuleType("gate_d_preroot_authenticated")
        module.__file__ = str(module_path)
        exec(compile(payload, str(module_path), "exec"), module.__dict__)
        module.validate(document)
        if not args.execute:
            print(json.dumps({"valid": True, "readOnly": True, "outputDisabled": True}, indent=2, sort_keys=True)); return
        if os.geteuid() != 0:
            raise SystemExit("pre-root bootstrap execution requires root and --execute")
        def pre_root_probe() -> dict:
            overlays = subprocess.run(["/usr/bin/dtoverlay", "-l"], stdout=subprocess.PIPE, text=True, check=False, env=FIXED_ENV).stdout
            dkms = subprocess.run(["/usr/sbin/dkms", "status"], stdout=subprocess.PIPE, text=True, check=False, env=FIXED_ENV).stdout
            return {"moduleLoaded": pathlib.Path("/sys/module/rp1_gpclk_dkms").exists(),
                    "endpointPresent": pathlib.Path("/dev/rp1-gpclk").exists(),
                    "overlayActive": "rp1-gpclk" in overlays,
                    "dkmsTestVersions": "rp1-gpclk-dkms/" in dkms, "liveOutput": False}
        def pre_root_runner(argv: list[str]) -> None:
            subprocess.run(argv, stdin=subprocess.DEVNULL, check=True,
                           timeout=document["deadlineSeconds"], env=FIXED_ENV)
        result = module.execute(document, prefix=pathlib.Path("/"), runner=pre_root_runner,
                                probe=pre_root_probe, recover=args.resume)
        print(json.dumps(result, indent=2, sort_keys=True)); return
    trust_bootstrapped = False
    if args.instance is not None:
        bootstrap_root_validator(args.instance)
        trust_bootstrapped = True
    if args.action == "bootstrap":
        scripts=pathlib.Path(__file__).resolve().parent
        if str(scripts) not in sys.path: sys.path.insert(0,str(scripts))
        from gate_d_bootstrap import execute as execute_bootstrap, validate as validate_bootstrap
        if not args.execute:
            print(json.dumps(validate_bootstrap(document),indent=2,sort_keys=True)); return
        if os.geteuid()!=0 or args.instance is None: raise SystemExit("bootstrap execution requires root, --execute, and --instance")
        if not trust_bootstrapped: bootstrap_root_validator(args.instance)
        from gate_d_instance import load as load_instance, validate as validate_instance
        instance=load_instance(args.instance); validate_instance(instance,require_ready=True)
        qualification_root=instance.get("qualificationRoot")
        identity_root=pathlib.Path(__file__).resolve().parents[1]
        if qualification_root:
            from gate_d_root import validate as validate_root
            identity_root=validate_root(qualification_root)
            if document.get("qualificationRoot")!=qualification_root:
                raise SystemExit("bootstrap and execution-instance qualification roots differ")
        bootstrap_path=instance["executionPolicy"].get("qualificationBootstrap")
        bootstrap_sha=instance["executionPolicy"].get("qualificationBootstrapSha256")
        if (bootstrap_path is None or bootstrap_sha is None or
                args.document.resolve()!=((identity_root/bootstrap_path).resolve()) or
                digest(args.document)!=bootstrap_sha):
            raise SystemExit("bootstrap plan differs from the sealed execution instance")
        def probe() -> dict:
            overlays=subprocess.run(["/usr/bin/dtoverlay","-l"],stdout=subprocess.PIPE,text=True,check=False,env=FIXED_ENV).stdout
            dkms=subprocess.run(["/usr/sbin/dkms","status"],stdout=subprocess.PIPE,text=True,check=False,env=FIXED_ENV).stdout
            return {"moduleLoaded":pathlib.Path("/sys/module/rp1_gpclk_dkms").exists(),"endpointPresent":pathlib.Path("/dev/rp1-gpclk").exists(),"overlayActive":"rp1-gpclk" in overlays,"dkmsTestVersions":"rp1-gpclk-dkms/" in dkms,"liveOutput":False}
        def run_bootstrap(argv:list[str])->None:
            subprocess.run(argv,stdin=subprocess.DEVNULL,check=True,timeout=document["deadlineSeconds"],env=FIXED_ENV)
        result=execute_bootstrap(document,root=pathlib.Path("/"),runner=run_bootstrap,probe=probe,recover=args.resume)
        print(json.dumps(result,indent=2,sort_keys=True)); return
    validate_document(document)
    if args.action == "validate":
        result = {"valid": True, "readOnly": True, "operationId": document["operationId"]}
    elif args.action == "plan":
        result = {"operationId": document["operationId"], "readOnly": True,
                  "actions": ClosedDispatcher(document).plan()}
    else:
        if not args.execute or os.geteuid() != 0 or args.index is None or args.instance is None:
            raise SystemExit("target execution requires root, --execute, --index, and --instance")
        if not trust_bootstrapped: bootstrap_root_validator(args.instance)
        scripts = pathlib.Path(__file__).resolve().parent
        if str(scripts) not in sys.path:
            sys.path.insert(0, str(scripts))
        from gate_d_attempts import validate_index
        from gate_d_instance import load as load_instance, validate as validate_instance
        index_result = validate_index(args.index)
        instance = load_instance(args.instance)
        validate_instance(instance, require_ready=True)
        index_hash = digest(args.index)
        policy = instance["executionPolicy"]
        if index_hash != policy["attemptIndexSha256"]:
            raise SystemExit("attempt index differs from the sealed execution instance")
        records = {item["operationId"]: item for item in load_json(args.index)["attempts"]}
        record = records.get(document["operationId"])
        expected_path = args.index.parent / record["file"] if record else None
        if (record is None or args.document.resolve() != expected_path.resolve() or
                args.document.is_symlink() or digest(args.document) != record["sha256"]):
            raise SystemExit("attempt document is not the exact indexed file")
        def target_internal(operation: str, target_document: dict, target_root: pathlib.Path) -> None:
            default_internal(operation, target_document, target_root)
            if operation == "stage-source":
                staging = rooted(target_root, target_document["inputs"]["stagingDirectory"])
                atomic_json(staging / "execution-instance.json", instance)
        result = execute(document, document_sha256=digest(args.document),
                         index_sha256=index_hash, root=pathlib.Path("/"),
                         runner=Runner(), internal=target_internal,
                         recover_from=args.recover_from, resume=args.resume)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
