#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Fail-closed Phase 5.3 package transaction coordinator.

Planning and status are read-only.  System mutation requires both root and the
explicit --execute flag.  The command records an inactive journal before any
external command so recovery can recognize every interruption.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import platform
import pwd
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from typing import Callable

PACKAGE = "rp1-gpclk-dkms"
MODULE = "rp1_gpclk_dkms"
VERSION = "0.0.0-phase5.33"
ROUTES = {"gpio4": "rp1-gpclk-gpio4.dtbo", "gpio20": "rp1-gpclk-gpio20.dtbo"}
ROUTE_CHANGE_STEPS = ["prove-idle", "disable-live-eligibility",
                      "remove-old-binding-proven-cleanup", "verify-both-pins-safe",
                      "select-new-overlay", "revalidate-entire-compatibility-identity",
                      "renew-enrollment-if-policy-requires"]
STEPS = ["preflight", "stage", "verify-staged-hashes", "dkms-add", "dkms-build",
         "verify-dkms-signature", "verify-module", "dkms-install", "install-overlay-inactive",
         "install-policy", "verify-output-disabled", "commit-state"]
SAFE_PATH = re.compile(r"^/[A-Za-z0-9._+/-]+$")
IDENTITY_FIELDS = ("compatibilityEntryId", "compatibilityManifestSha256",
                   "moduleRelease", "moduleSha256", "uapiAbi", "uapiHeaderSha256",
                   "kernelRelease", "kernelConfigSha256", "baseDtSha256",
                   "firmwareIdentity", "overlaySourceSha256", "overlayDtboSha256",
                   "route", "signingIdentity")
ACKNOWLEDGEMENT = ("I accept Experimental RP1 GPCLK dedicated-host and "
                   "software-cohabitation risk for this exact release, identity, and route.")
HASH_IDENTITY_FIELDS = {"compatibilityManifestSha256", "moduleSha256", "uapiHeaderSha256",
                        "kernelConfigSha256", "baseDtSha256", "overlaySourceSha256",
                        "overlayDtboSha256"}


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rooted(root: pathlib.Path, absolute: str) -> pathlib.Path:
    if not SAFE_PATH.fullmatch(absolute) or ".." in pathlib.PurePosixPath(absolute).parts:
        raise ValueError(f"unsafe installation path: {absolute}")
    result = root / absolute.lstrip("/")
    current = root
    for part in pathlib.PurePosixPath(absolute).parts[1:]:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"refusing symlink installation path: {absolute}")
    return result


def kernel_module_tree(root: pathlib.Path, kernel: str) -> pathlib.Path:
    """Resolve the real stock-kernel module tree through one canonical alias."""
    if not re.fullmatch(r"[A-Za-z0-9._+-]+", kernel):
        raise ValueError("unsafe kernel release")
    lib = root / "lib"
    if lib.is_symlink():
        link = os.readlink(lib)
        if link not in {"usr/lib", "/usr/lib"}:
            raise ValueError("kernel module tree uses an unallowlisted /lib alias")
        canonical_lib = rooted(root, "/usr/lib")
    else:
        canonical_lib = rooted(root, "/lib")
    parent = canonical_lib / "modules" / kernel
    current = canonical_lib
    for part in ("modules", kernel):
        current = current / part
        if current.is_symlink():
            raise ValueError("kernel module tree contains an unexpected symlink")
    if not parent.is_dir():
        raise ValueError("kernel module tree is missing")
    return parent


def kernel_headers(root: pathlib.Path, kernel: str) -> pathlib.Path:
    """Resolve only the stock-kernel build link to a protected /usr/src tree."""
    parent = kernel_module_tree(root, kernel)
    build = parent / "build"
    if build.is_symlink():
        link = os.readlink(build)
        if os.path.isabs(link):
            candidate = root / link.lstrip("/")
        else:
            candidate = parent / link
    else:
        candidate = build
    try:
        canonical = candidate.resolve(strict=True)
        canonical_usr_src = (root / "usr/src").resolve(strict=True)
    except OSError as error:
        raise ValueError("kernel header build path is missing or unresolved") from error
    if canonical == canonical_usr_src or canonical_usr_src not in canonical.parents:
        raise ValueError("kernel header build path is outside canonical /usr/src")
    current = canonical_usr_src
    for part in canonical.relative_to(canonical_usr_src).parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("kernel header canonical path contains a symlink")
    status = canonical.stat()
    root_uid = root.stat().st_uid
    if not canonical.is_dir() or status.st_uid != root_uid or status.st_mode & 0o022:
        raise ValueError("kernel header directory ownership or mode is unsafe")
    return canonical


def dkms_built_module(root: pathlib.Path, kernel: str,
                      architecture: str) -> pathlib.Path:
    """Select one allowlisted DKMS-built module representation."""
    if not re.fullmatch(r"[A-Za-z0-9._+-]+", kernel):
        raise ValueError("unsafe kernel release")
    if not re.fullmatch(r"[A-Za-z0-9._+-]+", architecture):
        raise ValueError("unsafe architecture")
    directory = rooted(
        root, f"/var/lib/dkms/{PACKAGE}/{VERSION}/{kernel}/{architecture}/module")
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("DKMS built-module directory is missing or unsafe")
    candidates = [directory / f"{MODULE}{suffix}" for suffix in
                  (".ko", ".ko.xz", ".ko.gz", ".ko.zst")]
    allowed_names = {path.name for path in candidates}
    unknown = [path for path in directory.iterdir()
               if path.name.startswith(f"{MODULE}.ko") and path.name not in allowed_names]
    if unknown:
        raise ValueError("DKMS built-module representation has an unknown suffix")
    present = [path for path in candidates if path.exists() or path.is_symlink()]
    if len(present) != 1:
        raise ValueError("DKMS built-module representation is absent or ambiguous")
    selected = present[0]
    if selected.is_symlink() or not selected.is_file():
        raise ValueError("DKMS built-module representation is not a regular file")
    return selected


