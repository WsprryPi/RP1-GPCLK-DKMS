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
CHECKPOINTS = ("preflight", "archive-prior-state", "create-root", "install", "cleanup-runtime",
               "copy-control-set", "verify-transition", "commit")
LEGACY_RELEASE_INPUT_ROLES = {
    "archive": None,
    "gpio4Dtbo": "rp1-gpclk-gpio4.dtbo",
    "gpio20Dtbo": "rp1-gpclk-gpio20.dtbo",
    "compatibilityManifest": "rp1-gpclk-compatibility-manifest.json",
    "provenance": "PROVENANCE.json",
    "releaseMetadata": "release-metadata.json",
    "checksums": "SHA256SUMS",
}
SPLIT_RELEASE_INPUT_ROLES = {
    **LEGACY_RELEASE_INPUT_ROLES,
    "qualificationArchive": None,
}


def release_input_roles(schema: int, release: str) -> dict[str, str]:
    roles = dict(SPLIT_RELEASE_INPUT_ROLES if schema in {6, 7} else LEGACY_RELEASE_INPUT_ROLES)
    roles["archive"] = f"rp1-gpclk-dkms-{release}.tar.gz"
    if schema in {6, 7}:
        roles["qualificationArchive"] = f"rp1-gpclk-dkms-qualification-{release}.tar.gz"
    return roles


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def validate_package_paths(items: object) -> list[dict]:
    if not isinstance(items,list) or not items: raise ValueError("typed package inventory is empty")
    paths=[]
    for item in items:
        common={"path","type","mode","ownerUid","groupGid"}
        if (not isinstance(item,dict) or item.get("type") not in {"file","symlink"} or
                not pathlib.PurePosixPath(item.get("path","")).is_absolute() or
                ".." in pathlib.PurePosixPath(item["path"]).parts or
                item.get("mode") not in {"0644","0755","0777"} or
                type(item.get("ownerUid")) is not int or item["ownerUid"]<0 or
                type(item.get("groupGid")) is not int or item["groupGid"]<0): raise ValueError("invalid typed package identity")
        if item["type"]=="file":
            if set(item)!=common|{"sha256"} or not SHA256.fullmatch(item.get("sha256","")) or item["mode"] not in {"0644","0755"}: raise ValueError("invalid typed package file")
        elif (set(item)!=common|{"target"} or not isinstance(item.get("target"),str) or not item["target"] or pathlib.PurePosixPath(item["target"]).is_absolute() or item["mode"] not in {"0755","0777"}): raise ValueError("invalid typed package symlink")
        paths.append(item["path"])
    if len(paths)!=len(set(paths)): raise ValueError("duplicate typed package path")
    return items
def package_paths_digest(items:list[dict])->str:
    return hashlib.sha256((json.dumps(items,sort_keys=True,separators=(",",":"))+"\n").encode()).hexdigest()

def verify_package_path(prefix:pathlib.Path,item:dict)->None:
    path=rooted_leaf(prefix,item["path"]); status=path.lstat()
    if status.st_uid!=item["ownerUid"] or status.st_gid!=item["groupGid"] or stat.S_IMODE(status.st_mode)!=int(item["mode"],8): raise ValueError("typed package metadata differs")
    if item["type"]=="file":
        if path.is_symlink() or not path.is_file() or digest(path)!=item["sha256"]: raise ValueError("typed package file differs")
    elif not path.is_symlink() or os.readlink(path)!=item["target"]: raise ValueError("typed package symlink differs")

