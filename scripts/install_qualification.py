#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Install or remove qualification tooling without touching the DKMS product."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import shutil
import subprocess

PACKAGE = "rp1-gpclk-dkms"
RELEASE = "0.0.0-phase5.53"
LEDGER = "/var/lib/rp1-gpclk-dkms/qualification.json"


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rooted(root: pathlib.Path, raw: str) -> pathlib.Path:
    pure = pathlib.PurePosixPath(raw)
    if not pure.is_absolute() or ".." in pure.parts:
        raise ValueError("unsafe qualification destination")
    path = root.joinpath(*pure.parts[1:])
    current = root
    for part in pure.parts[1:]:
        current /= part
        if current.is_symlink():
            raise ValueError(f"symlink in qualification destination: {raw}")
    return path


def confined(root: pathlib.Path, raw: str) -> pathlib.Path:
    """Recover an absolute ledger path only when it remains below root."""
    path = pathlib.Path(raw)
    if not path.is_absolute():
        raise ValueError("qualification ledger path is not absolute")
    try:
        path.relative_to(root)
    except ValueError as error:
        raise ValueError("qualification ledger path escapes root") from error
    current = root
    for part in path.relative_to(root).parts:
        current /= part
        if current.is_symlink():
            raise ValueError(f"symlink in qualification ledger path: {path}")
    return path


