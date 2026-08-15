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
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from typing import Callable

PACKAGE = "rp1-gpclk-dkms"
MODULE = "rp1_gpclk_dkms"
VERSION = "0.0.0-phase5.2"
ROUTES = {"gpio4": "rp1-gpclk-gpio4.dtbo", "gpio20": "rp1-gpclk-gpio20.dtbo"}
ROUTE_CHANGE_STEPS = ["prove-idle", "disable-live-eligibility",
                      "remove-old-binding-proven-cleanup", "verify-both-pins-safe",
                      "select-new-overlay", "revalidate-entire-compatibility-identity",
                      "renew-enrollment-if-policy-requires"]
STEPS = ["preflight", "stage", "verify-staged-hashes", "dkms-add", "dkms-build",
         "sign-if-required", "verify-module", "dkms-install", "install-overlay-inactive",
         "install-policy", "verify-output-disabled", "commit-state"]
SAFE_PATH = re.compile(r"^/[A-Za-z0-9._+/-]+$")


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


def command_runner(args: list[str]) -> str:
    return subprocess.check_output(args, stdin=subprocess.DEVNULL, text=True,
                                   env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin"}).strip()


def execute(release: pathlib.Path, route: str, signing: bool, key: pathlib.Path | None,
            certificate: pathlib.Path | None, root: pathlib.Path = pathlib.Path("/"),
            runner: Callable[[list[str]], str] = command_runner) -> dict:
    transaction = plan(route, signing)
    if release.is_symlink() or not release.is_dir():
        raise ValueError("release must be a real directory")
    metadata = json.loads((release / "release-metadata.json").read_text())
    if metadata.get("release") != VERSION or not metadata.get("publishable"):
        raise ValueError("only the exact publishable release is installable")
    checksums = load_checksums(release)
    if ROUTES[route] not in checksums:
        raise ValueError("selected overlay is absent from checksums")
    if signing and (key is None or certificate is None or key.is_symlink() or certificate.is_symlink()
                    or not key.is_file() or not certificate.is_file()):
        raise ValueError("administrator signing key and certificate are required")
    kernel = platform.release()
    state_path = rooted(root, "/var/lib/rp1-gpclk-dkms/transaction.json")
    if state_path.exists():
        old = json.loads(state_path.read_text())
        if old.get("status") not in {"complete", "recovered"}:
            raise ValueError("unresolved transaction requires explicit recovery")
    transaction.update({"status": "inactive-in-progress", "checkpoint": "preflight",
                        "kernel": kernel, "recoveryRequired": True, "commands": [],
                        "ownedFiles": [], "ownedDirectories": []})
    atomic_json(state_path, transaction)
    try:
        headers = rooted(root, f"/lib/modules/{kernel}/build")
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
        archive_path = release / metadata["archive"]
        if digest(archive_path) != metadata["archiveSha256"]:
            raise ValueError("staged archive hash mismatch")
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
        built_module = f"/var/lib/dkms/{PACKAGE}/{VERSION}/{kernel}/{architecture}/module/{MODULE}.ko"
        installed_module = f"/lib/modules/{kernel}/updates/dkms/{MODULE}.ko"
        if signing:
            commands.append([str(headers / "scripts/sign-file"), "sha256", str(key), str(certificate),
                             built_module])
        commands += [["modinfo", "-F", "version", built_module],
                     ["modinfo", "-F", "vermagic", built_module]]
        if signing:
            commands.append(["modinfo", "-F", "signer", built_module])
        commands += [["dkms", "install", "-m", PACKAGE, "-v", VERSION, "-k", kernel],
                     ["modinfo", "-F", "version", installed_module],
                     ["modinfo", "-F", "vermagic", installed_module]]
        if signing:
            commands.append(["modinfo", "-F", "signer", installed_module])
        for args in commands:
            transaction["checkpoint"] = "sign-if-required" if "sign-file" in args[0] else args[1]
            transaction["commands"].append(["<administrator-key>" if key and value == str(key) else value for value in args])
            atomic_json(state_path, transaction)
            output = runner(args)
            if args[:3] == ["modinfo", "-F", "version"] and output.strip() != VERSION:
                raise ValueError("module version verification failed")
            if args[:3] == ["modinfo", "-F", "vermagic"] and not output.strip().startswith(kernel + " "):
                raise ValueError("module vermagic verification failed")
            if args[:3] == ["modinfo", "-F", "signer"] and not output.strip():
                raise ValueError("required module signer is absent")
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
        package_files = ((source / "scripts/rp1-gpclk-admin.py", libexec / "rp1-gpclk-admin", 0o755),
                         (source / "scripts/rp1-gpclk-diagnostics.py", libexec / "rp1-gpclk-diagnostics", 0o755),
                         (model_source, release_data / "installation-model-v1.json", 0o644),
                         (source / "release/overlay-contract-v1.json",
                          release_data / "overlay-contract-v1.json", 0o644))
        for origin, destination, mode in package_files:
            if not origin.is_file() or origin.is_symlink() or destination.exists() or destination.is_symlink():
                raise ValueError(f"unsafe or existing package file: {destination}")
            shutil.copyfile(origin, destination)
            destination.chmod(mode)
            transaction["ownedFiles"].append({"path": str(destination), "sha256": digest(destination)})
            atomic_json(state_path, transaction)
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
    parser.add_argument("action", choices=("plan", "route-change-plan", "install", "status", "recover"))
    parser.add_argument("--release-directory", type=pathlib.Path)
    parser.add_argument("--route", choices=tuple(ROUTES), default="gpio4")
    parser.add_argument("--signing-required", action="store_true")
    parser.add_argument("--private-key", type=pathlib.Path)
    parser.add_argument("--certificate", type=pathlib.Path)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--snapshot", type=pathlib.Path)
    args = parser.parse_args()
    state = pathlib.Path("/var/lib/rp1-gpclk-dkms/transaction.json")
    if args.action == "plan":
        result = plan(args.route, args.signing_required)
    elif args.action == "route-change-plan":
        if args.snapshot is None or args.snapshot.is_symlink() or not args.snapshot.is_file():
            raise SystemExit("--snapshot must name a real snapshot file")
        result = route_change_plan(json.loads(args.snapshot.read_text()), args.route)
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
        result = execute(args.release_directory.resolve(), args.route, args.signing_required,
                         args.private_key, args.certificate)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