def dkms_installed_module(root: pathlib.Path, kernel: str) -> pathlib.Path:
    """Select one allowlisted installed DKMS module representation."""
    directory = kernel_module_tree(root, kernel)
    for part in ("updates", "dkms"):
        directory = directory / part
        if directory.is_symlink():
            raise ValueError("installed DKMS module path contains a symlink")
    if not directory.is_dir():
        raise ValueError("installed DKMS module directory is missing or unsafe")
    candidates = [directory / f"{MODULE}{suffix}" for suffix in
                  (".ko", ".ko.xz", ".ko.gz", ".ko.zst")]
    allowed_names = {path.name for path in candidates}
    unknown = [path for path in directory.iterdir()
               if path.name.startswith(f"{MODULE}.ko") and path.name not in allowed_names]
    if unknown:
        raise ValueError("installed DKMS module representation has an unknown suffix")
    present = [path for path in candidates if path.exists() or path.is_symlink()]
    if len(present) != 1:
        raise ValueError("installed DKMS module representation is absent or ambiguous")
    selected = present[0]
    if selected.is_symlink() or not selected.is_file():
        raise ValueError("installed DKMS module representation is not a regular file")
    return selected


def load_checksums(release: pathlib.Path) -> dict[str, str]:
    checksums: dict[str, str] = {}
    for line in (release / "SHA256SUMS").read_text().splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9][A-Za-z0-9._+-]*)", line)
        if not match or match.group(2) in checksums:
            raise ValueError("invalid checksum manifest")
        checksums[match.group(2)] = match.group(1)
    for name, expected in checksums.items():
        path = release / name
        if path.is_symlink() or not path.is_file() or digest(path) != expected:
            raise ValueError(f"release checksum mismatch: {name}")
    return checksums


def plan(route: str, signing: bool) -> dict:
    if route not in ROUTES:
        raise ValueError("route must be gpio4 or gpio20")
    return {"package": PACKAGE, "dkmsModule": PACKAGE, "kernelModule": MODULE,
            "release": VERSION, "routeArtifact": ROUTES[route], "steps": STEPS,
            "signingRequired": signing, "liveOutput": False, "moduleLoad": "not-performed",
            "overlayActivation": "not-performed", "routeSelection": "not-performed",
            "experimentalEnrollment": "not-performed", "reboot": "not-performed"}


def route_change_plan(snapshot: dict, new_route: str) -> dict:
    """Validate a fail-closed snapshot and return a non-mutating transition plan."""
    if new_route not in ROUTES:
        raise ValueError("route must be gpio4 or gpio20")
    required_false = ("moduleLoaded", "endpointBound", "endpointOpen", "ownerPresent",
                      "generationActive", "callbackPending", "dmaActive", "clockPrepared",
                      "clockEnabled", "cleanupFault", "routeConflict", "persistentConflict",
                      "duplicateMarker", "runtimeOverlayConflict", "endpointBusy")
    required_true = ("liveEligibilityDisabled", "gpio4Safe", "gpio20Safe",
                     "oldBindingCleanupProven", "artifactIdentityValid",
                     "compatibilityIdentityValid", "configurationOwnershipKnown")
    allowed = {"currentRoute", "enrollmentPolicyRequiresRenewal", *required_false, *required_true}
    if set(snapshot) != allowed:
        raise ValueError("route snapshot fields are incomplete or unknown")
    current = snapshot.get("currentRoute")
    if current not in ROUTES or current == new_route:
        raise ValueError("route change requires two distinct allowlisted routes")
    for field in required_false:
        if snapshot.get(field) is not False:
            raise ValueError(f"route transition rejected by {field}")
    for field in required_true:
        if snapshot.get(field) is not True:
            raise ValueError(f"route transition rejected by {field}")
    if snapshot.get("enrollmentPolicyRequiresRenewal") is not True:
        raise ValueError("Phase 5.4 requires explicit enrollment-policy invalidation")
    return {"fromRoute": current, "toRoute": new_route, "steps": ROUTE_CHANGE_STEPS,
            "liveOutput": False, "persistentMutation": False,
            "automaticSubstitution": False, "renewedEnrollmentRequired": True}


def atomic_json(path: pathlib.Path, value: dict) -> None:
    path.parent.mkdir(parents=True, mode=0o755, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=".transaction.", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w") as output:
            json.dump(value, output, indent=2, sort_keys=True)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary_name, path)
    finally:
        pathlib.Path(temporary_name).unlink(missing_ok=True)