def atomic_json(path: pathlib.Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("x", encoding="utf-8") as output:
        json.dump(value, output, indent=2, sort_keys=True)
        output.write("\n")
        output.flush()
        os.fsync(output.fileno())
    os.replace(temporary, path)
    path.chmod(0o600)


def load_layout(source: pathlib.Path) -> dict:
    path = source / "release/qualification-layout-v1.json"
    if path.is_symlink() or not path.is_file():
        raise ValueError("qualification layout is absent or unsafe")
    value = json.loads(path.read_text())
    if (value.get("package") != f"{PACKAGE}-qualification" or
            value.get("release") != RELEASE or not isinstance(value.get("artifacts"), list)):
        raise ValueError("qualification layout identity differs")
    destinations = [item.get("destination") for item in value["artifacts"]]
    if len(destinations) != len(set(destinations)):
        raise ValueError("qualification destinations are ambiguous")
    required = {"id", "kind", "path", "destination", "owner", "group",
                "mode", "replacement", "removalOwner"}
    ids = []
    for item in value["artifacts"]:
        source_path = pathlib.PurePosixPath(item.get("path", ""))
        if (set(item) != required or item.get("kind") not in {"archive", "installed-build"} or
                item.get("owner") != "root" or item.get("group") != "root" or
                item.get("mode") not in {"0644", "0755"} or source_path.is_absolute() or
                not source_path.parts or ".." in source_path.parts):
            raise ValueError("qualification layout artifact is unsafe")
        rooted(pathlib.Path("/"), item["destination"])
        ids.append(item["id"])
    if len(ids) != len(set(ids)):
        raise ValueError("qualification artifact identities are ambiguous")
    return value


def install(source: pathlib.Path, root: pathlib.Path, *, runner=subprocess.run) -> dict:
    if source.is_symlink() or not source.is_dir():
        raise ValueError("qualification source must be a real directory")
    ledger = rooted(root, LEDGER)
    if ledger.exists() or ledger.is_symlink():
        raise ValueError("qualification ledger already exists")
    layout = load_layout(source)
    state = {"SPDX-License-Identifier": "MIT", "schemaVersion": 1,
             "kind": "rp1-gpclk-dkms-qualification-installation",
             "release": RELEASE, "status": "installing", "liveOutput": False,
             "productMutation": False, "ownedFiles": [], "ownedDirectories": [],
             "commands": []}
    atomic_json(ledger, state)
    try:
        for item in layout["artifacts"]:
            if item["kind"] not in {"archive", "archive-tree"}:
                continue
            origin = source / item["path"]
            destination = rooted(root, item["destination"])
            if origin.is_symlink() or not origin.is_file():
                raise ValueError(f"qualification source is absent or unsafe: {item['path']}")
            if destination.exists() or destination.is_symlink():
                raise ValueError(f"qualification destination already exists: {item['destination']}")
            missing = []
            parent = destination.parent
            while parent != root and not parent.exists():
                missing.append(parent)
                parent = parent.parent
            destination.parent.mkdir(parents=True, exist_ok=True)
            for directory in reversed(missing):
                directory.chmod(0o755)
                state["ownedDirectories"].append(str(directory))
            shutil.copyfile(origin, destination)
            destination.chmod(int(item["mode"], 8))
            state["ownedFiles"].append({"path": str(destination),
                                         "sha256": digest(destination)})
            atomic_json(ledger, state)
        include = rooted(root, f"/usr/src/{PACKAGE}-{RELEASE}/include/uapi")
        uapi = include / "linux/rp1_gpclk.h"
        if uapi.is_symlink() or not uapi.is_file():
            raise ValueError("installed product UAPI is absent or unsafe")
        builds = {
            "gate-d-uapi-probe": ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                                  f"-I{include}", str(source / "tools/gate_d_uapi_probe.c")],
            "gate-d-busy-injector": ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                                     f"-I{include}", str(source / "tools/gate_d_busy_injector.c")],
        }
        by_id = {item["id"]: item for item in layout["artifacts"]}
        for identity, command in builds.items():
            item = by_id[identity]
            destination = rooted(root, item["destination"])
            if destination.exists() or destination.is_symlink():
                raise ValueError(f"qualification build destination exists: {item['destination']}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary = destination.with_name(f".{destination.name}.{os.getpid()}.installing")
            if temporary.exists() or temporary.is_symlink():
                raise ValueError(f"qualification temporary build destination exists: {temporary}")
            state["pendingBuild"] = {"temporary": str(temporary),
                                     "destination": str(destination)}
            argv = [*command, "-o", str(temporary)]
            state["commands"].append(argv)
            atomic_json(ledger, state)
            runner(argv, check=True, stdin=subprocess.DEVNULL,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                   env={"PATH": "/usr/bin:/bin"})
            if temporary.is_symlink() or not temporary.is_file():
                raise ValueError("qualification build produced no real output")
            temporary.chmod(0o755)
            state["pendingBuild"]["sha256"] = digest(temporary)
            atomic_json(ledger, state)
            os.replace(temporary, destination)
            state["ownedFiles"].append({"path": str(destination),
                                         "sha256": digest(destination)})
            del state["pendingBuild"]
            atomic_json(ledger, state)
        state.update({"status": "complete", "recoveryRequired": False})
        atomic_json(ledger, state)
        return state
    except BaseException:
        state.update({"status": "recovery-required", "recoveryRequired": True})
        atomic_json(ledger, state)
        raise


def remove(root: pathlib.Path) -> dict:
    ledger = rooted(root, LEDGER)
    if ledger.is_symlink() or not ledger.is_file():
        raise ValueError("qualification ledger is absent or unsafe")
    state = json.loads(ledger.read_text())
    if state.get("status") not in {"complete", "recovery-required"}:
        raise ValueError("qualification state is not removable")
    pending = state.get("pendingBuild")
    if pending is not None:
        if not isinstance(pending, dict) or set(pending) not in ({"temporary", "destination"},
                                                                 {"temporary", "destination", "sha256"}):
            raise ValueError("qualification pending build state is unsafe")
        temporary = confined(root, pending["temporary"])
        destination = confined(root, pending["destination"])
        if destination.exists() or destination.is_symlink():
            if (destination.is_symlink() or not destination.is_file() or
                    "sha256" not in pending or digest(destination) != pending["sha256"]):
                raise ValueError(f"qualification pending destination differs: {destination}")
            destination.unlink()
        if temporary.exists() or temporary.is_symlink():
            if temporary.is_symlink() or not temporary.is_file():
                raise ValueError(f"qualification pending output is unsafe: {temporary}")
            if "sha256" in pending and digest(temporary) != pending["sha256"]:
                raise ValueError(f"qualification pending output differs: {temporary}")
            temporary.unlink()
    for item in reversed(state.get("ownedFiles", [])):
        path = confined(root, item["path"])
        if path.is_symlink() or not path.is_file() or digest(path) != item["sha256"]:
            raise ValueError(f"qualification-owned file differs: {path}")
        path.unlink()
    for raw in reversed(state.get("ownedDirectories", [])):
        path = confined(root, raw)
        try:
            path.rmdir()
        except OSError:
            pass
    state.update({"status": "removed", "recoveryRequired": False})
    atomic_json(ledger, state)
    return state


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("install", "remove", "status"))
    parser.add_argument("--source", type=pathlib.Path)
    parser.add_argument("--root", type=pathlib.Path, default=pathlib.Path("/"))
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    ledger = rooted(root, LEDGER)
    if args.action == "status":
        value = json.loads(ledger.read_text()) if ledger.is_file() and not ledger.is_symlink() else {"status": "absent"}
        value["readOnly"] = True
    else:
        if not args.execute or (root == pathlib.Path("/") and os.geteuid() != 0):
            raise SystemExit("qualification mutation requires --execute and root on the real system")
        if args.action == "install":
            if args.source is None:
                raise SystemExit("qualification install requires --source")
            value = install(args.source.resolve(), root)
        else:
            value = remove(root)
    print(json.dumps(value, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
