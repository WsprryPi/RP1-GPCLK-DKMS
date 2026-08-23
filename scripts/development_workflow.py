#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Exact-source RP1-GPCLK-DKMS development lifecycle.

This deliberately does not create or consume release identity.  Mutating
operations write an attributable rollback record before changing host state.
"""

from __future__ import annotations

import argparse
import bz2
import gzip
import hashlib
import json
import lzma
import os
import pathlib
import platform
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from typing import Any

PACKAGE = "rp1-gpclk-dkms"
CANONICAL_MODULE = "rp1_gpclk_dkms"
ENDPOINT = "/dev/rp1-gpclk"
SCHEMA = "rp1-gpclk-source-development-manifest-v1"
ENROLLMENT_SCHEMA = "rp1-gpclk-development-enrollment-v1"
ROLLBACK_SCHEMA = "rp1-gpclk-development-rollback-v1"
STATE_BASE = pathlib.Path("/var/lib/rp1-gpclk-dkms/development")
ENROLLMENT_BASE = pathlib.Path("/etc/rp1-gpclk-dkms/development")
TOOL_PATHS = ("/usr/local/sbin", "/usr/local/bin", "/usr/sbin", "/usr/bin", "/sbin", "/bin")
ROUTES = {"gpio4": "rp1-gpclk-gpio4", "gpio20": "rp1-gpclk-gpio20"}
MODULE_SUFFIXES = (".ko", ".ko.xz", ".ko.zst", ".ko.gz", ".ko.bz2")


class Failure(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(value, indent=2, sort_keys=True).encode() + b"\n"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def root_path(path: pathlib.Path | str) -> pathlib.Path:
    root = pathlib.Path(os.environ.get("RP1_GPCLK_DEVELOPMENT_ROOT", "/"))
    value = pathlib.Path(path)
    return root / str(value).lstrip("/") if root != pathlib.Path("/") and value.is_absolute() else value


def atomic_write(path: pathlib.Path, data: bytes, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    with temporary.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.chmod(mode)
    os.replace(temporary, path)


def run(args: list[str], *, cwd: pathlib.Path | None = None, check: bool = True,
        capture: bool = True, log: pathlib.Path | None = None) -> subprocess.CompletedProcess[str]:
    print("COMMAND " + " ".join(args), file=sys.stderr, flush=True)
    result = subprocess.run(args, cwd=cwd, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE if capture else None,
                            stderr=subprocess.PIPE if capture else None,
                            text=True, check=False, env={**os.environ, "LC_ALL": "C"})
    if log is not None:
        atomic_write(log, ((result.stdout or "") + (result.stderr or "")).encode(), 0o600)
    if capture:
        if result.stdout:
            print(result.stdout, end="", file=sys.stderr)
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
    if check and result.returncode:
        raise Failure(f"command failed ({result.returncode}): {' '.join(args)}")
    return result


def tool(name: str, required: bool = True) -> str | None:
    override = os.environ.get(f"RP1_GPCLK_TOOL_{name.upper().replace('-', '_')}")
    candidates = ([override] if override else []) + [str(pathlib.Path(base) / name) for base in TOOL_PATHS]
    found = next((item for item in candidates if item and pathlib.Path(item).is_file() and os.access(item, os.X_OK)), None)
    if required and found is None:
        raise Failure(f"required tool unavailable: {name}; searched {', '.join(candidates)}")
    return found


def tool_inventory() -> dict[str, str | None]:
    result = {}
    for name in ("dkms", "modprobe", "modinfo", "depmod", "rmmod", "make", "cc", "gcc",
                 "sha256sum", "xz", "zstd", "systemctl", "dtoverlay", "dtc", "cpp"):
        result[name] = tool(name, False)
    return result


def git(source: pathlib.Path, *args: str) -> str:
    result = run([tool("git") or "git", "-C", str(source), *args])
    return result.stdout or ""


def inventory(base: pathlib.Path, relative_paths: list[str]) -> list[dict[str, Any]]:
    result = []
    for name in sorted(relative_paths):
        path = base / name
        if path.is_symlink() or not path.is_file():
            raise Failure(f"tracked input is not a regular file: {name}")
        result.append({"path": name, "size": path.stat().st_size, "sha256": sha256(path)})
    return result


def render(source: pathlib.Path, output: pathlib.Path, version: str, allow_dirty: bool) -> pathlib.Path:
    source, output = source.resolve(), output.absolute()
    if not re.fullmatch(r"[0-9A-Za-z][0-9A-Za-z._+-]*", version):
        raise Failure("invalid module version")
    if output.exists():
        raise Failure(f"destination already exists: {output}")
    commit = git(source, "rev-parse", "HEAD").strip()
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise Failure("source is not at an exact Git commit")
    status = git(source, "status", "--porcelain=v1", "--untracked-files=all")
    dirty = bool(status)
    if dirty and not allow_dirty:
        raise Failure("source checkout is dirty; use --allow-dirty to record and render tracked changes")
    names = [item for item in git(source, "ls-files", "-z").split("\0") if item]
    raw = inventory(source, names)
    output.mkdir(parents=True, mode=0o755)
    try:
        for name in names:
            destination = output / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / name, destination)
            destination.chmod(stat.S_IMODE((source / name).stat().st_mode))
        dkms = output / "dkms.conf"
        before = dkms.read_bytes()
        expected = b'PACKAGE_VERSION="#MODULE_VERSION#"'
        if before.count(expected) != 1:
            raise Failure("dkms.conf does not contain exactly one maintained module-version placeholder")
        intermediate = before.replace(expected, f'PACKAGE_VERSION="{version}"'.encode())
        kernel_filter = re.compile(br'(?m)^BUILD_EXCLUSIVE_KERNEL="[^"]+"$')
        if len(kernel_filter.findall(intermediate)) != 1:
            raise Failure("dkms.conf does not contain exactly one kernel-name filter")
        after = kernel_filter.sub(b'BUILD_EXCLUSIVE_KERNEL=".*"', intermediate)
        dkms.write_bytes(after)
        unresolved = []
        for name in names:
            data = (output / name).read_bytes()
            if re.search(br'(?m)^PACKAGE_VERSION="#[A-Z0-9_]+#"$', data):
                unresolved.append(name)
        if unresolved:
            raise Failure("unresolved module-version placeholder: " + ", ".join(unresolved))
        rendered = inventory(output, names)
        changes = []
        raw_by_name = {item["path"]: item for item in raw}
        for item in rendered:
            if item["sha256"] != raw_by_name[item["path"]]["sha256"]:
                changes.append({"path": item["path"], "beforeSha256": raw_by_name[item["path"]]["sha256"],
                                "afterSha256": item["sha256"], "operation": "replace-module-version-placeholder"})
        if [item["path"] for item in changes] != ["dkms.conf"]:
            raise Failure("renderer performed an unapproved transformation")
        transformations = [
            {"path":"dkms.conf","operation":"replace-module-version-placeholder","beforeSha256":sha256_bytes(before),"afterSha256":sha256_bytes(intermediate)},
            {"path":"dkms.conf","operation":"relax-development-kernel-name-filter","beforeSha256":sha256_bytes(intermediate),"afterSha256":sha256_bytes(after)},
        ]
        repository_url = run([tool("git") or "git", "-C", str(source), "config", "--get", "remote.origin.url"], check=False).stdout.strip()
        manifest = {
            "schema": SCHEMA, "classification": "source-development", "qualification": False,
            "createdAtUnix": int(time.time()), "repository": str(source),
            "repositoryUrl": repository_url or None,
            "sourceCommit": commit,
            "sourceState": "dirty-explicitly-allowed" if dirty else "clean", "sourceStatus": status.splitlines(),
            "renderedVersion": version, "packageName": PACKAGE, "dkmsName": PACKAGE,
            "moduleName": CANONICAL_MODULE, "renderedTree": str(output),
            "rawInventory": raw, "renderedInventory": rendered, "transformations": transformations,
            "changedFiles":["dkms.conf"],
            "uapiIdentity": {"path":"include/uapi/linux/rp1_gpclk.h", "sha256":sha256(output/"include/uapi/linux/rp1_gpclk.h")},
            "overlayIdentity": {route:{"path":f"overlays/rp1-gpclk-{route}.dts", "sha256":sha256(output/f"overlays/rp1-gpclk-{route}.dts")} for route in ROUTES},
            "compatibilityIdentity": {"path":"src/rp1_gpclk_compatibility.c", "sha256":sha256(output/"src/rp1_gpclk_compatibility.c")},
            "releaseIdentity": None, "releaseQualified": False,
        }
        path = output / "DEVELOPMENT_MANIFEST.json"
        atomic_write(path, canonical(manifest), 0o644)
        return path
    except BaseException:
        shutil.rmtree(output)
        raise


def load_manifest(path: pathlib.Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise Failure(f"development manifest is unreadable: {error}") from error
    if value.get("schema") != SCHEMA or value.get("classification") != "source-development" or value.get("qualification") is not False:
        raise Failure("not a valid source-development manifest")
    if value.get("moduleName") != CANONICAL_MODULE or value.get("dkmsName") != PACKAGE:
        raise Failure("manifest module identity mismatch")
    return value


def compression(path: pathlib.Path) -> str:
    return "none" if path.name.endswith(".ko") else path.suffix.lstrip(".")


def decompressed(path: pathlib.Path) -> bytes:
    data = path.read_bytes()
    kind = compression(path)
    if kind == "none": return data
    if kind == "xz": return lzma.decompress(data)
    if kind == "gz": return gzip.decompress(data)
    if kind == "bz2": return bz2.decompress(data)
    if kind == "zst":
        zstd = tool("zstd")
        result = subprocess.run([zstd or "zstd", "-q", "-d", "-c", str(path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode: raise Failure(f"zstd decompression failed: {result.stderr.decode(errors='replace')}")
        return result.stdout
    raise Failure(f"unsupported module compression: {kind}")


def module_candidates(kernel: str) -> list[pathlib.Path]:
    base = root_path(f"/lib/modules/{kernel}")
    return sorted(path for path in base.rglob(f"{CANONICAL_MODULE}.ko*")
                  if path.is_file() and any(path.name.endswith(s) for s in MODULE_SUFFIXES)) if base.is_dir() else []


def modinfo(path: pathlib.Path, field: str) -> str:
    result = run([tool("modinfo") or "modinfo", "-F", field, str(path)], check=False)
    return (result.stdout or "").strip() if result.returncode == 0 else ""


def resolve_module(kernel: str, expected_version: str | None = None) -> dict[str, Any]:
    matches = []
    for path in module_candidates(kernel):
        name = modinfo(path, "name")
        if name == CANONICAL_MODULE:
            matches.append((path, name))
    if len(matches) != 1:
        raise Failure(f"expected exactly one installed {CANONICAL_MODULE} artifact for {kernel}; found {len(matches)}")
    path, name = matches[0]
    version = modinfo(path, "version")
    if expected_version and version != expected_version:
        raise Failure(f"installed module version mismatch: expected {expected_version}, got {version or 'absent'}")
    elf = decompressed(path)
    if not elf.startswith(b"\x7fELF"):
        raise Failure("installed module does not decompress to ELF")
    return {"installedPath": str(path), "installedFileSha256": sha256(path), "compression": compression(path),
            "decompressedElfSha256": sha256_bytes(elf), "moduleName": name, "moduleVersion": version,
            "vermagic": modinfo(path, "vermagic"), "signer": modinfo(path, "signer"),
            "signatureKey": modinfo(path, "sig_key"), "signatureHashAlgorithm": modinfo(path, "sig_hashalgo"),
            "signatureState": "signed" if modinfo(path, "signer") else "unsigned"}


def kernel_identities(requested: str) -> dict[str, Any]:
    running = platform.release()
    headers = root_path(f"/lib/modules/{requested}/build")
    boot = root_path("/boot/firmware").exists()
    loaded = root_path(f"/sys/module/{CANONICAL_MODULE}").exists()
    return {"runningKernel": running, "requestedBuildKernel": requested,
            "headersKernel": requested if headers.exists() else None,
            "installedModuleKernel": requested if module_candidates(requested) else None,
            "bootSelectedKernel": requested if boot and requested == running else "not-reliably-discoverable",
            "loadedModuleKernel": running if loaded else None}


def print_mutation_identity(kernel: str, artifact: str | None = None) -> None:
    print(json.dumps({"resolvedModuleName": CANONICAL_MODULE, "installedArtifact": artifact,
                      "targetKernel": kernel}, sort_keys=True), file=sys.stderr)


def require_root() -> None:
    if os.environ.get("RP1_GPCLK_DEVELOPMENT_TEST_ROOT") != "1" and os.geteuid() != 0:
        raise Failure("mutation requires root")


def update_manifest(path: pathlib.Path, additions: dict[str, Any]) -> dict[str, Any]:
    value = load_manifest(path)
    value.update(additions)
    atomic_write(path, canonical(value), 0o644)
    return value


def install(args: argparse.Namespace) -> dict[str, Any]:
    requested = args.kernel or platform.release()
    identities, tools = kernel_identities(requested), tool_inventory()
    print(json.dumps({"kernels": identities, "tools": tools}, indent=2, sort_keys=True), file=sys.stderr)
    for required in ("make", "dkms", "depmod", "modinfo", "sha256sum"):
        if not tools[required]: raise Failure(f"required tool unavailable: {required}")
    if (args.load or root_path(f"/sys/module/{CANONICAL_MODULE}").exists()) and not tools["modprobe"]:
        raise Failure("required tool unavailable: modprobe")
    if identities["headersKernel"] is None:
        raise Failure(f"missing headers for requested kernel: /lib/modules/{requested}/build")
    source = pathlib.Path(args.source).resolve()
    evidence = pathlib.Path(args.evidence_directory).absolute()
    if evidence.exists(): raise Failure(f"evidence directory already exists: {evidence}")
    evidence.mkdir(parents=True, mode=0o755)
    rendered = evidence / "rendered-source"
    manifest_path = render(source, rendered, args.module_version, args.allow_dirty)
    rollback_path = evidence / "ROLLBACK.json"
    before = {"dkmsStatus": run([tools["dkms"], "status", "-m", PACKAGE], check=False).stdout.splitlines(),
              "installedArtifacts": [{"path": str(p), "sha256": sha256(p)} for p in module_candidates(requested)],
              "loaded": root_path(f"/sys/module/{CANONICAL_MODULE}").exists(), "createdFiles": []}
    rollback = {"schema": ROLLBACK_SCHEMA, "classification": "source-development", "manifest": str(manifest_path),
                "kernel": requested, "moduleName": CANONICAL_MODULE, "version": args.module_version,
                "prior": before, "workflowCreatedFiles": [], "status": "prepared"}
    atomic_write(rollback_path, canonical(rollback))
    install_requested = args.install or not args.build_only
    if args.build_only or install_requested:
        require_root()
        print_mutation_identity(requested)
        destination = root_path(f"/usr/src/{PACKAGE}-{args.module_version}")
        if destination.exists():
            if root_path(f"/sys/module/{CANONICAL_MODULE}").exists():
                run([tools["modprobe"], "-r", CANONICAL_MODULE], log=evidence / "module-unload-for-replace.log")
            run([tools["dkms"], "remove", "-m", PACKAGE, "-v", args.module_version, "--all"], log=evidence / "dkms-remove.log")
            if destination.exists(): shutil.rmtree(destination)
        shutil.copytree(rendered, destination)
        rollback["workflowCreatedFiles"].append(str(destination))
        run([tools["dkms"], "add", "-m", PACKAGE, "-v", args.module_version], log=evidence / "dkms-add.log")
        run([tools["dkms"], "build", "-m", PACKAGE, "-v", args.module_version, "-k", requested], log=evidence / "dkms-build.log")
        if install_requested:
            run([tools["dkms"], "install", "-m", PACKAGE, "-v", args.module_version, "-k", requested], log=evidence / "dkms-install.log")
            run([tools["depmod"], "-a", requested], log=evidence / "depmod.log")
    module = resolve_module(requested, args.module_version) if install_requested else None
    if module: print_mutation_identity(requested, module["installedPath"])
    compiler = tools["cc"] or tools["gcc"]
    version_safe = {"dkms","modinfo","depmod","make","cc","gcc","sha256sum","xz","zstd","dtc","cpp"}
    tool_versions = {name:(run([path,"--version"],check=False).stdout or "").splitlines()[:1]
                     for name,path in tools.items() if path and name in version_safe}
    manifest = update_manifest(manifest_path, {"targetKernel": requested, "kernelIdentities": kernel_identities(requested),
        "architecture": platform.machine(), "headersPath":str(root_path(f"/lib/modules/{requested}/build")),
        "compiler":compiler, "toolVersions":tool_versions, "tools": tools, "installedModule": module, "route": args.route,
        "parameters": {"live_output": args.live_output}, "buildLogs": sorted(str(p) for p in evidence.glob("*.log")),
        "dkmsStatus":run([tools["dkms"],"status","-m",PACKAGE,"-v",args.module_version],check=False).stdout.splitlines(),
        "rollbackRecord": str(rollback_path), "developmentState": "development-installed" if module else "development-built"})
    if args.load:
        if requested != platform.release(): raise Failure("cannot load a module built for a non-running kernel")
        lifecycle_action("load", manifest_path, args.live_output)
        manifest = load_manifest(manifest_path)
    rollback["status"] = "ready"; atomic_write(rollback_path, canonical(rollback))
    result = {"status": "ok", "classification": "source-development", "manifest": str(manifest_path),
              "rollback": str(rollback_path), "state": manifest.get("developmentState"), "module": module}
    atomic_write(evidence / "RESULT.json", canonical(result), 0o644)
    return result


def sysfs_parameter(name: str) -> str | None:
    path = root_path(f"/sys/module/{CANONICAL_MODULE}/parameters/{name}")
    return path.read_text().strip() if path.is_file() else None


def lifecycle_action(action: str, manifest_path: pathlib.Path, live_output: int | None = None) -> dict[str, Any]:
    manifest = load_manifest(manifest_path); kernel = manifest.get("targetKernel")
    if not kernel: raise Failure("manifest has no target kernel")
    module = resolve_module(kernel, manifest["renderedVersion"])
    loaded = root_path(f"/sys/module/{CANONICAL_MODULE}").exists()
    if action == "status": return lifecycle_status(manifest_path)
    require_root(); print_mutation_identity(kernel, module["installedPath"])
    modprobe, depmod = tool("modprobe"), tool("depmod")
    if action in {"load", "reload"}:
        if kernel != platform.release(): raise Failure("requested module kernel is not running")
        if action == "reload" and loaded: run([modprobe or "modprobe", "-r", CANONICAL_MODULE])
        elif loaded: raise Failure("module is already loaded; use reload")
        run([depmod or "depmod", "-a", kernel])
        run([modprobe or "modprobe", CANONICAL_MODULE, f"live_output={int(live_output or 0)}"])
        loaded_version_path = root_path(f"/sys/module/{CANONICAL_MODULE}/version")
        loaded_version = loaded_version_path.read_text().strip() if loaded_version_path.is_file() else None
        if loaded_version is not None and loaded_version != manifest["renderedVersion"]:
            raise Failure(f"loaded module version mismatch: expected {manifest['renderedVersion']}, got {loaded_version}")
        observed = sysfs_parameter("live_output")
        expected = "Y" if live_output else "N"
        if observed not in {expected, str(int(bool(live_output)))}:
            raise Failure(f"loaded live_output mismatch: expected {expected}, got {observed}")
        update_manifest(manifest_path, {"parameters": {"live_output": int(live_output or 0)},
                                       "developmentState": "development-live-enabled" if live_output else "development-loaded"})
    elif action == "unload":
        if loaded: run([modprobe or "modprobe", "-r", CANONICAL_MODULE])
        if root_path(f"/sys/module/{CANONICAL_MODULE}").exists(): raise Failure("module remains loaded")
        update_manifest(manifest_path, {"developmentState": "development-installed"})
    else: raise Failure(f"unknown lifecycle action: {action}")
    return lifecycle_status(manifest_path)


def endpoint_status() -> dict[str, Any]:
    path = root_path(ENDPOINT)
    present = path.exists()
    metadata: dict[str, Any] = {"path": ENDPOINT, "present": present}
    if present:
        value = path.stat(); metadata.update(mode=f"{stat.S_IMODE(value.st_mode):04o}", uid=value.st_uid, gid=value.st_gid)
        if stat.S_ISCHR(value.st_mode): metadata.update(major=os.major(value.st_rdev), minor=os.minor(value.st_rdev))
    lsof = tool("lsof", False)
    metadata["openOwners"] = run([lsof, ENDPOINT], check=False).stdout.splitlines()[1:] if present and lsof else []
    return metadata


def lifecycle_status(manifest_path: pathlib.Path) -> dict[str, Any]:
    manifest = load_manifest(manifest_path); kernel = manifest.get("targetKernel") or platform.release()
    loaded = root_path(f"/sys/module/{CANONICAL_MODULE}").exists()
    endpoint = endpoint_status()
    state = "development-endpoint-ready" if loaded and endpoint["present"] else "development-loaded" if loaded else "development-installed" if module_candidates(kernel) else "development-built"
    if loaded and sysfs_parameter("live_output") in {"Y", "1"}: state = "development-live-enabled"
    module = None
    try: module = resolve_module(kernel, manifest["renderedVersion"])
    except Failure: pass
    return {"classification": "source-development", "releaseQualified": False, "developmentState": state,
            "nextAction": {"development-built":"install", "development-installed":"load", "development-loaded":"verify endpoint",
                           "development-endpoint-ready":"separately authorize use", "development-live-enabled":"separately authorize operation"}.get(state),
            "sourceCommit": manifest["sourceCommit"], "sourceState": manifest["sourceState"], "renderedVersion": manifest["renderedVersion"],
            "module": module, "loaded": loaded, "loadedParameters": {"live_output": sysfs_parameter("live_output")},
            "moduleRefcount": root_path(f"/sys/module/{CANONICAL_MODULE}/refcnt").read_text().strip() if root_path(f"/sys/module/{CANONICAL_MODULE}/refcnt").is_file() else None,
            "endpoint": endpoint, "kernels": kernel_identities(kernel), "route": manifest.get("route"),
            "enrollment": enrollment_status(manifest_path), "manifest": str(manifest_path)}


def enrollment_path(manifest: dict[str, Any]) -> pathlib.Path:
    return root_path(ENROLLMENT_BASE / f"{manifest['sourceCommit']}-{manifest['renderedVersion']}.json")


def development_identity(manifest: dict[str, Any]) -> str:
    fields = {name:manifest.get(name) for name in ("sourceCommit","sourceState","renderedVersion","moduleName",
              "targetKernel","route","uapiIdentity","overlayIdentity","compatibilityIdentity","installedModule")}
    return sha256_bytes(json.dumps(fields,sort_keys=True,separators=(",",":")).encode())


def enrollment_status(manifest_path: pathlib.Path) -> dict[str, Any]:
    manifest = load_manifest(manifest_path); path = enrollment_path(manifest)
    if not path.is_file(): return {"status": "absent", "path": str(path)}
    try: value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError): return {"status": "rejected", "path": str(path)}
    expected = {"sourceCommit": manifest["sourceCommit"], "moduleVersion": manifest["renderedVersion"],
                "moduleName": CANONICAL_MODULE, "kernel": manifest.get("targetKernel"), "route": manifest.get("route"),
                "developmentIdentitySha256":development_identity(manifest)}
    return {"status": "current" if all(value.get(k) == v for k, v in expected.items()) else "mismatch", "path": str(path), "record": value}


def enroll(manifest_path: pathlib.Path, route: str, kernel: str, remove: bool = False) -> dict[str, Any]:
    require_root(); manifest = load_manifest(manifest_path)
    if manifest.get("targetKernel") != kernel or manifest.get("route") != route:
        raise Failure("development enrollment kernel or route differs from manifest")
    path = enrollment_path(manifest)
    if remove:
        print_mutation_identity(kernel)
        if path.is_file(): path.unlink()
        return {"status": "removed", "path": str(path)}
    module = resolve_module(kernel, manifest["renderedVersion"])
    print_mutation_identity(kernel, module["installedPath"])
    record = {"schema": ENROLLMENT_SCHEMA, "classification": "Experimental", "qualification": False,
              "sourceCommit": manifest["sourceCommit"], "sourceManifestSha256": sha256(manifest_path),
              "developmentIdentitySha256":development_identity(manifest),
              "moduleName": CANONICAL_MODULE, "moduleVersion": manifest["renderedVersion"],
              "installedModule": module, "kernel": kernel, "route": route,
              "uapiIdentity": manifest.get("uapiIdentity"), "overlayIdentity": manifest.get("overlayIdentity"),
              "compatibilityIdentity": manifest.get("compatibilityIdentity"), "removalCommand": f"sudo ./scripts/development-enroll --remove --manifest {manifest_path} --route {route} --kernel {kernel}"}
    atomic_write(path, canonical(record), 0o644)
    return {"status": "enrolled", "path": str(path), "record": record}


def rollback(record_path: pathlib.Path) -> dict[str, Any]:
    require_root()
    try: record = json.loads(record_path.read_text())
    except (OSError, json.JSONDecodeError) as error: raise Failure(f"rollback record unreadable: {error}") from error
    if record.get("schema") != ROLLBACK_SCHEMA: raise Failure("invalid rollback record")
    kernel, version = record["kernel"], record["version"]
    print_mutation_identity(kernel)
    if root_path(f"/sys/module/{CANONICAL_MODULE}").exists(): run([tool("modprobe") or "modprobe", "-r", CANONICAL_MODULE])
    run([tool("dkms") or "dkms", "remove", "-m", PACKAGE, "-v", version, "--all"], check=False)
    for name in record.get("workflowCreatedFiles", []):
        path = pathlib.Path(name)
        allowed = root_path(f"/usr/src/{PACKAGE}-{version}")
        if path != allowed: raise Failure(f"rollback record contains out-of-scope path: {path}")
        if path.is_dir(): shutil.rmtree(path)
    run([tool("depmod") or "depmod", "-a", kernel])
    record["status"] = "rolled-back"; atomic_write(record_path, canonical(record))
    return {"status": "rolled-back", "record": str(record_path), "scope": "recorded-objects-only"}


def route_observation(manifest_path: pathlib.Path) -> dict[str, Any]:
    manifest = load_manifest(manifest_path); requested = manifest.get("route")
    enrollment = enrollment_status(manifest_path)
    config = root_path("/boot/firmware/config.txt")
    configured = []
    if config.is_file():
        text = config.read_text(errors="replace")
        configured = [route for route, overlay in ROUTES.items() if re.search(rf"(?m)^dtoverlay={re.escape(overlay)}\s*$", text)]
    active = []
    tree = root_path("/sys/firmware/devicetree/base")
    if tree.is_dir():
        for route in ROUTES:
            if any(path.name == f"rp1-gpclk-dkms-{route}" for path in tree.rglob(f"rp1-gpclk-dkms-{route}")):
                active.append(route)
    module_route = None
    route_parameter = root_path(f"/sys/module/{CANONICAL_MODULE}/parameters/route")
    if route_parameter.is_file(): module_route = route_parameter.read_text().strip().lower()
    endpoint = endpoint_status()
    configured_route = configured[0] if len(configured) == 1 else "ambiguous" if configured else None
    active_route = active[0] if len(active) == 1 else "ambiguous" if active else None
    live = (requested is not None and configured_route == active_route == requested and
            module_route in {None, requested} and endpoint["present"] and enrollment["status"] == "current" and
            sysfs_parameter("live_output") in {"Y", "1"})
    return {"requestedRoute": requested, "savedRoute": enrollment.get("record", {}).get("route"),
            "configuredRoute": configured_route, "overlayActiveRoute": active_route,
            "moduleReportedRoute": module_route, "endpoint": endpoint, "liveEligibleRoute": requested if live else None,
            "classification": "Experimental", "releaseQualified": False,
            "rebootRequired": configured_route != active_route}


def route_action(action: str, manifest_path: pathlib.Path, route: str | None) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    if route is not None and manifest.get("route") != route: raise Failure("requested route differs from development manifest")
    if action in {"status", "verify"}:
        state = route_observation(manifest_path)
        if action == "verify" and any((state["configuredRoute"] not in {None, manifest.get("route")},
                                       state["overlayActiveRoute"] not in {None, manifest.get("route")},
                                       state["moduleReportedRoute"] not in {None, manifest.get("route")})):
            raise Failure("development route identity mismatch")
        return state
    require_root(); selected = route or manifest.get("route")
    if selected not in ROUTES: raise Failure("an explicit gpio4 or gpio20 route is required")
    kernel = manifest.get("targetKernel") or platform.release(); print_mutation_identity(kernel)
    config = root_path("/boot/firmware/config.txt")
    if config.is_symlink() or not config.is_file(): raise Failure("boot configuration is absent or unsafe")
    record_path = root_path(STATE_BASE / f"route-{manifest['sourceCommit'][:12]}-{selected}.json")
    if action == "rollback":
        try: record = json.loads(record_path.read_text())
        except (OSError,json.JSONDecodeError) as error: raise Failure(f"route rollback record unavailable: {error}") from error
        if record.get("schema") != ROLLBACK_SCHEMA or record.get("kind") != "development-route": raise Failure("invalid development route record")
        lines=[line for line in config.read_text().splitlines() if line != f"dtoverlay={ROUTES[selected]}"]
        atomic_write(config,("\n".join(lines)+"\n").encode(),stat.S_IMODE(config.stat().st_mode))
        record["status"]="removed-awaiting-reboot"; atomic_write(record_path,canonical(record))
        return {"status":"removed-awaiting-reboot","affectedFile":str(config),"rebootRequired":True}
    before = config.read_bytes(); text = before.decode(errors="strict")
    lines = [line for line in text.splitlines() if not any(line == f"dtoverlay={overlay}" for overlay in ROUTES.values())]
    lines.append(f"dtoverlay={ROUTES[selected]}")
    after = ("\n".join(lines) + "\n").encode()
    record = {"schema": ROLLBACK_SCHEMA, "kind": "development-route", "manifest": str(manifest_path),
              "path": str(config), "beforeSha256": sha256_bytes(before), "before": before.decode(),
              "afterSha256": sha256_bytes(after), "route": selected, "status": "prepared",
              "rollbackCommand": f"sudo ./scripts/development-route rollback --manifest {manifest_path}"}
    atomic_write(record_path, canonical(record)); atomic_write(config, after, stat.S_IMODE(config.stat().st_mode))
    record["status"] = "awaiting-reboot"; atomic_write(record_path, canonical(record))
    return {**route_observation(manifest_path), "affectedFiles": [str(config), str(record_path)],
            "priorSha256": record["beforeSha256"], "newSha256": record["afterSha256"],
            "ownership": "development-recorded-exact-file", "rollbackCommand": record["rollbackCommand"]}


def overlay_action(action: str, manifest_path: pathlib.Path, output: pathlib.Path | None) -> dict[str, Any]:
    manifest = load_manifest(manifest_path); tree = pathlib.Path(manifest["renderedTree"]); route = manifest.get("route")
    if route not in ROUTES: raise Failure("manifest route is absent")
    kernel = manifest.get("targetKernel") or platform.release()
    if action == "status": return route_observation(manifest_path)
    require_root(); print_mutation_identity(kernel)
    record = root_path(STATE_BASE / f"overlay-{manifest['sourceCommit'][:12]}-{route}.json")
    if action == "rollback":
        try: payload=json.loads(record.read_text())
        except (OSError,json.JSONDecodeError) as error: raise Failure(f"overlay rollback record unavailable: {error}") from error
        destination=pathlib.Path(payload["path"])
        if payload.get("schema")!=ROLLBACK_SCHEMA or payload.get("kind")!="development-overlay": raise Failure("invalid development overlay record")
        if destination.is_file(): destination.unlink()
        payload["status"]="removed"; atomic_write(record,canonical(payload))
        return {"status":"removed","affectedFile":str(destination),"rebootRequired":True}
    tools = tool_inventory(); dtc, cpp = tools["dtc"], tools["cpp"]
    if not dtc or not cpp: raise Failure("overlay build requires cpp and dtc")
    output = (output or pathlib.Path(manifest["renderedTree"]) / "development-overlays").absolute()
    output.mkdir(parents=True, exist_ok=True)
    common = root_path(f"/usr/src/linux-headers-{kernel.replace('+rpt-rpi-2712','+rpt-common-rpi')}/include")
    if not common.is_dir(): raise Failure(f"device-tree headers unavailable: {common}")
    source = tree / "overlays" / f"rp1-gpclk-{route}.dts"; pp = output / f"rp1-gpclk-{route}.pp.dts"; artifact = output / f"rp1-gpclk-{route}.dtbo"
    pre = run([cpp, "-nostdinc", "-I", str(common), "-undef", "-x", "assembler-with-cpp", str(source)])
    atomic_write(pp, (pre.stdout or "").encode(), 0o644)
    run([dtc, "-@", "-I", "dts", "-O", "dtb", "-o", str(artifact), str(pp)])
    result = {"route": route, "source": str(source), "sourceSha256": sha256(source), "artifact": str(artifact), "artifactSha256": sha256(artifact)}
    if action == "install":
        destination = root_path(f"/boot/firmware/overlays/rp1-gpclk-{route}.dtbo")
        before = {"present": destination.is_file(), "sha256": sha256(destination) if destination.is_file() else None}
        if destination.exists() and (destination.is_symlink() or not destination.is_file()): raise Failure("overlay destination is unsafe")
        payload = {"schema": ROLLBACK_SCHEMA, "kind": "development-overlay", "path": str(destination), "before": before,
                   "newSha256": result["artifactSha256"], "manifest": str(manifest_path), "status": "prepared"}
        atomic_write(record, canonical(payload)); shutil.copyfile(artifact, destination); destination.chmod(0o644)
        payload["status"] = "installed"; atomic_write(record, canonical(payload)); result.update(installedPath=str(destination), prior=before,
            rebootRequired=True, rollbackRecord=str(record))
    update_manifest(manifest_path, {"overlayIdentity": result})
    return result


def parser_for(command: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=f"scripts/{command}")
    if command == "render-development-tree":
        parser.add_argument("--source", required=True); parser.add_argument("--output", required=True)
        parser.add_argument("--module-version", required=True); parser.add_argument("--allow-dirty", action="store_true")
    elif command == "development-preflight": parser.add_argument("--kernel", default=platform.release())
    elif command == "development-install":
        parser.add_argument("--source", default="."); parser.add_argument("--kernel", default=platform.release())
        parser.add_argument("--module-version", required=True); parser.add_argument("--route", choices=ROUTES, required=True)
        parser.add_argument("--live-output", type=int, choices=(0,1), required=True); parser.add_argument("--evidence-directory", required=True)
        parser.add_argument("--build-only", action="store_true"); parser.add_argument("--install", action="store_true")
        parser.add_argument("--load", action="store_true")
        parser.add_argument("--keep-build", action="store_true"); parser.add_argument("--allow-dirty", action="store_true")
    elif command == "development-enroll":
        parser.add_argument("--manifest", type=pathlib.Path, required=True); parser.add_argument("--route", choices=ROUTES, required=True)
        parser.add_argument("--kernel", required=True); parser.add_argument("--remove", action="store_true")
    elif command == "development-module":
        parser.add_argument("action", choices=("load","reload","status","unload")); parser.add_argument("--manifest", type=pathlib.Path, required=True)
        parser.add_argument("--live-output", type=int, choices=(0,1), default=0)
    elif command in {"development-status", "development-endpoint"}:
        parser.add_argument("--manifest", type=pathlib.Path, required=True); parser.add_argument("--json", action="store_true")
    elif command == "development-rollback": parser.add_argument("--record", type=pathlib.Path, required=True)
    elif command == "development-route":
        parser.add_argument("action", choices=("status","apply","verify","rollback")); parser.add_argument("--development-manifest", "--manifest", dest="manifest", type=pathlib.Path, required=True)
        parser.add_argument("--route", choices=ROUTES)
    elif command == "development-overlay":
        parser.add_argument("action", choices=("build","install","status","rollback")); parser.add_argument("--manifest", type=pathlib.Path, required=True)
        parser.add_argument("--output", type=pathlib.Path)
    return parser


def main() -> int:
    command = pathlib.Path(sys.argv[0]).name
    if command == "development_workflow.py":
        if len(sys.argv) < 2: raise Failure("development command required")
        command, sys.argv = sys.argv[1], [sys.argv[0], *sys.argv[2:]]
    args = parser_for(command).parse_args()
    if command == "render-development-tree": result = {"manifest": str(render(pathlib.Path(args.source), pathlib.Path(args.output), args.module_version, args.allow_dirty))}
    elif command == "development-preflight":
        result = {"classification":"source-development", "kernels":kernel_identities(args.kernel), "tools":tool_inventory(), "moduleName":CANONICAL_MODULE}
    elif command == "development-install": result = install(args)
    elif command == "development-enroll": result = enroll(args.manifest, args.route, args.kernel, args.remove)
    elif command == "development-module": result = lifecycle_action(args.action, args.manifest, args.live_output)
    elif command == "development-status": result = lifecycle_status(args.manifest)
    elif command == "development-endpoint": result = lifecycle_status(args.manifest)["endpoint"]
    elif command == "development-rollback": result = rollback(args.record)
    elif command == "development-route": result = route_action(args.action, args.manifest, args.route)
    elif command == "development-overlay": result = overlay_action(args.action, args.manifest, args.output)
    else: raise Failure(f"unknown development command: {command}")
    sys.stdout.buffer.write(canonical(result)); return 0


if __name__ == "__main__":
    try: raise SystemExit(main())
    except (Failure, OSError, subprocess.SubprocessError) as error:
        print(f"development workflow failed: {error}", file=sys.stderr); raise SystemExit(2)