def validate_removed_ledger(path:pathlib.Path,value:dict,prior:dict)->None:
    """Bind a schema-7 removed ledger to the captured predecessor inventory."""
    if path.is_symlink() or not path.is_file(): raise ValueError("removed predecessor ledger is absent")
    state=json.loads(path.read_text())
    candidate=value["candidate"]
    if (state.get("status")!="removed" or state.get("checkpoint")!="inactive-clean" or
            state.get("recoveryRequired") is not False or state.get("outputActive") is not False or
            state.get("package")!="rp1-gpclk-dkms" or state.get("release")!=candidate["release"] or
            state.get("predecessorRelease")!=candidate["release"]):
        raise ValueError("removed predecessor ledger state differs")
    expected={item["path"]:item for item in value["predecessorPackagePaths"]}
    actual={}
    for item in state.get("ownedFiles",[])+state.get("replacedFiles",[]):
        raw=item.get("path")
        if not isinstance(raw,str) or raw in actual: raise ValueError("removed predecessor inventory is ambiguous")
        if "symlink" in item: current={"type":"symlink","target":item["symlink"]}
        elif item.get("type")=="symlink": current={"type":"symlink","target":item.get("successorTarget")}
        else: current={"type":"file","sha256":item.get("successorSha256",item.get("sha256"))}
        actual[raw]=current
    if set(actual)!=set(expected): raise ValueError("removed predecessor inventory paths differ")
    for raw,current in actual.items():
        wanted=expected[raw]
        if current["type"]!=wanted["type"] or (current.get("sha256") or current.get("target"))!=(wanted.get("sha256") or wanted.get("target")):
            raise ValueError("removed predecessor inventory identity differs")
    if not SHA256.fullmatch(prior.get("sha256","")): raise ValueError("pre-removal ledger identity differs")


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

