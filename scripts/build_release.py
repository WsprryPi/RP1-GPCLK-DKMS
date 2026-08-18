#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Generate the deterministic Phase 5.2 RP1-GPCLK-DKMS release unit."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import pathlib
import re
import shutil
import subprocess
import tarfile
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
LAYOUT_PATH = ROOT / "release/release-layout-v1.json"
KEY_SUFFIXES = {".key", ".pem", ".p12", ".pfx", ".der"}
SOURCE_RELEASE_EXACT = {
    "Kbuild", "LICENSE.md", "Makefile", "README.md", "SECURITY.md",
    "dkms.conf", "release/release-layout-v1.json", "uapi-identity.json",
    "scripts/build_release.py", "scripts/validate_release.py",
}
SOURCE_RELEASE_PATTERNS = ("LICENSES/*",)
VERSION_RE = re.compile(r'^#define RP1_GPCLK_MODULE_VERSION "([0-9A-Za-z][0-9A-Za-z._+-]*)"$', re.M)


def run(*args: str, cwd: pathlib.Path = ROOT) -> str:
    return subprocess.check_output(args, cwd=cwd, text=True, stderr=subprocess.STDOUT).strip()


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_write(path: pathlib.Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def load_layout() -> dict:
    value = json.loads(LAYOUT_PATH.read_text())
    required = {"package", "module", "release", "expectedTag", "uapiAbi", "artifacts"}
    if not required <= value.keys():
        raise SystemExit("release layout is incomplete")
    return value


def validate_versions(layout: dict) -> None:
    version_header = (ROOT / "include/rp1_gpclk/version.h").read_text()
    match = VERSION_RE.search(version_header)
    if not match or match.group(1) != layout["release"]:
        raise SystemExit("module metadata and release layout versions differ")
    dkms = (ROOT / "dkms.conf").read_text()
    if f'PACKAGE_VERSION="{layout["release"]}"' not in dkms:
        raise SystemExit("dkms.conf and release layout versions differ")
    if f'PACKAGE_NAME="{layout["package"]}"' not in dkms:
        raise SystemExit("dkms.conf and release layout package names differ")
    for note in ("security", "behavior"):
        path = ROOT / f"docs/releases/{layout['release']}-{note}.md"
        if not path.is_file() or layout["release"] not in path.read_text():
            raise SystemExit(f"missing or mismatched {note} release notes")
    identity = json.loads((ROOT / "uapi-identity.json").read_text())
    if identity.get("abi") != layout["uapiAbi"]:
        raise SystemExit("UAPI ABI and release layout differ")


def source_files(development: bool, layout: dict) -> tuple[list[pathlib.Path], bool]:
    dirty = bool(run("git", "status", "--porcelain", "--untracked-files=all"))
    if dirty and not development:
        raise SystemExit("refusing publishable output from a dirty worktree")
    listing = run("git", "ls-files", "--cached", "--others", "--exclude-standard", "-z")
    paths: list[pathlib.Path] = []
    for raw in listing.split("\0"):
        if not raw:
            continue
        rel = pathlib.Path(raw)
        posix = rel.as_posix()
        patterns = SOURCE_RELEASE_PATTERNS + tuple(
            item["path"] for item in layout["artifacts"]
            if item["kind"] in {"archive", "archive-tree"})
        if posix not in SOURCE_RELEASE_EXACT and not any(rel.match(pattern) for pattern in patterns):
            continue
        path = ROOT / rel
        if path.is_symlink() or not path.is_file():
            raise SystemExit(f"unsafe release input: {rel}")
        if path.suffix.lower() in KEY_SUFFIXES:
            raise SystemExit(f"prohibited key-like release input: {rel}")
        mode = path.stat().st_mode & 0o777
        if mode not in {0o644, 0o755}:
            raise SystemExit(f"unexpected release input mode {mode:04o}: {rel}")
        paths.append(rel)
    found = {path.as_posix() for path in paths}
    missing = SOURCE_RELEASE_EXACT - found
    if missing:
        raise SystemExit(f"missing source-release input: {sorted(missing)[0]}")
    for pattern in patterns:
        if not any(pathlib.PurePosixPath(name).match(pattern) for name in found):
            raise SystemExit(f"missing source-release pattern: {pattern}")
    return sorted(paths, key=lambda path: path.as_posix()), dirty


def tool_identity(command: str, version_args: tuple[str, ...]) -> dict:
    resolved = shutil.which(command)
    if not resolved:
        raise SystemExit(f"required tool unavailable: {command}")
    output = run(resolved, *version_args)
    return {"command": command, "version": output.splitlines()[0],
            "binarySha256": sha256(pathlib.Path(resolved)), "_resolved": resolved}


def build_dtbo(source: pathlib.Path, destination: pathlib.Path, dtc: str) -> None:
    text = source.read_text()
    text = re.sub(r"^#include <dt-bindings/clock/rp1.h>$", "", text, flags=re.M)
    text = re.sub(r"^#include <dt-bindings/mfd/rp1.h>$", "", text, flags=re.M)
    text = text.replace("RP1_CLK_GP0", "33").replace("RP1_DMA_DMA_TICK_TICK0", "0x30")
    if "#include" in text:
        raise SystemExit(f"unresolved overlay include in {source.name}")
    with tempfile.NamedTemporaryFile("w", suffix=".dts", delete=False) as preprocessed:
        preprocessed.write(text)
        temporary = pathlib.Path(preprocessed.name)
    try:
        warning_policy = ["-Wno-reg_format", "-Wno-unit_address_vs_reg", "-Wno-pci_device_reg",
                          "-Wno-pci_device_bus_num", "-Wno-simple_bus_reg", "-Wno-i2c_bus_reg",
                          "-Wno-spi_bus_reg", "-Wno-avoid_default_addr_size", "-Wno-avoid_unnecessary_addr_size",
                          "-Wno-unique_unit_address"]
        result = subprocess.run([dtc, *warning_policy, "-@", "-I", "dts", "-O", "dtb", "-o", str(destination), str(temporary)],
                                check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode or "warning" in result.stderr.lower():
            raise SystemExit(f"dtc failed or warned for {source.name}: {result.stderr.strip()}")
    finally:
        temporary.unlink(missing_ok=True)


def create_archive(path: pathlib.Path, files: list[pathlib.Path], prefix: str, epoch: int) -> None:
    with path.open("wb") as output:
        with gzip.GzipFile(filename="", mode="wb", fileobj=output, mtime=epoch, compresslevel=9) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
                for rel in files:
                    data = (ROOT / rel).read_bytes()
                    member = tarfile.TarInfo(f"{prefix}/{rel.as_posix()}")
                    member.size = len(data)
                    member.mtime = epoch
                    member.uid = member.gid = 0
                    member.uname = member.gname = ""
                    member.mode = 0o755 if data.startswith(b"#!") else 0o644
                    archive.addfile(member, io.BytesIO(data))


def generate(output: pathlib.Path, development: bool) -> None:
    layout = load_layout()
    validate_versions(layout)
    files, dirty = source_files(development, layout)
    commit = run("git", "rev-parse", "HEAD")
    epoch = int(run("git", "show", "-s", "--format=%ct", "HEAD"))
    tags = run("git", "tag", "--points-at", "HEAD").splitlines()
    tagged = layout["expectedTag"] in tags
    if not tagged and not development:
        raise SystemExit(f"HEAD lacks expected release tag {layout['expectedTag']}")
    publishable = not dirty and tagged
    if output.exists():
        if output.is_symlink() or not output.is_dir() or any(output.iterdir()):
            raise SystemExit("output must be a new or empty real directory")
    else:
        output.mkdir(parents=True, mode=0o755)
    dtc_identity = tool_identity("dtc", ("--version",))
    dtc_executable = dtc_identity.pop("_resolved")
    python_executable = pathlib.Path(os.path.realpath(os.sys.executable))
    python_identity = {"implementation": os.sys.implementation.name, "version": os.sys.version.splitlines()[0],
                       "binarySha256": sha256(python_executable)}
    try:
        archive_name = f"{layout['package']}-{layout['release']}.tar.gz"
        archive = output / archive_name
        create_archive(archive, files, f"{layout['package']}-{layout['release']}", epoch)
        overlay_hashes = {}
        for route in ("gpio4", "gpio20"):
            source = ROOT / f"overlays/rp1-gpclk-{route}.dts"
            dtbo = output / f"rp1-gpclk-{route}.dtbo"
            build_dtbo(source, dtbo, dtc_executable)
            overlay_hashes[route.upper()] = {"sourceSha256": sha256(source), "dtboSha256": sha256(dtbo)}
        uapi_hash = sha256(ROOT / "include/uapi/linux/rp1_gpclk.h")
        decisions = json.loads((ROOT / "release/compatibility-decisions-v1.json").read_text(encoding="utf-8"))
        compatibility = {
            "SPDX-License-Identifier": "MIT",
            "schemaVersion": 1,
            "manifestId": f"{layout['package']}-{layout['release']}-{commit}",
            "generatedAt": f"{run('git', 'show', '-s', '--format=%cI', 'HEAD')}",
            "module": {"name": layout["module"], "release": layout["release"], "sourceCommit": commit,
                       "sourceArchiveSha256": sha256(archive), "uapiAbi": layout["uapiAbi"], "uapiHeaderSha256": uapi_hash},
            "defaultState": "Unavailable",
            "entries": decisions["entries"]
        }
        compatibility_path = output / "rp1-gpclk-compatibility-manifest.json"
        json_write(compatibility_path, compatibility)
        dtc_identity["options"] = ["-Wno-reg_format", "-Wno-unit_address_vs_reg", "-Wno-pci_device_reg",
                                   "-Wno-pci_device_bus_num", "-Wno-simple_bus_reg", "-Wno-i2c_bus_reg",
                                   "-Wno-spi_bus_reg", "-Wno-avoid_default_addr_size", "-Wno-avoid_unnecessary_addr_size",
                                   "-Wno-unique_unit_address", "-@", "-I", "dts", "-O", "dtb"]
        tools = {"python": python_identity, "dtc": dtc_identity,
                 "tar": {"format": "PAX", "implementation": "Python tarfile"},
                 "gzip": {"implementation": "Python gzip", "compresslevel": 9, "filename": "", "mtime": epoch},
                 "overlayPreprocessor": {"implementation": "scripts/build_release.py fixed RP1 bindings", "RP1_CLK_GP0": 33, "RP1_DMA_DMA_TICK_TICK0": 48}}
        metadata = {
            "SPDX-License-Identifier": "MIT", "schemaVersion": 1, "package": layout["package"], "module": layout["module"],
            "release": layout["release"], "sourceCommit": commit, "expectedTag": layout["expectedTag"], "tagPresent": tagged,
            "dirtySource": dirty, "publishable": publishable, "sourceDateEpoch": epoch, "archive": archive_name,
            "archiveSha256": sha256(archive), "uapiAbi": layout["uapiAbi"], "uapiHeaderSha256": uapi_hash,
            "overlays": overlay_hashes, "compatibilityManifestSha256": sha256(compatibility_path),
            "compatibilitySchemaSha256": sha256(ROOT / "schema/rp1-gpclk-compatibility-manifest-v1.schema.json"),
            "releaseLayoutSha256": sha256(LAYOUT_PATH), "tools": tools
        }
        metadata_path = output / "release-metadata.json"
        json_write(metadata_path, metadata)
        provenance = dict(metadata)
        provenance.update({"generationCommand": "scripts/build_release.py OUTPUT [--development]", "sourceFiles": [path.as_posix() for path in files]})
        provenance_path = output / "PROVENANCE.json"
        json_write(provenance_path, provenance)
        distributable = sorted(path for path in output.iterdir() if path.name != "SHA256SUMS")
        (output / "SHA256SUMS").write_text("".join(f"{sha256(path)}  {path.name}\n" for path in distributable))
    except BaseException:
        for child in output.iterdir():
            if child.is_file() and not child.is_symlink():
                child.unlink()
        raise


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=pathlib.Path)
    parser.add_argument("--development", action="store_true", help="mark dirty or untagged output non-publishable")
    args = parser.parse_args()
    generate(args.output.resolve(), args.development)


if __name__ == "__main__":
    main()