def evaluate_permission_state(snapshot: dict, enrollment: dict | None) -> dict:
    """Pure, fail-closed evaluation of the five distinct operator states."""
    required = {*IDENTITY_FIELDS, "packageFilesPresent", "dkmsEntryPresent",
                "runtimePrerequisitesPass", "compatibilityState", "cleanupLatch",
                "routeSelected", "operatorAuthorized", "devicePresent", "deviceUid",
                "deviceGid", "deviceMode", "deviceType", "ownerCount"}
    if set(snapshot) != required:
        raise ValueError("permission snapshot fields are incomplete or unknown")
    if snapshot["route"] not in {"GPIO4", "GPIO20"}:
        raise ValueError("route is not allowlisted")
    if snapshot["compatibilityState"] not in {"Qualified", "Experimental",
                                                "Compatible-unqualified", "Unavailable", "Rejected"}:
        raise ValueError("unknown compatibility state")
    if not isinstance(snapshot["ownerCount"], int) or isinstance(snapshot["ownerCount"], bool) or snapshot["ownerCount"] not in {0, 1}:
        raise ValueError("active ownership must be zero or one")
    installed = snapshot["packageFilesPresent"] is True and snapshot["dkmsEntryPresent"] is True
    permission_ok = (snapshot["devicePresent"] is True and snapshot["deviceUid"] == 0 and
                     snapshot["deviceGid"] == 0 and snapshot["deviceMode"] == "0600" and
                     snapshot["deviceType"] == "character")
    compatible = snapshot["compatibilityState"] in {"Qualified", "Experimental"}
    available = (installed and snapshot["runtimePrerequisitesPass"] is True and compatible and
                 snapshot["cleanupLatch"] is False and permission_ok)
    enrollment_current = False
    enrollment_reason = "not-required-for-qualified" if snapshot["compatibilityState"] == "Qualified" else "absent"
    if snapshot["compatibilityState"] == "Experimental" and enrollment is not None:
        base_fields = {*IDENTITY_FIELDS, "schemaVersion", "kind", "administratorUid",
                       "administratorName", "acceptedAt", "acknowledgement", "revoked"}
        revoked_fields = {"revokedByUid", "revokedByName", "revokedAt"}
        if frozenset(enrollment) not in {frozenset(base_fields), frozenset(base_fields | revoked_fields)}:
            enrollment_reason = "malformed"
        elif enrollment.get("revoked") is True:
            enrollment_reason = "revoked"
        elif (enrollment.get("schemaVersion") != 1 or enrollment.get("kind") != "Experimental" or
              enrollment.get("administratorUid") != 0 or not enrollment.get("administratorName") or
              enrollment.get("acknowledgement") != ACKNOWLEDGEMENT):
            enrollment_reason = "invalid-attribution-or-acceptance"
        elif all(enrollment.get(field) == snapshot.get(field) for field in IDENTITY_FIELDS):
            enrollment_current = True
            enrollment_reason = "current"
        else:
            enrollment_reason = "stale-identity"
    normal_authority = snapshot["routeSelected"] is True and snapshot["operatorAuthorized"] is True
    live_eligible = available and normal_authority and (
        snapshot["compatibilityState"] == "Qualified" or enrollment_current)
    active = snapshot["ownerCount"] == 1
    reasons = []
    if not installed:
        reasons.append("not-installed")
    if not permission_ok:
        reasons.append("device-permission-or-type-mismatch")
    if snapshot["cleanupLatch"] is not False:
        reasons.append("cleanup-latched")
    if not normal_authority:
        reasons.append("route-or-operator-authorization-missing")
    if snapshot["compatibilityState"] == "Experimental" and not enrollment_current:
        reasons.append(f"experimental-enrollment-{enrollment_reason}")
    return {"installed": installed, "available": available, "enrolled": enrollment_current,
            "liveEligible": live_eligible, "active": active, "enrollmentReason": enrollment_reason,
            "reasons": reasons, "readOnly": True}


def write_experimental_enrollment(path: pathlib.Path, identity: dict, acknowledgement: str,
                                  administrator_uid: int, administrator_name: str,
                                  now: str | None = None) -> dict:
    if administrator_uid != 0:
        raise PermissionError("root administrator required")
    if acknowledgement != ACKNOWLEDGEMENT:
        raise ValueError("exact Experimental-risk acknowledgement required")
    if set(identity) != set(IDENTITY_FIELDS) or identity.get("route") not in {"GPIO4", "GPIO20"}:
        raise ValueError("complete allowlisted enrollment identity required")
    if identity.get("uapiAbi") != 1:
        raise ValueError("unsupported UAPI identity")
    for field in IDENTITY_FIELDS:
        value = identity[field]
        if field == "uapiAbi":
            continue
        if not isinstance(value, str) or not value:
            raise ValueError(f"invalid enrollment identity: {field}")
        if field in HASH_IDENTITY_FIELDS and not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError(f"invalid enrollment digest: {field}")
    if path.is_symlink() or (path.exists() and (not path.is_file() or path.stat().st_uid != 0 or
                                                path.stat().st_gid != 0 or path.stat().st_mode & 0o777 != 0o600)):
        raise ValueError("existing enrollment is not a root-owned 0600 real file")
    record = {**identity, "schemaVersion": 1, "kind": "Experimental",
              "administratorUid": administrator_uid, "administratorName": administrator_name,
              "acceptedAt": now or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
              "acknowledgement": acknowledgement, "revoked": False}
    atomic_json(path, record)
    path.chmod(0o600)
    return record