def rooted_leaf(prefix:pathlib.Path,absolute:str)->pathlib.Path:
    pure=pathlib.PurePosixPath(absolute)
    if not pure.is_absolute() or ".." in pure.parts or pure==pathlib.PurePosixPath("/"): raise ValueError("unsafe pre-root package path")
    return rooted(prefix,str(pure.parent))/pure.name


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
    schema = value.get("schemaVersion")
    if schema in {2, 3, 4, 5, 6, 7}:
        required.update({"releaseInputs", "administratorState"})
    if schema in {3, 4, 5, 6, 7}:
        required.add("priorTerminalState")
    if schema in {4, 5, 6, 7}:
        required.update({"installedPackagePaths","packagePathsSha256"})
    if schema in {5, 6, 7}:
        required.update({"liveTargetSnapshotSha256", "predecessorPackagePaths",
                         "predecessorPackagePathsSha256"})
    if (not isinstance(value, dict) or set(value) != required or
            value.get("SPDX-License-Identifier") != "MIT" or schema not in {1, 2, 3, 4, 5, 6, 7} or
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
    release_inputs = value.get("releaseInputs", [])
    expected_release_names = release_input_roles(schema, candidate["release"])
    if schema in {2, 3, 4, 5, 6, 7} and (not isinstance(release_inputs, list) or len(release_inputs) != len(expected_release_names)):
        raise ValueError("pre-root release-input graph is incomplete")
    roles = {}
    for item in release_inputs:
        if (not isinstance(item, dict) or set(item) != {"role", "path", "sha256"} or
                item.get("role") not in expected_release_names or
                pathlib.PurePosixPath(item.get("path", "")).name != expected_release_names[item["role"]] or
                not SHA256.fullmatch(item.get("sha256", "")) or
                input_paths.get(item["path"]) != item["sha256"]):
            raise ValueError("invalid pre-root release-input identity")
        roles[item["role"]] = item
    if schema in {2, 3, 4, 5, 6, 7} and (set(roles) != set(expected_release_names) or roles["archive"]["path"] != candidate["archivePath"]):
        raise ValueError("pre-root release-input graph differs")
    release_parent = pathlib.PurePosixPath(candidate["archivePath"]).parent
    if schema in {2, 3, 4, 5, 6, 7} and any(pathlib.PurePosixPath(item["path"]).parent != release_parent for item in release_inputs):
        raise ValueError("pre-root release inputs do not share the administrator release directory")
    administrator_state = value.get("administratorState", {
        "path": "/var/lib/rp1-gpclk-dkms/transaction.json",
        "absenceBeforeInvocation": True,
        "recoveryPolicy": "invoke-only-for-real-owned-state",
    })
    if (not isinstance(administrator_state, dict) or
            set(administrator_state) != {"path", "absenceBeforeInvocation", "recoveryPolicy"} or
            administrator_state.get("absenceBeforeInvocation") is not True or
            administrator_state.get("recoveryPolicy") != "invoke-only-for-real-owned-state" or
            not pathlib.PurePosixPath(administrator_state.get("path", "")).is_absolute() or
            ".." in pathlib.PurePosixPath(administrator_state["path"]).parts):
        raise ValueError("invalid administrator transaction-state contract")
    prior = value.get("priorTerminalState")
    if schema in {3, 4, 5, 6, 7}:
        prior_keys = {"path", "sha256", "status", "recoveryRequired", "outputActive",
                      "ownerUid", "mode", "archivePath", "archiveMode"}
        if (not isinstance(prior, dict) or set(prior) != prior_keys or
                prior.get("path") != administrator_state["path"] or
                not SHA256.fullmatch(prior.get("sha256", "")) or
                prior.get("status") not in ({"removed"} if schema == 7 else ({"complete"} if schema in {5, 6} else {"recovered"})) or prior.get("recoveryRequired") is not False or
                prior.get("outputActive") is not False or type(prior.get("ownerUid")) is not int or
                prior["ownerUid"] < 0 or prior.get("mode") != "0600" or
                prior.get("archiveMode") != "0400"):
            raise ValueError("invalid prior terminal administrator state")
        current = pathlib.PurePosixPath(prior["path"])
        archive = pathlib.PurePosixPath(prior.get("archivePath", ""))
        if (not archive.is_absolute() or ".." in archive.parts or archive == current or
                archive.parent.parent != current.parent):
            raise ValueError("invalid prior terminal archive path")
    if schema in {4, 5, 6, 7}:
        package_paths=validate_package_paths(value["installedPackagePaths"])
        if not SHA256.fullmatch(value.get("packagePathsSha256","")) or package_paths_digest(package_paths)!=value["packagePathsSha256"]: raise ValueError("typed package inventory digest differs")
        if not {item["path"] for item in value["installedTools"]}.issubset({item["path"] for item in package_paths}): raise ValueError("installed tools are outside typed package inventory")
    if schema in {5, 6, 7} and not SHA256.fullmatch(value.get("liveTargetSnapshotSha256", "")):
        raise ValueError("live-target snapshot identity differs")
    if schema in {5, 6, 7}:
        predecessor_paths = validate_package_paths(value["predecessorPackagePaths"])
        if (not SHA256.fullmatch(value.get("predecessorPackagePathsSha256", "")) or
                package_paths_digest(predecessor_paths) != value["predecessorPackagePathsSha256"]):
            raise ValueError("predecessor package inventory digest differs")
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
        if any(token in " ".join(argv) for token in ("output_inhibit=0", "/dev/mem", "--force")):
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
                "dkmsTestVersions": False, "outputActive": False}
    safety = {"outputDisabled": True, "outputActive": False, "gpioAccess": False,
              "clockEnabled": False, "dmaActive": False, "sdrActive": False, "rf": False}
    if value["expectedPreState"] != baseline or value["expectedPostState"] != baseline or value["safety"] != safety:
        raise ValueError("pre-root safety contract differs")
    if not isinstance(value["cleanupPaths"], list) or not value["cleanupPaths"] or not 1 <= value["deadlineSeconds"] <= 1800:
        raise ValueError("pre-root lifecycle is incomplete")
    absolute = [root["path"], value["stagedExecutor"]["path"], value["preRootModule"]["path"],
                value["journal"], administrator_state["path"], candidate["archivePath"], *value["cleanupPaths"],
                *(item["path"] for item in value["inputFiles"]), *(item["path"] for item in value["installedTools"])]
    if schema==4: absolute.extend(item["path"] for item in value["installedPackagePaths"])
    if prior is not None:
        absolute.append(prior["archivePath"])
    if any(not pathlib.PurePosixPath(path).is_absolute() or ".." in pathlib.PurePosixPath(path).parts for path in absolute):
        raise ValueError("pre-root path is not absolute and closed")
    return {"valid": True, "readOnly": True, "outputDisabled": True}


