#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Independently validate a generated RP1-GPCLK-DKMS release unit."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import tarfile

ROOT = pathlib.Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise SystemExit(message)


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(output: pathlib.Path, allow_development: bool) -> None:
    if output.is_symlink() or not output.is_dir():
        fail("release unit must be a real directory")
    layout = json.loads((ROOT / "release/release-layout-v1.json").read_text())
    expected = {item["path"] for item in layout["artifacts"] if item["kind"] == "generated" and item["destination"] == "release-download"}
    expected |= {"rp1-gpclk-gpio4.dtbo", "rp1-gpclk-gpio20.dtbo", "rp1-gpclk-compatibility-manifest.json", "PROVENANCE.json", "SHA256SUMS", "release-metadata.json"}
    actual = {path.name for path in output.iterdir()}
    if actual != expected:
        fail(f"release artifact set differs: missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
    checksum_lines = (output / "SHA256SUMS").read_text().splitlines()
    checksum_names = []
    for line in checksum_lines:
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9][A-Za-z0-9._+-]*)", line)
        if not match:
            fail("malformed checksum line")
        checksum_names.append(match.group(2))
        if sha256(output / match.group(2)) != match.group(1):
            fail(f"checksum mismatch: {match.group(2)}")
    if checksum_names != sorted(expected - {"SHA256SUMS"}):
        fail("checksum coverage or order differs")
    metadata = json.loads((output / "release-metadata.json").read_text())
    provenance = json.loads((output / "PROVENANCE.json").read_text())
    compatibility = json.loads((output / "rp1-gpclk-compatibility-manifest.json").read_text())
    for value in (metadata, provenance):
        for key in ("release", "sourceCommit", "uapiAbi", "uapiHeaderSha256", "archiveSha256", "compatibilityManifestSha256", "overlays", "tools"):
            if value.get(key) != metadata.get(key):
                fail(f"provenance and metadata differ at {key}")
    if metadata["release"] != layout["release"] or metadata["expectedTag"] != layout["expectedTag"]:
        fail("release/tag metadata differs from layout")
    if not metadata["publishable"] and not allow_development:
        fail("release unit is marked non-publishable")
    if metadata["publishable"] != (metadata["tagPresent"] and not metadata["dirtySource"]):
        fail("invalid publishable state")
    archive = output / metadata["archive"]
    if archive.name != f"{layout['package']}-{layout['release']}.tar.gz" or sha256(archive) != metadata["archiveSha256"]:
        fail("archive identity differs")
    if compatibility["module"] != {"name": layout["module"], "release": layout["release"], "sourceCommit": metadata["sourceCommit"],
                                    "sourceArchiveSha256": metadata["archiveSha256"], "uapiAbi": layout["uapiAbi"],
                                    "uapiHeaderSha256": metadata["uapiHeaderSha256"]}:
        fail("compatibility module identity differs")
    if compatibility["defaultState"] != "Unavailable" or compatibility["entries"]:
        fail("Phase 5.2 compatibility manifest must be populated deny-by-default with no positive entries")
    schema = json.loads((ROOT / "schema/rp1-gpclk-compatibility-manifest-v1.schema.json").read_text())
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema" or schema.get("additionalProperties") is not False:
        fail("compatibility schema identity differs")
    if set(compatibility) != set(schema["required"]) or compatibility["schemaVersion"] != 1:
        fail("compatibility manifest does not satisfy required top-level schema fields")
    try:
        import jsonschema
    except ImportError:
        pass
    else:
        jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(compatibility)
    prefix = f"{layout['package']}-{layout['release']}/"
    tracked = subprocess.check_output(["git", "-C", str(ROOT), "ls-files", "-z"]).decode().split("\0")
    with tarfile.open(archive, "r:gz") as source:
        members = source.getmembers()
        names = [member.name.removeprefix(prefix) for member in members]
        if not members or any(not member.name.startswith(prefix) or member.name.startswith("/") or ".." in pathlib.PurePosixPath(member.name).parts for member in members):
            fail("unsafe archive root or member")
        if names != sorted(names) or len(names) != len(set(names)):
            fail("archive member order/uniqueness differs")
        required = {"Kbuild", "Makefile", "dkms.conf", "include/uapi/linux/rp1_gpclk.h", "release/release-layout-v1.json",
                    "scripts/rp1-gpclk-lifecycle.sh", "scripts/rp1-gpclk-diagnostics.py", "docs/operator/signing.md",
                    "scripts/rp1-gpclk-admin.py", "release/installation-model-v1.json",
                    "release/overlay-contract-v1.json",
                    f"docs/releases/{layout['release']}-security.md", f"docs/releases/{layout['release']}-behavior.md",
                    "overlays/rp1-gpclk-gpio4.dts", "overlays/rp1-gpclk-gpio20.dts"}
        if not required <= set(names):
            fail(f"archive lacks required inputs: {sorted(required-set(names))}")
        for member in members:
            if not member.isfile() or member.issym() or member.islnk() or member.uid or member.gid or member.uname or member.gname:
                fail(f"unsafe archive metadata: {member.name}")
            if member.mtime != metadata["sourceDateEpoch"] or member.mode not in {0o644, 0o755}:
                fail(f"nondeterministic archive metadata: {member.name}")
            rel = member.name.removeprefix(prefix)
            if rel in tracked and source.extractfile(member).read() != (ROOT / rel).read_bytes():
                fail(f"archive byte mismatch: {rel}")
        uapi_member = source.getmember(prefix + "include/uapi/linux/rp1_gpclk.h")
        if hashlib.sha256(source.extractfile(uapi_member).read()).hexdigest() != metadata["uapiHeaderSha256"]:
            fail("archived UAPI hash differs")
    if sha256(output / "rp1-gpclk-compatibility-manifest.json") != metadata["compatibilityManifestSha256"]:
        fail("compatibility manifest hash differs")
    for route in ("GPIO4", "GPIO20"):
        lower = route.lower()
        if sha256(ROOT / f"overlays/rp1-gpclk-{lower}.dts") != metadata["overlays"][route]["sourceSha256"]:
            fail(f"{route} source hash differs")
        if sha256(output / f"rp1-gpclk-{lower}.dtbo") != metadata["overlays"][route]["dtboSha256"]:
            fail(f"{route} DTBO hash differs")
    ids = [item["id"] for item in layout["artifacts"]]
    if len(ids) != len(set(ids)) or any(item["owner"] == "" or item["destination"] == "" for item in layout["artifacts"]):
        fail("release installation inventory is incomplete or ambiguous")
    print(f"release unit validation: PASS ({metadata['release']}, publishable={str(metadata['publishable']).lower()})")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("release_directory", type=pathlib.Path)
    parser.add_argument("--allow-development", action="store_true")
    args = parser.parse_args()
    validate(args.release_directory.resolve(), args.allow_development)


if __name__ == "__main__":
    main()