def revoke_enrollment(path: pathlib.Path, administrator_uid: int,
                      administrator_name: str, now: str | None = None) -> dict:
    if administrator_uid != 0:
        raise PermissionError("root administrator required")
    if path.is_symlink() or not path.is_file() or path.stat().st_mode & 0o777 != 0o600:
        raise ValueError("enrollment record is absent or unsafe")
    record = json.loads(path.read_text())
    record.update({"revoked": True, "revokedByUid": administrator_uid,
                   "revokedByName": administrator_name,
                   "revokedAt": now or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")})
    atomic_json(path, record)
    path.chmod(0o600)
    return record


def command_runner(args: list[str]) -> str:
    return subprocess.check_output(args, stdin=subprocess.DEVNULL, text=True,
                                   env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin"}).strip()


def validate_qualification_identity(path: pathlib.Path, metadata: dict,
                                    archive_sha256: str) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError("qualification identity must be a real file")
    value = json.loads(path.read_text(encoding="utf-8"))
    required = {"SPDX-License-Identifier", "schemaVersion", "kind", "release",
                "sourceCommit", "archiveSha256", "publishable", "tagPresent",
                "outputDisabled", "liveOutput", "purpose"}
    schema = value.get("schemaVersion")
    if schema == 2:
        required.add("toolTransitions")
    if (not isinstance(value, dict) or set(value) != required or
            value.get("SPDX-License-Identifier") != "MIT" or
            schema not in {1, 2} or
            value.get("kind") != "rp1-gpclk-gate-d-qualification-install-identity" or
            value.get("publishable") is not False or value.get("tagPresent") is not False or
            value.get("outputDisabled") is not True or value.get("liveOutput") is not False or
            value.get("purpose") != "gate-d-representative-system-qualification" or
            not isinstance(value.get("sourceCommit"), str) or
            not re.fullmatch(r"[0-9a-f]{40}", value["sourceCommit"]) or
            not isinstance(value.get("archiveSha256"), str) or
            not re.fullmatch(r"[0-9a-f]{64}", value["archiveSha256"]) or
            value.get("release") != metadata.get("release") or
            value.get("sourceCommit") != metadata.get("sourceCommit") or
            value.get("archiveSha256") != archive_sha256):
        raise ValueError("qualification identity differs from sealed candidate")
    if schema == 2:
        paths = []
        for item in value["toolTransitions"]:
            if (not isinstance(item, dict) or set(item) != {"path", "predecessorSha256", "successorSha256", "mode"} or
                    not pathlib.PurePosixPath(item.get("path", "")).is_absolute() or
                    ".." in pathlib.PurePosixPath(item["path"]).parts or
                    not all(re.fullmatch(r"[0-9a-f]{64}", item.get(key, ""))
                            for key in ("predecessorSha256", "successorSha256")) or
                    item.get("mode") not in {"0644", "0755"}):
                raise ValueError("invalid qualification tool transition")
            paths.append(item["path"])
        if not paths or len(paths) != len(set(paths)):
            raise ValueError("qualification tool-transition graph is empty or ambiguous")
    return value


def replace_qualification_tool(destination: pathlib.Path, prepared: pathlib.Path,
                               transition: dict, transaction: dict,
                               state_path: pathlib.Path) -> None:
    """Atomically replace one authenticated predecessor and ledger its backup."""
    if (destination.is_symlink() or not destination.is_file() or
            digest(destination) != transition["predecessorSha256"] or
            prepared.is_symlink() or not prepared.is_file() or
            digest(prepared) != transition["successorSha256"]):
        raise ValueError(f"qualification tool transition identity differs: {destination}")
    backup = destination.with_name(f".{destination.name}.rp1-gpclk-predecessor")
    if backup.exists() or backup.is_symlink():
        raise ValueError(f"qualification tool transition backup exists: {backup}")
    record = {"path": str(destination), "backup": str(backup),
              "predecessorSha256": transition["predecessorSha256"],
              "successorSha256": transition["successorSha256"], "status": "planned"}
    transaction["replacedFiles"].append(record)
    atomic_json(state_path, transaction)
    with prepared.open("rb") as payload:
        os.fsync(payload.fileno())
    os.replace(destination, backup)
    directory_fd = os.open(destination.parent, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)
    record["status"] = "predecessor-backed-up"
    atomic_json(state_path, transaction)
    os.replace(prepared, destination)
    destination.chmod(int(transition["mode"], 8))
    directory_fd = os.open(destination.parent, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)
    record["status"] = "successor-installed"
    atomic_json(state_path, transaction)


def execute(release: pathlib.Path, route: str, signing: bool, key: pathlib.Path | None,
            certificate: pathlib.Path | None, root: pathlib.Path = pathlib.Path("/"),
            runner: Callable[[list[str]], str] = command_runner,
            expected_signer: str | None = None, expected_key_id: str | None = None,
            qualification_identity: pathlib.Path | None = None) -> dict:
    transaction = plan(route, signing)
    if release.is_symlink() or not release.is_dir():
        raise ValueError("release must be a real directory")
    metadata = json.loads((release / "release-metadata.json").read_text())
    if metadata.get("release") != VERSION:
        raise ValueError("release identity differs")
    checksums = load_checksums(release)
    archive_path = release / metadata.get("archive", "")
    if (archive_path.is_symlink() or not archive_path.is_file() or
            digest(archive_path) != metadata.get("archiveSha256")):
        raise ValueError("staged archive hash mismatch")
    qualification = None
    if qualification_identity is None:
        if metadata.get("publishable") is not True:
            raise ValueError("only the exact publishable release is installable")
    else:
        if metadata.get("publishable") is not False or metadata.get("tagPresent") is not False:
            raise ValueError("qualification mode accepts only an unpublished development candidate")
        qualification = validate_qualification_identity(qualification_identity, metadata,
                                                        metadata["archiveSha256"])
    if ROUTES[route] not in checksums:
        raise ValueError("selected overlay is absent from checksums")
    if key is not None or certificate is not None:
        raise ValueError("manual signing material is not accepted; configure DKMS native signing")
    if signing and (not expected_signer or not expected_key_id):
        raise ValueError("exact expected DKMS signer and signature key ID are required")
    kernel = platform.release()
    state_path = rooted(root, "/var/lib/rp1-gpclk-dkms/transaction.json")
    if state_path.exists():
        old = json.loads(state_path.read_text())
        if old.get("status") not in {"complete", "recovered"}:
            raise ValueError("unresolved transaction requires explicit recovery")
    transitions = ({item["path"]: item for item in qualification["toolTransitions"]}
                   if qualification and qualification["schemaVersion"] == 2 else {})
    for raw, transition in transitions.items():
        destination = rooted(root, raw)
        if (destination.is_symlink() or not destination.is_file() or
                digest(destination) != transition["predecessorSha256"]):
            raise ValueError(f"qualification predecessor tool differs: {destination}")
    transaction.update({"status": "inactive-in-progress", "checkpoint": "preflight",
                        "kernel": kernel, "recoveryRequired": True, "commands": [],
                        "ownedFiles": [], "ownedDirectories": [], "replacedFiles": []})
    atomic_json(state_path, transaction)
    try:
        headers = kernel_headers(root, kernel)
        overlays = rooted(root, "/boot/firmware/overlays")
        if root == pathlib.Path("/"):
            if os.geteuid() != 0:
                raise PermissionError("root required")
            if platform.machine() != "aarch64" or not headers.is_dir() or not overlays.is_dir():
                raise ValueError("unsupported target or missing headers/overlay directory")
            for tool in ("dkms", "modinfo"):
                if not shutil.which(tool):
                    raise ValueError(f"required tool unavailable: {tool}")
        source = rooted(root, f"/usr/src/{PACKAGE}-{VERSION}")
        if source.exists():
            raise ValueError("source destination already exists")
        transaction["checkpoint"] = "stage"
        atomic_json(state_path, transaction)
        source.mkdir(parents=True, mode=0o755)
        source.chmod(0o755)
        transaction["ownedDirectories"].append(str(source))
        atomic_json(state_path, transaction)
        prefix = f"{PACKAGE}-{VERSION}/"
        with tarfile.open(archive_path, "r:gz") as archive:
            members = archive.getmembers()
            if not members:
                raise ValueError("empty source archive")
            for member in members:
                pure = pathlib.PurePosixPath(member.name)
                if (not member.isfile() or member.issym() or member.islnk() or
                        not member.name.startswith(prefix) or ".." in pure.parts):
                    raise ValueError("unsafe source archive member")
                relative = pathlib.PurePosixPath(member.name.removeprefix(prefix))
                destination = source.joinpath(*relative.parts)
                missing_parents = []
                parent = destination.parent
                while parent != source and not parent.exists():
                    missing_parents.append(parent)
                    parent = parent.parent
                destination.parent.mkdir(parents=True, mode=0o755, exist_ok=True)
                transaction["ownedDirectories"].extend(str(path) for path in reversed(missing_parents))
                payload = archive.extractfile(member)
                if payload is None:
                    raise ValueError("unreadable source archive member")
                destination.write_bytes(payload.read())
                destination.chmod(member.mode)
                transaction["ownedFiles"].append({"path": str(destination), "sha256": digest(destination)})
                atomic_json(state_path, transaction)
        for required in ("dkms.conf", "Kbuild", "include/rp1_gpclk/version.h"):
            if not (source / required).is_file():
                raise ValueError(f"staged source lacks {required}")
        commands = [["dkms", "add", "-m", PACKAGE, "-v", VERSION],
                    ["dkms", "build", "-m", PACKAGE, "-v", VERSION, "-k", kernel]]
        architecture = platform.machine()
        def run_commands(batch: list[list[str]]) -> None:
            for args in batch:
                transaction["checkpoint"] = "verify-dkms-signature" if args[:3] in (
                    ["modinfo", "-F", "signer"], ["modinfo", "-F", "sig_key"]) else args[1]
                transaction["commands"].append(args)
                atomic_json(state_path, transaction)
                output = runner(args)
                if args[:3] == ["modinfo", "-F", "version"] and output.strip() != VERSION:
                    raise ValueError("module version verification failed")
                if args[:3] == ["modinfo", "-F", "vermagic"] and not output.strip().startswith(kernel + " "):
                    raise ValueError("module vermagic verification failed")
                if args[:3] == ["modinfo", "-F", "signer"] and output.strip() != expected_signer:
                    raise ValueError("required module signer identity differs")
                if args[:3] == ["modinfo", "-F", "sig_key"] and output.strip() != expected_key_id:
                    raise ValueError("required module signature key ID differs")

        run_commands(commands)
        built_module = str(dkms_built_module(root, kernel, architecture))
        commands = [["modinfo", "-F", "version", built_module],
                    ["modinfo", "-F", "vermagic", built_module]]
        if signing:
            commands += [["modinfo", "-F", "signer", built_module],
                         ["modinfo", "-F", "sig_key", built_module]]
        commands += [["dkms", "install", "-m", PACKAGE, "-v", VERSION, "-k", kernel]]
        run_commands(commands)
        installed_module = str(dkms_installed_module(root, kernel))
        commands = [["modinfo", "-F", "version", installed_module],
                    ["modinfo", "-F", "vermagic", installed_module]]
        if signing:
            commands += [["modinfo", "-F", "signer", installed_module],
                         ["modinfo", "-F", "sig_key", installed_module]]
        run_commands(commands)
        overlay_destination = overlays / ROUTES[route]
        if overlay_destination.is_symlink() or (overlay_destination.exists() and digest(overlay_destination) != checksums[ROUTES[route]]):
            raise ValueError("refusing unrelated or different overlay")
        overlays.mkdir(parents=True, mode=0o755, exist_ok=True)
        if not overlay_destination.exists():
            shutil.copyfile(release / ROUTES[route], overlay_destination)
            overlay_destination.chmod(0o644)
            transaction["ownedFiles"].append({"path": str(overlay_destination), "sha256": digest(overlay_destination)})
            atomic_json(state_path, transaction)
        release_data = rooted(root, f"/usr/share/{PACKAGE}/{VERSION}")
        release_data_created = not release_data.exists()
        release_data.mkdir(parents=True, mode=0o755, exist_ok=True)
        if release_data_created:
            transaction["ownedDirectories"].append(str(release_data))
        for name in ("SHA256SUMS", "PROVENANCE.json", "release-metadata.json", "rp1-gpclk-compatibility-manifest.json"):
            destination = release_data / name
            if destination.exists() or destination.is_symlink():
                raise ValueError(f"refusing existing policy file: {name}")
            shutil.copyfile(release / name, destination)
            destination.chmod(0o644)
            transaction["ownedFiles"].append({"path": str(destination), "sha256": digest(destination)})
            atomic_json(state_path, transaction)
        model_source = source / "release/installation-model-v1.json"
        libexec = rooted(root, f"/usr/libexec/{PACKAGE}")
        documentation = rooted(root, f"/usr/share/doc/{PACKAGE}")
        configuration = rooted(root, f"/etc/{PACKAGE}")
        for directory in (libexec, documentation, configuration):
            created = not directory.exists()
            if directory.is_symlink():
                raise ValueError(f"refusing symlink directory: {directory}")
            directory.mkdir(parents=True, mode=0o755, exist_ok=True)
            directory.chmod(0o755)
            if created:
                transaction["ownedDirectories"].append(str(directory))
        def install_tool(origin: pathlib.Path, destination: pathlib.Path, mode: int) -> None:
            transition = transitions.pop(str(pathlib.PurePosixPath("/") / destination.relative_to(root))) if transitions else None
            if transition is None:
                if destination.exists() or destination.is_symlink():
                    raise ValueError(f"unsafe or existing package file: {destination}")
                shutil.copyfile(origin, destination)
                destination.chmod(mode)
                transaction["ownedFiles"].append({"path": str(destination), "sha256": digest(destination)})
                atomic_json(state_path, transaction)
                return
            prepared = destination.with_name(f".{destination.name}.rp1-gpclk-successor")
            if prepared.exists() or prepared.is_symlink():
                raise ValueError(f"qualification successor temporary exists: {prepared}")
            shutil.copyfile(origin, prepared)
            prepared.chmod(mode)
            replace_qualification_tool(destination, prepared, transition, transaction, state_path)
        probe_source = source / "tools/gate_d_uapi_probe.c"
        probe_destination = libexec / "gate-d-uapi-probe"
        if not probe_source.is_file() or probe_source.is_symlink() or probe_destination.is_symlink():
            raise ValueError("unsafe Gate D UAPI probe")
        probe_transition = transitions.pop("/usr/libexec/rp1-gpclk-dkms/gate-d-uapi-probe", None)
        if probe_destination.exists() and probe_transition is None:
            raise ValueError("existing Gate D UAPI probe lacks a transition identity")
        probe_output = (probe_destination.with_name(f".{probe_destination.name}.rp1-gpclk-successor")
                        if probe_transition else probe_destination)
        probe_command = ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                         f"-I{source / 'include/uapi'}", str(probe_source),
                         "-o", str(probe_output)]
        transaction["commands"].append(probe_command)
        atomic_json(state_path, transaction)
        runner(probe_command)
        if not probe_output.is_file() or probe_output.is_symlink():
            raise ValueError("Gate D UAPI probe build produced no real binary")
        if probe_transition:
            replace_qualification_tool(probe_destination, probe_output, probe_transition, transaction, state_path)
        else:
            probe_destination.chmod(0o755)
            transaction["ownedFiles"].append({"path": str(probe_destination), "sha256": digest(probe_destination)})
            atomic_json(state_path, transaction)
        busy_source = source / "tools/gate_d_busy_injector.c"
        busy_destination = libexec / "gate-d-busy-injector"
        if not busy_source.is_file() or busy_source.is_symlink() or busy_destination.is_symlink():
            raise ValueError("unsafe Gate D busy injector")
        busy_transition = transitions.pop("/usr/libexec/rp1-gpclk-dkms/gate-d-busy-injector", None)
        if busy_destination.exists() and busy_transition is None:
            raise ValueError("existing Gate D busy injector lacks a transition identity")
        busy_output = (busy_destination.with_name(f".{busy_destination.name}.rp1-gpclk-successor")
                       if busy_transition else busy_destination)
        busy_command = ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        f"-I{source / 'include/uapi'}", str(busy_source),
                        "-o", str(busy_output)]
        transaction["commands"].append(busy_command)
        atomic_json(state_path, transaction)
        runner(busy_command)
        if not busy_output.is_file() or busy_output.is_symlink():
            raise ValueError("Gate D busy injector build produced no real binary")
        if busy_transition:
            replace_qualification_tool(busy_destination, busy_output, busy_transition, transaction, state_path)
        else:
            busy_destination.chmod(0o755)
            transaction["ownedFiles"].append({"path": str(busy_destination), "sha256": digest(busy_destination)})
            atomic_json(state_path, transaction)
        package_files = ((source / "scripts/rp1-gpclk-admin.py", libexec / "rp1-gpclk-admin", 0o755),
                         (source / "scripts/rp1-gpclk-diagnostics.py", libexec / "rp1-gpclk-diagnostics", 0o755),
                         (model_source, release_data / "installation-model-v1.json", 0o644),
                         (source / "release/overlay-contract-v1.json",
                          release_data / "overlay-contract-v1.json", 0o644),
                         (source / "release/permissions-enrollment-policy-v1.json",
                          release_data / "permissions-enrollment-policy-v1.json", 0o644),
                         (source / "release/diagnostics-contract-v1.json",
                          release_data / "diagnostics-contract-v1.json", 0o644),
                         (source / "release/lifecycle-removal-contract-v1.json",
                          release_data / "lifecycle-removal-contract-v1.json", 0o644),
                         (source / "release/gate-d-phase5.24-residue-recovery-v1.json",
                          release_data / "gate-d-phase5.24-residue-recovery-v1.json", 0o644),
                         (source / "schema/gate-d-execution-instance-v1.schema.json",
                          release_data / "gate-d-execution-instance-v1.schema.json", 0o644),
                         (source / "schema/gate-d-qualification-root-v1.schema.json", release_data / "gate-d-qualification-root-v1.schema.json", 0o644),
                         (source / "schema/gate-d-qualification-bootstrap-plan-v1.schema.json", release_data / "gate-d-qualification-bootstrap-plan-v1.schema.json", 0o644),
                         (source / "schema/gate-d-target-plan-v1.schema.json", release_data / "gate-d-target-plan-v1.schema.json", 0o644),
                         (source / "schema/gate-d-pre-root-bootstrap-envelope-v1.schema.json", release_data / "gate-d-pre-root-bootstrap-envelope-v1.schema.json", 0o644),
                         (source / "schema/gate-d-attempt-index-v1.schema.json", release_data / "gate-d-attempt-index-v1.schema.json", 0o644),
                         (source / "scripts/lifecycle_policy.py",
                          libexec / "lifecycle-policy", 0o755),
                         (source / "scripts/gate_d_instance.py",
                          libexec / "gate-d-instance", 0o755),
                         (source / "scripts/gate_d_lifecycle.py",
                          libexec / "gate-d-lifecycle", 0o755),
                         (source / "scripts/gate_d_platform.py",
                          libexec / "gate-d-platform", 0o755),
                         (source / "scripts/gate_d_boot.py",
                          libexec / "gate-d-boot", 0o755),
                         (source / "scripts/gate_d_target_plan.py",
                          libexec / "gate-d-target-plan", 0o755),
                         (source / "scripts/gate_d_attempts.py",
                          libexec / "gate-d-attempts", 0o755),
                         (source / "scripts/gate_d_outer.py",
                          libexec / "gate-d-executor", 0o755),
                         (source / "scripts/gate_d_bootstrap.py",
                          libexec / "gate-d-bootstrap", 0o755),
                         (source / "scripts/gate_d_residue.py",
                          libexec / "gate-d-residue", 0o755),
                         (source / "scripts/gate_d_root.py",
                          libexec / "gate_d_root.py", 0o644),
                         (source / "scripts/gate_d_bootstrap.py", libexec / "gate_d_bootstrap.py", 0o644),
                         (source / "scripts/gate_d_target_plan.py", libexec / "gate_d_target_plan.py", 0o644),
                         (source / "scripts/gate_d_lifecycle.py", libexec / "gate_d_lifecycle.py", 0o644),
                         (source / "scripts/gate_d_outer.py", libexec / "gate_d_outer.py", 0o644),
                         (source / "scripts/gate_d_attempts.py", libexec / "gate_d_attempts.py", 0o644),
                         (source / "scripts/gate_d_instance.py", libexec / "gate_d_instance.py", 0o644))
        package_files += ((source / "scripts/gate_d_preroot.py", libexec / "gate_d_preroot.py", 0o644),)
        for origin, destination, mode in package_files:
            if not origin.is_file() or origin.is_symlink() or destination.is_symlink():
                raise ValueError(f"unsafe package file: {destination}")
            install_tool(origin, destination, mode)
        if transitions:
            raise ValueError("qualification tool-transition path is not an installed permanent tool")
        for origin in sorted((source / "docs/operator").glob("*.md")):
            destination = documentation / origin.name
            if origin.is_symlink() or destination.exists() or destination.is_symlink():
                raise ValueError(f"unsafe or existing documentation: {destination}")
            shutil.copyfile(origin, destination)
            destination.chmod(0o644)
            transaction["ownedFiles"].append({"path": str(destination), "sha256": digest(destination)})
            atomic_json(state_path, transaction)
        sbin = rooted(root, "/usr/sbin")
        sbin.mkdir(parents=True, mode=0o755, exist_ok=True)
        for name in ("rp1-gpclk-admin", "rp1-gpclk-diagnostics"):
            link = sbin / name
            if link.exists() or link.is_symlink():
                raise ValueError(f"refusing existing command: {link}")
            link.symlink_to(f"../libexec/{PACKAGE}/{name}")
            transaction["ownedFiles"].append({"path": str(link), "symlink": f"../libexec/{PACKAGE}/{name}"})
            atomic_json(state_path, transaction)
        loaded = rooted(root, f"/sys/module/{MODULE}")
        if loaded.exists():
            raise ValueError("module is already loaded; output-disabled inactive install cannot be proven")
        for item in transaction["replacedFiles"]:
            destination = pathlib.Path(item["path"])
            backup = pathlib.Path(item["backup"])
            if (item["status"] != "successor-installed" or destination.is_symlink() or
                    not destination.is_file() or digest(destination) != item["successorSha256"] or
                    backup.is_symlink() or not backup.is_file() or
                    digest(backup) != item["predecessorSha256"]):
                raise ValueError("qualification tool transition cannot commit")
            backup.unlink()
            item["status"] = "committed"
            atomic_json(state_path, transaction)
        transaction.update({"status": "complete", "checkpoint": "commit-state", "recoveryRequired": False,
                            "overlayInstalled": str(overlay_destination), "overlayActivationRequired": True,
                            "rebootRequired": False, "keyEnrollmentStatus": "administrator-verification-required" if signing else "not-required-by-install"})
        atomic_json(state_path, transaction)
        return transaction
    except BaseException as error:
        transaction.update({"status": "inactive-recovery-required", "recoveryRequired": True,
                            "failure": type(error).__name__})
        atomic_json(state_path, transaction)
        raise


def recover(state_path: pathlib.Path, runner: Callable[[list[str]], str] = command_runner) -> dict:
    if state_path.is_symlink() or not state_path.is_file():
        raise ValueError("no real transaction state to recover")
    state = json.loads(state_path.read_text())
    if state.get("status") != "inactive-recovery-required" or state.get("liveOutput") is not False:
        raise ValueError("transaction is not an inactive recoverable state")
    kernel = state.get("kernel")
    if not isinstance(kernel, str) or not kernel:
        raise ValueError("transaction lacks kernel identity")
    for command in (["dkms", "uninstall", "-m", PACKAGE, "-v", VERSION, "-k", kernel],
                    ["dkms", "remove", "-m", PACKAGE, "-v", VERSION, "--all"]):
        try:
            runner(command)
        except subprocess.CalledProcessError:
            # Absence is acceptable during recovery; filesystem ownership is
            # still independently verified below.
            pass
    for item in reversed(state.get("ownedFiles", [])):
        path = pathlib.Path(item["path"])
        if "symlink" in item:
            if not path.is_symlink() or os.readlink(path) != item["symlink"]:
                raise ValueError(f"owned command link changed: {path}")
        elif path.is_symlink() or not path.is_file() or digest(path) != item.get("sha256"):
            raise ValueError(f"owned file changed: {path}")
        path.unlink()
    for item in reversed(state.get("replacedFiles", [])):
        path = pathlib.Path(item["path"])
        backup = pathlib.Path(item["backup"])
        status = item.get("status")
        if status == "planned":
            if path.is_symlink() or not path.is_file() or digest(path) != item["predecessorSha256"]:
                raise ValueError(f"planned predecessor changed: {path}")
            continue
        if status == "predecessor-backed-up":
            if path.exists() or path.is_symlink():
                raise ValueError(f"interrupted transition destination exists: {path}")
        elif status == "successor-installed":
            if path.is_symlink() or not path.is_file() or digest(path) != item["successorSha256"]:
                raise ValueError(f"transition successor changed: {path}")
            path.unlink()
        else:
            raise ValueError("transition ledger status is not recoverable")
        if backup.is_symlink() or not backup.is_file() or digest(backup) != item["predecessorSha256"]:
            raise ValueError(f"transition predecessor backup changed: {backup}")
        os.replace(backup, path)
    candidates = sorted({pathlib.Path(value) for value in state.get("ownedDirectories", [])},
                        key=lambda path: len(path.parts), reverse=True)
    for directory in candidates:
        try:
            directory.rmdir()
        except OSError:
            pass
    state.update({"status": "recovered", "checkpoint": "inactive-clean", "recoveryRequired": False})
    atomic_json(state_path, state)
    return state


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("plan", "route-change-plan", "permission-status",
                                            "enroll-experimental", "revoke-enrollment",
                                            "install", "status", "recover"))
    parser.add_argument("--release-directory", type=pathlib.Path)
    parser.add_argument("--route", choices=tuple(ROUTES), default="gpio4")
    parser.add_argument("--signing-required", action="store_true")
    parser.add_argument("--private-key", type=pathlib.Path)
    parser.add_argument("--certificate", type=pathlib.Path)
    parser.add_argument("--expected-signer")
    parser.add_argument("--expected-signature-key-id")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--snapshot", type=pathlib.Path)
    parser.add_argument("--acknowledgement")
    parser.add_argument("--qualification-install", action="store_true")
    parser.add_argument("--qualification-identity", type=pathlib.Path)
    args = parser.parse_args()
    state = pathlib.Path("/var/lib/rp1-gpclk-dkms/transaction.json")
    if args.action == "plan":
        result = plan(args.route, args.signing_required)
    elif args.action == "route-change-plan":
        if args.snapshot is None or args.snapshot.is_symlink() or not args.snapshot.is_file():
            raise SystemExit("--snapshot must name a real snapshot file")
        result = route_change_plan(json.loads(args.snapshot.read_text()), args.route)
    elif args.action == "permission-status":
        if args.snapshot is None or args.snapshot.is_symlink() or not args.snapshot.is_file():
            raise SystemExit("--snapshot must name a real snapshot file")
        enrollment_path = pathlib.Path("/etc/rp1-gpclk-dkms/enrollment.json")
        enrollment = None
        if enrollment_path.exists():
            if (enrollment_path.is_symlink() or not enrollment_path.is_file() or
                    enrollment_path.stat().st_uid != 0 or enrollment_path.stat().st_gid != 0 or
                    enrollment_path.stat().st_mode & 0o777 != 0o600):
                raise SystemExit("enrollment file ownership or mode is unsafe")
            enrollment = json.loads(enrollment_path.read_text())
        result = evaluate_permission_state(json.loads(args.snapshot.read_text()), enrollment)
    elif args.action == "enroll-experimental":
        if not args.execute or os.geteuid() != 0:
            raise SystemExit("Experimental enrollment requires root and --execute")
        if args.snapshot is None or args.snapshot.is_symlink() or not args.snapshot.is_file():
            raise SystemExit("--snapshot must name a real identity file")
        result = write_experimental_enrollment(
            pathlib.Path("/etc/rp1-gpclk-dkms/enrollment.json"),
            json.loads(args.snapshot.read_text()), args.acknowledgement or "",
            os.geteuid(), pwd.getpwuid(os.geteuid()).pw_name)
    elif args.action == "revoke-enrollment":
        if not args.execute or os.geteuid() != 0:
            raise SystemExit("enrollment revocation requires root and --execute")
        result = revoke_enrollment(pathlib.Path("/etc/rp1-gpclk-dkms/enrollment.json"),
                                   os.geteuid(), pwd.getpwuid(os.geteuid()).pw_name)
    elif args.action == "status":
        result = json.loads(state.read_text()) if state.is_file() and not state.is_symlink() else {"status": "absent", "readOnly": True}
    elif args.action == "recover":
        if not args.execute:
            raise SystemExit("recovery mutation requires --execute")
        if os.geteuid() != 0:
            raise SystemExit("root required")
        result = recover(state)
    else:
        if not args.execute:
            raise SystemExit("install mutation requires --execute")
        if args.release_directory is None:
            raise SystemExit("--release-directory is required")
        if args.qualification_install != (args.qualification_identity is not None):
            raise SystemExit("qualification install requires both --qualification-install and --qualification-identity")
        release_directory = (args.release_directory if args.release_directory.is_absolute()
                             else pathlib.Path.cwd() / args.release_directory)
        qualification_identity = args.qualification_identity
        if qualification_identity is not None and not qualification_identity.is_absolute():
            qualification_identity = pathlib.Path.cwd() / qualification_identity
        result = execute(release_directory, args.route, args.signing_required,
                         args.private_key, args.certificate,
                         expected_signer=args.expected_signer,
                         expected_key_id=args.expected_signature_key_id,
                         qualification_identity=(qualification_identity
                                                 if args.qualification_install else None))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