def validate_release_inputs(value: dict, *, prefix: pathlib.Path) -> None:
    records = {item["role"]: item for item in value["releaseInputs"]}
    paths = {}
    for role, item in records.items():
        path = rooted(prefix, item["path"])
        if path.is_symlink() or not path.is_file() or digest(path) != item["sha256"]:
            raise ValueError(f"pre-root release input differs: {role}")
        paths[role] = path
    lines = paths["checksums"].read_text(encoding="utf-8").splitlines()
    checksums = {}
    for line in lines:
        parts = line.split("  ", 1)
        if len(parts) != 2 or not SHA256.fullmatch(parts[0]) or pathlib.PurePosixPath(parts[1]).name != parts[1]:
            raise ValueError("invalid staged SHA256SUMS entry")
        if parts[1] in checksums:
            raise ValueError("duplicate staged SHA256SUMS entry")
        checksums[parts[1]] = parts[0]
    role_names = release_input_roles(value["schemaVersion"], value["candidate"]["release"])
    expected = {paths[role].name for role in role_names if role != "checksums"}
    if set(checksums) != expected:
        raise ValueError("staged SHA256SUMS membership differs")
    for role in role_names:
        name = paths[role].name
        if role != "checksums" and checksums[name] != records[role]["sha256"]:
            raise ValueError(f"staged SHA256SUMS hash differs: {role}")


def validate_partial_root(value: dict, root: pathlib.Path) -> None:
    if not root.exists():
        return
    marker = root / ".gate-d-root.json"
    if (root.is_symlink() or not root.is_dir() or marker.is_symlink() or not marker.is_file() or
            digest(marker) != value["proposedRoot"]["markerSha256"]):
        raise ValueError("partial root identity differs during recovery")
    allowed_files = {marker}
    allowed_directories = {root}
    for item in value["transitionFiles"]:
        path = root / item["destination"]
        current = path.parent
        while current != root:
            allowed_directories.add(current); current = current.parent
        if path.exists() or path.is_symlink():
            if path.is_symlink() or not path.is_file() or digest(path) != item["sha256"]:
                raise ValueError("partial transition file differs during recovery")
            allowed_files.add(path)
    for path in root.rglob("*"):
        if path.is_symlink() or (path.is_file() and path not in allowed_files) or (path.is_dir() and path not in allowed_directories):
            raise ValueError("partial root contains foreign recovery bytes")


