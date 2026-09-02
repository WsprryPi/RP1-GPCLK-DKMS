#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Fail-closed stock-kernel selector for an authorized Gate D reboot.

Planning and status are read-only.  ``select`` and ``restore`` require root and
``--execute``.  They operate only on digest-bound files named by a sealed boot
operation, never on tryboot.txt or historical kernel artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import tempfile
import platform

SHA_LEN = 64
MARKER_BEGIN = "# BEGIN RP1-GPCLK-DKMS GATE-D TEST-OWNED"
MARKER_END = "# END RP1-GPCLK-DKMS GATE-D TEST-OWNED"


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: pathlib.Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError("boot operation must be a real file")
    value = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "schemaVersion", "operationId", "targetKernel", "sourceKernel",
        "sourceKernelSha256", "sourceInitramfs", "sourceInitramfsSha256",
        "config", "configSha256", "tryboot", "trybootSha256",
        "stagedKernel", "stagedInitramfs", "backupConfig", "state",
    }
    if not isinstance(value, dict) or set(value) != required or value["schemaVersion"] != 1:
        raise ValueError("boot operation fields are incomplete or unknown")
    for field in ("operationId", "targetKernel"):
        if not isinstance(value[field], str) or not value[field]:
            raise ValueError(f"invalid {field}")
    for field in ("sourceKernel", "sourceInitramfs", "config", "tryboot",
                  "stagedKernel", "stagedInitramfs", "backupConfig", "state"):
        item = value[field]
        if not isinstance(item, str) or not item.startswith("/") or ".." in pathlib.PurePosixPath(item).parts:
            raise ValueError(f"unsafe {field}")
    for field in ("sourceKernelSha256", "sourceInitramfsSha256", "configSha256", "trybootSha256"):
        item = value[field]
        if not isinstance(item, str) or len(item) != SHA_LEN or any(c not in "0123456789abcdef" for c in item):
            raise ValueError(f"invalid {field}")
    if pathlib.PurePosixPath(value["tryboot"]).name != "tryboot.txt":
        raise ValueError("tryboot identity must be explicit")
    if not pathlib.PurePosixPath(value["stagedKernel"]).name.startswith("gate-d-stock-"):
        raise ValueError("staged kernel is not test-owned")
    if not pathlib.PurePosixPath(value["stagedInitramfs"]).name.startswith("gate-d-stock-"):
        raise ValueError("staged initramfs is not test-owned")
    return value


def rooted(root: pathlib.Path, absolute: str) -> pathlib.Path:
    result = root / absolute.lstrip("/")
    current = root
    for part in pathlib.PurePosixPath(absolute).parts[1:]:
        current /= part
        if current.is_symlink():
            raise ValueError(f"symlink in boot path: {absolute}")
    return result


