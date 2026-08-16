#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""One-shot authenticated transition into the Gate D qualification root."""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import shutil
import stat
from datetime import datetime, timezone
from typing import Callable

SHA256 = __import__("re").compile(r"[0-9a-f]{64}")
COMMIT = __import__("re").compile(r"[0-9a-f]{40}")
CHECKPOINTS = ("preflight", "create-root", "install", "cleanup-runtime",
               "copy-control-set", "verify-transition", "commit")


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rooted(prefix: pathlib.Path, absolute: str) -> pathlib.Path:
    pure = pathlib.PurePosixPath(absolute)
    if not pure.is_absolute() or ".." in pure.parts:
        raise ValueError("unsafe pre-root absolute path")
    current = prefix
    for part in pure.parts[1:]:
        current /= part
        if current.exists() and current.is_symlink():
            raise ValueError("symlink in pre-root controlled path")
    return current


def atomic_json(path: pathlib.Path, value: dict) -> None:
    if path.is_symlink():
        raise ValueError("pre-root journal is symlinked")
    path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("x", encoding="utf-8") as output:
        json.dump(value, output, indent=2, sort_keys=True)
        output.write("\n")
        output.flush()
        os.fsync(output.fileno())
    os.replace(temporary, path)


def validate(value: dict) -> dict:
    required = {"SPDX-License-Identifier", "schemaVersion", "kind", "operationId",
                "candidate", "proposedRoot", "stagedExecutor", "preRootModule", "administrator", "qualificationIdentity",
                "inputFiles", "transitionFiles", "installedTools", "argv",
                "cleanupArgv", "recoveryArgv", "journal", "cleanupPaths",
                "deadlineSeconds", "expectedPreState", "expectedPostState", "safety"}
    if (not isinstance(value, dict) or set(value) != required or
            value.get("SPDX-License-Identifier") != "MIT" or value.get("schemaVersion") != 1 or
            value.get("kind") != "gate-d-pre-root-bootstrap-envelope"):
        raise ValueError("invalid pre-root envelope identity")
    candidate = value["candidate"]
    if (not isinstance(candidate, dict) or set(candidate) != {"release", "sourceCommit", "archivePath", "archiveSha256"} or
            not COMMIT.fullmatch(candidate.get("sourceCommit", "")) or
            not SHA256.fullmatch(candidate.get("archiveSha256", ""))):
        raise ValueError("invalid pre-root candidate")
    root = value["proposedRoot"]
    if (not isinstance(root, dict) or set(root) != {"path", "ownerUid", "mode", "marker", "markerSha256"} or
            root.get("mode") != "0700" or type(root.get("ownerUid")) is not int or root["ownerUid"] < 0 or
            not SHA256.fullmatch(root.get("markerSha256", ""))):
        raise ValueError("invalid proposed qualification root")
    marker = root.get("marker")
    if (not isinstance(marker, dict) or set(marker) != {"SPDX-License-Identifier", "schemaVersion", "kind", "rootPath", "candidateRelease", "sourceCommit"} or
            marker.get("SPDX-License-Identifier") != "MIT" or marker.get("schemaVersion") != 1 or
            marker.get("kind") != "gate-d-qualification-root-identity" or marker.get("rootPath") != root["path"] or
            marker.get("candidateRelease") != candidate["release"] or marker.get("sourceCommit") != candidate["sourceCommit"]):
        raise ValueError("invalid proposed root marker")
    marker_bytes = (json.dumps(marker, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if hashlib.sha256(marker_bytes).hexdigest() != root["markerSha256"]:
        raise ValueError("proposed root marker hash differs")
    identity_keys = {"path", "sha256"}
    for field in ("stagedExecutor", "preRootModule", "administrator", "qualificationIdentity"):
        item = value[field]
        if not isinstance(item, dict) or set(item) != identity_keys or not SHA256.fullmatch(item.get("sha256", "")):
            raise ValueError(f"invalid {field} identity")
    for field in ("inputFiles", "installedTools"):
        records = value[field]
        if not isinstance(records, list) or not records:
            raise ValueError(f"{field} is empty")
        paths = []
        for item in records:
            if not isinstance(item, dict) or set(item) != identity_keys or not SHA256.fullmatch(item.get("sha256", "")):
                raise ValueError(f"invalid {field} identity")
            paths.append(item["path"])
        if len(paths) != len(set(paths)):
            raise ValueError(f"duplicate {field} path")
    transitions = value["transitionFiles"]
    destinations = []
    if not isinstance(transitions, list) or not transitions:
        raise ValueError("transition files are empty")
    input_paths = {item["path"]: item["sha256"] for item in value["inputFiles"]}
    for item in (candidate, value["administrator"], value["qualificationIdentity"]):
        path = item["archivePath"] if item is candidate else item["path"]
        expected = item["archiveSha256"] if item is candidate else item["sha256"]
        if input_paths.get(path) != expected:
            raise ValueError("pre-root primary input is not bound")
    for item in transitions:
        if (not isinstance(item, dict) or set(item) != {"sourcePath", "destination", "sha256", "mode"} or
                item.get("sourcePath") not in input_paths or input_paths[item["sourcePath"]] != item.get("sha256") or
                pathlib.PurePosixPath(item.get("destination", "")).is_absolute() or
                ".." in pathlib.PurePosixPath(item.get("destination", "")).parts or
                item.get("mode") not in {"0400", "0444"}):
            raise ValueError("invalid transition-file identity")
        destinations.append(item["destination"])
    if len(destinations) != len(set(destinations)):
        raise ValueError("duplicate transition destination")
    for field in ("argv", "cleanupArgv", "recoveryArgv"):
        argv = value[field]
        if not isinstance(argv, list) or not argv or not all(isinstance(x, str) and x for x in argv):
            raise ValueError(f"invalid {field}")
        if any(token in " ".join(argv) for token in ("live_output=1", "/dev/mem", "--force")):
            raise ValueError(f"prohibited {field}")
    expected_install_prefix = ["/usr/bin/python3", value["administrator"]["path"], "install", "--execute"]
    if (value["argv"][:4] != expected_install_prefix or
            "--qualification-install" not in value["argv"] or
            value["qualificationIdentity"]["path"] not in value["argv"]):
        raise ValueError("pre-root install argv differs")
    if value["cleanupArgv"][:3] != ["/usr/libexec/rp1-gpclk-dkms/gate-d-lifecycle", "dispatch", "complete-removal"]:
        raise ValueError("pre-root cleanup argv differs")
    if value["recoveryArgv"] != ["/usr/bin/python3", value["administrator"]["path"], "recover", "--execute"]:
        raise ValueError("pre-root recovery argv differs")
    baseline = {"moduleLoaded": False, "endpointPresent": False, "overlayActive": False,
                "dkmsTestVersions": False, "liveOutput": False}
    safety = {"outputDisabled": True, "liveOutput": False, "gpioAccess": False,
              "clockEnabled": False, "dmaActive": False, "sdrActive": False, "rf": False}
    if value["expectedPreState"] != baseline or value["expectedPostState"] != baseline or value["safety"] != safety:
        raise ValueError("pre-root safety contract differs")
    if not isinstance(value["cleanupPaths"], list) or not value["cleanupPaths"] or not 1 <= value["deadlineSeconds"] <= 1800:
        raise ValueError("pre-root lifecycle is incomplete")
    absolute = [root["path"], value["stagedExecutor"]["path"], value["preRootModule"]["path"],
                value["journal"], candidate["archivePath"], *value["cleanupPaths"],
                *(item["path"] for item in value["inputFiles"]), *(item["path"] for item in value["installedTools"])]
    if any(not pathlib.PurePosixPath(path).is_absolute() or ".." in pathlib.PurePosixPath(path).parts for path in absolute):
        raise ValueError("pre-root path is not absolute and closed")
    return {"valid": True, "readOnly": True, "outputDisabled": True}


def execute(value: dict, *, prefix: pathlib.Path, runner: Callable[[list[str]], None],
            probe: Callable[[], dict], stop_after: str | None = None, recover: bool = False) -> dict:
    validate(value)
    root = rooted(prefix, value["proposedRoot"]["path"])
    journal = rooted(prefix, value["journal"])
    if recover:
        if journal.is_symlink() or not journal.is_file():
            raise ValueError("pre-root recovery journal is absent")
        old = json.loads(journal.read_text())
        if old.get("status") != "recovery-required" or old.get("liveOutput") is not False:
            raise ValueError("pre-root journal is not recoverable")
        runner(value["recoveryArgv"])
        if root.exists():
            marker = root / ".gate-d-root.json"
            if marker.is_symlink() or not marker.is_file() or digest(marker) != value["proposedRoot"]["markerSha256"]:
                raise ValueError("partial root identity differs during recovery")
            for item in reversed(value["transitionFiles"]):
                path = root / item["destination"]
                if path.exists() and not path.is_symlink() and digest(path) == item["sha256"]:
                    path.unlink()
            marker.unlink()
            for directory in sorted((p for p in root.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
                directory.rmdir()
            root.rmdir()
        journal.unlink()
    if journal.exists() or journal.is_symlink() or root.exists() or root.is_symlink():
        raise ValueError("pre-root transition is not fresh")
    parent = root.parent
    if (parent.is_symlink() or not parent.is_dir() or parent.stat().st_uid != value["proposedRoot"]["ownerUid"] or
            stat.S_IMODE(parent.stat().st_mode) & 0o022):
        raise ValueError("qualification-root parent is unsafe")
    for item in value["inputFiles"]:
        path = rooted(prefix, item["path"])
        if path.is_symlink() or not path.is_file() or digest(path) != item["sha256"]:
            raise ValueError("pre-root input identity differs")
    state = {"operationId": value["operationId"], "status": "in-progress", "checkpoint": "preflight", "liveOutput": False}
    atomic_json(journal, state)
    try:
        if probe() != value["expectedPreState"]:
            raise ValueError("pre-root baseline differs")
        for checkpoint in CHECKPOINTS[1:]:
            state["checkpoint"] = checkpoint
            atomic_json(journal, state)
            if checkpoint == "create-root":
                root.mkdir(mode=0o700)
                os.chown(root, value["proposedRoot"]["ownerUid"], -1)
                marker = root / ".gate-d-root.json"
                marker.write_text(json.dumps(value["proposedRoot"]["marker"], sort_keys=True, separators=(",", ":")) + "\n")
                marker.chmod(0o400)
            elif checkpoint == "install":
                runner(value["argv"])
            elif checkpoint == "cleanup-runtime":
                runner(value["cleanupArgv"])
            elif checkpoint == "copy-control-set":
                for item in value["transitionFiles"]:
                    source = rooted(prefix, item["sourcePath"])
                    destination = root / item["destination"]
                    destination.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
                    if destination.exists() or destination.is_symlink():
                        raise ValueError("transition destination already exists")
                    shutil.copyfile(source, destination)
                    destination.chmod(int(item["mode"], 8))
            elif checkpoint == "verify-transition":
                metadata = root.stat()
                marker = root / ".gate-d-root.json"
                if (root.is_symlink() or metadata.st_uid != value["proposedRoot"]["ownerUid"] or
                        stat.S_IMODE(metadata.st_mode) != 0o700 or marker.is_symlink() or
                        not marker.is_file() or digest(marker) != value["proposedRoot"]["markerSha256"]):
                    raise ValueError("committed qualification-root identity differs")
                if probe() != value["expectedPostState"]:
                    raise ValueError("pre-root post-state differs")
                for item in value["installedTools"]:
                    path = rooted(prefix, item["path"])
                    if path.is_symlink() or not path.is_file() or digest(path) != item["sha256"]:
                        raise ValueError("installed transition tool differs")
                for item in value["transitionFiles"]:
                    path = root / item["destination"]
                    if path.is_symlink() or not path.is_file() or digest(path) != item["sha256"]:
                        raise ValueError("root-bound control document differs")
                for raw in value["cleanupPaths"]:
                    residue = rooted(prefix, raw)
                    if residue.exists() or residue.is_symlink():
                        raise ValueError("pre-root cleanup residue remains")
            if stop_after == checkpoint:
                raise InterruptedError(checkpoint)
        state.update(status="complete", completedAt=datetime.now(timezone.utc).isoformat())
        atomic_json(journal, state)
        return state
    except BaseException as error:
        state.update(status="recovery-required", failure=type(error).__name__)
        atomic_json(journal, state)
        raise