def execute(value: dict, *, prefix: pathlib.Path, runner: Callable[[list[str]], None],
            probe: Callable[[], dict], stop_after: str | None = None, recover: bool = False) -> dict:
    validate(value)
    root = rooted(prefix, value["proposedRoot"]["path"])
    journal = rooted(prefix, value["journal"])
    administrator_contract = value.get("administratorState", {
        "path": "/var/lib/rp1-gpclk-dkms/transaction.json",
    })
    administrator_state = rooted(prefix, administrator_contract["path"])
    prior_contract = value.get("priorTerminalState")
    prior_archive = rooted(prefix, prior_contract["archivePath"]) if prior_contract else None
    if recover:
        if not journal.exists() and not journal.is_symlink() and not root.exists() and not root.is_symlink():
            if probe() != value["expectedPreState"]:
                raise ValueError("already-clean pre-root recovery baseline differs")
            return {"operationId": value["operationId"], "status": "already-clean", "outputActive": False}
        if journal.is_symlink() or not journal.is_file():
            raise ValueError("pre-root recovery journal is absent")
        old = json.loads(journal.read_text())
        if (old.get("status") != "recovery-required" or old.get("outputActive") is not False or
                type(old.get("administratorInvoked")) is not bool):
            raise ValueError("pre-root journal is not recoverable")
        validate_partial_root(value, root)
        if administrator_state.is_symlink():
            raise ValueError("administrator transaction state is symlinked")
        if administrator_state.exists():
            if not administrator_state.is_file() or not old["administratorInvoked"]:
                raise ValueError("administrator transaction state is ambiguous")
            runner(value["recoveryArgv"])
        elif prior_contract:
            if old["administratorInvoked"]:
                raise ValueError("invoked administrator has no recoverable transaction state")
            if prior_archive is None or prior_archive.is_symlink() or not prior_archive.is_file():
                raise ValueError("archived prior terminal state differs during recovery")
            if value["schemaVersion"]==7: validate_removed_ledger(prior_archive,value,prior_contract)
            elif digest(prior_archive)!=prior_contract["sha256"]: raise ValueError("archived prior terminal state differs during recovery")
            os.replace(prior_archive, administrator_state)
            administrator_state.chmod(int(prior_contract["mode"], 8))
            try:
                prior_archive.parent.rmdir()
            except OSError:
                pass
        elif probe() != value["expectedPreState"]:
            raise ValueError("pre-administrator recovery baseline differs")
        if root.exists():
            marker = root / ".gate-d-root.json"
            for item in reversed(value["transitionFiles"]):
                path = root / item["destination"]
                if path.exists() and not path.is_symlink() and digest(path) == item["sha256"]:
                    path.unlink()
            marker.unlink()
            for directory in sorted((p for p in root.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
                directory.rmdir()
            root.rmdir()
        if probe() != value["expectedPreState"]:
            raise ValueError("post-recovery pre-root baseline differs")
        failure_journal = journal.with_name(f"{journal.stem}.failure.json")
        if failure_journal.exists() or failure_journal.is_symlink():
            raise ValueError("preserved pre-root failure journal already exists")
        shutil.copyfile(journal, failure_journal)
        failure_journal.chmod(0o400)
        journal.unlink()
        return {"operationId": value["operationId"], "status": "recovered",
                "outputActive": False}
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
    if value["schemaVersion"] in {2, 3, 4, 5, 6, 7}:
        validate_release_inputs(value, prefix=prefix)
    if prior_contract:
        if (administrator_state.is_symlink() or not administrator_state.is_file() or
                administrator_state.stat().st_uid != prior_contract["ownerUid"] or
                stat.S_IMODE(administrator_state.stat().st_mode) != int(prior_contract["mode"], 8) or
                (value["schemaVersion"]!=7 and digest(administrator_state) != prior_contract["sha256"])):
            raise ValueError("prior terminal administrator state differs")
        prior_value = json.loads(administrator_state.read_text())
        if (prior_value.get("status") != prior_contract["status"] or
                prior_value.get("recoveryRequired") is not prior_contract["recoveryRequired"] or
                prior_value.get("outputActive") is not prior_contract["outputActive"]):
            raise ValueError("prior administrator state is not terminal recovered")
        if value["schemaVersion"]==7: validate_removed_ledger(administrator_state,value,prior_contract)
        if prior_archive is None or prior_archive.exists() or prior_archive.is_symlink():
            raise ValueError("prior terminal archive destination exists")
    elif administrator_state.exists() or administrator_state.is_symlink():
        raise ValueError("administrator transaction state exists before invocation")
    state = {"operationId": value["operationId"], "status": "in-progress", "checkpoint": "preflight",
             "outputActive": False, "administratorInvoked": False}
    atomic_json(journal, state)
    try:
        if probe() != value["expectedPreState"]:
            raise ValueError("pre-root baseline differs")
        for checkpoint in CHECKPOINTS[1:]:
            state["checkpoint"] = checkpoint
            atomic_json(journal, state)
            if checkpoint == "archive-prior-state" and prior_contract:
                archive_parent = prior_archive.parent
                if archive_parent.exists():
                    if (archive_parent.is_symlink() or not archive_parent.is_dir() or
                            archive_parent.stat().st_uid != prior_contract["ownerUid"] or
                            stat.S_IMODE(archive_parent.stat().st_mode) != 0o700):
                        raise ValueError("prior terminal archive directory is unsafe")
                else:
                    archive_parent.mkdir(mode=0o700)
                os.replace(administrator_state, prior_archive)
                prior_archive.chmod(int(prior_contract["archiveMode"], 8))
            elif checkpoint == "create-root":
                root.mkdir(mode=0o700)
                os.chown(root, value["proposedRoot"]["ownerUid"], -1)
                marker = root / ".gate-d-root.json"
                marker.write_text(json.dumps(value["proposedRoot"]["marker"], sort_keys=True, separators=(",", ":")) + "\n")
                marker.chmod(0o400)
            elif checkpoint == "install":
                state["administratorInvoked"] = True
                atomic_json(journal, state)
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
                if value["schemaVersion"] in {4, 5, 6, 7}:
                    for item in value["installedPackagePaths"]: verify_package_path(prefix,item)
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