def atomic_bytes(path: pathlib.Path, data: bytes, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp = pathlib.Path(temporary)
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        os.chmod(temp, mode)
        os.replace(temp, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        temp.unlink(missing_ok=True)


def verified(path: pathlib.Path, expected: str, label: str) -> None:
    if path.is_symlink() or not path.is_file() or digest(path) != expected:
        raise ValueError(f"{label} identity differs")


def plan(spec: dict) -> dict:
    return {
        "operationId": spec["operationId"], "targetKernel": spec["targetKernel"],
        "actions": ["verify-current-config-and-tryboot", "verify-versioned-stock-artifacts",
                    "copy-test-owned-kernel-and-initramfs", "write-exact-config-backup",
                    "atomically-append-test-owned-selection", "operator-notice", "reboot",
                    "verify-target-kernel", "restore-config-by-digest", "remove-test-owned-artifacts",
                    "operator-notice", "reboot", "verify-original-kernel"],
        "trybootMutation": False, "historicalArtifactMutation": False,
        "outputActive": False, "readOnly": True,
    }


def select(spec: dict, root: pathlib.Path) -> dict:
    config = rooted(root, spec["config"])
    tryboot = rooted(root, spec["tryboot"])
    source_kernel = rooted(root, spec["sourceKernel"])
    source_initramfs = rooted(root, spec["sourceInitramfs"])
    staged_kernel = rooted(root, spec["stagedKernel"])
    staged_initramfs = rooted(root, spec["stagedInitramfs"])
    backup = rooted(root, spec["backupConfig"])
    state = rooted(root, spec["state"])
    for path in (staged_kernel, staged_initramfs, backup, state):
        if path.exists() or path.is_symlink():
            raise ValueError(f"test-owned boot path already exists: {path}")
    verified(config, spec["configSha256"], "config")
    verified(tryboot, spec["trybootSha256"], "tryboot")
    verified(source_kernel, spec["sourceKernelSha256"], "source kernel")
    verified(source_initramfs, spec["sourceInitramfsSha256"], "source initramfs")
    original = config.read_bytes()
    if MARKER_BEGIN.encode() in original or MARKER_END.encode() in original:
        raise ValueError("Gate D boot marker already exists")
    record = {
        "schemaVersion": 1, "operationId": spec["operationId"], "status": "staging-recovery-required",
        "checkpoint": "journal-created", "targetKernel": spec["targetKernel"],
        "originalConfigSha256": spec["configSha256"], "backupConfigSha256": spec["configSha256"],
        "stagedKernelSha256": spec["sourceKernelSha256"],
        "stagedInitramfsSha256": spec["sourceInitramfsSha256"],
        "trybootSha256": digest(tryboot), "outputActive": False,
    }
    atomic_bytes(state, (json.dumps(record, indent=2, sort_keys=True) + "\n").encode(), 0o600)
    atomic_bytes(backup, original, 0o600)
    record["checkpoint"] = "backup-config"
    atomic_bytes(state, (json.dumps(record, indent=2, sort_keys=True) + "\n").encode(), 0o600)
    atomic_bytes(staged_kernel, source_kernel.read_bytes(), 0o644)
    record["checkpoint"] = "stage-kernel"
    atomic_bytes(state, (json.dumps(record, indent=2, sort_keys=True) + "\n").encode(), 0o600)
    atomic_bytes(staged_initramfs, source_initramfs.read_bytes(), 0o644)
    record["checkpoint"] = "stage-initramfs"
    atomic_bytes(state, (json.dumps(record, indent=2, sort_keys=True) + "\n").encode(), 0o600)
    kernel_hash = digest(staged_kernel)
    initramfs_hash = digest(staged_initramfs)
    suffix = ("\n" if original and not original.endswith(b"\n") else "") + (
        f"{MARKER_BEGIN}\n[all]\nauto_initramfs=0\n"
        f"kernel={staged_kernel.name}\n"
        f"initramfs {staged_initramfs.name} followkernel\n{MARKER_END}\n"
    )
    selected = original + suffix.encode("ascii")
    atomic_bytes(config, selected, 0o644)
    record.update({"status": "selected-reboot-required", "checkpoint": "select-config",
                   "selectedConfigSha256": digest(config),
                   "stagedKernelSha256": kernel_hash, "stagedInitramfsSha256": initramfs_hash})
    atomic_bytes(state, (json.dumps(record, indent=2, sort_keys=True) + "\n").encode(), 0o600)
    return record


def restore(spec: dict, root: pathlib.Path) -> dict:
    config = rooted(root, spec["config"])
    tryboot = rooted(root, spec["tryboot"])
    staged_kernel = rooted(root, spec["stagedKernel"])
    staged_initramfs = rooted(root, spec["stagedInitramfs"])
    backup = rooted(root, spec["backupConfig"])
    state_path = rooted(root, spec["state"])
    if state_path.is_symlink() or not state_path.is_file():
        raise ValueError("boot selection state is absent")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if state.get("operationId") != spec["operationId"] or state.get("status") not in {
            "staging-recovery-required", "selected-reboot-required", "restoring-recovery-required"}:
        raise ValueError("boot selection state is not restorable")
    verified(tryboot, spec["trybootSha256"], "tryboot")
    current_config = digest(config) if config.is_file() and not config.is_symlink() else None
    selected_hash = state.get("selectedConfigSha256")
    if current_config == selected_hash:
        verified(backup, state["backupConfigSha256"], "config backup")
        state.update({"status": "restoring-recovery-required", "checkpoint": "restore-config"})
        atomic_bytes(state_path, (json.dumps(state, indent=2, sort_keys=True) + "\n").encode(), 0o600)
        atomic_bytes(config, backup.read_bytes(), 0o644)
    elif current_config != spec["configSha256"]:
        raise ValueError("config is neither selected nor original")
    elif backup.exists() or backup.is_symlink():
        verified(backup, state["backupConfigSha256"], "config backup")
    if digest(config) != spec["configSha256"]:
        raise ValueError("restored config identity differs")
    for path, field, label in ((staged_kernel, "stagedKernelSha256", "staged kernel"),
                               (staged_initramfs, "stagedInitramfsSha256", "staged initramfs")):
        if path.exists() or path.is_symlink():
            verified(path, state[field], label)
            path.unlink()
    state.update({"status": "restored-reboot-required", "checkpoint": "restore-complete",
                  "restoredConfigSha256": digest(config)})
    atomic_bytes(state_path, (json.dumps(state, indent=2, sort_keys=True) + "\n").encode(), 0o600)
    return state


def verify_running(expected: str, *, running: str | None = None) -> dict:
    actual = platform.release() if running is None else running
    if actual != expected:
        raise ValueError(f"running kernel differs: expected {expected}, got {actual}")
    return {"runningKernel": actual, "verified": True, "readOnly": True,
            "outputActive": False}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("validate", "plan", "select", "restore", "verify-running"))
    parser.add_argument("operation")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.action == "verify-running":
        result = verify_running(args.operation)
    elif args.action == "validate":
        spec = load(pathlib.Path(args.operation))
        result = {"valid": True, "readOnly": True, "operationId": spec["operationId"]}
    elif args.action == "plan":
        spec = load(pathlib.Path(args.operation))
        result = plan(spec)
    else:
        spec = load(pathlib.Path(args.operation))
        if not args.execute or os.geteuid() != 0:
            raise SystemExit("boot mutation requires root and --execute")
        result = select(spec, pathlib.Path("/")) if args.action == "select" else restore(spec, pathlib.Path("/"))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
