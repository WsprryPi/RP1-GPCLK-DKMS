#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build deterministic release sidecars and the separate qualification archive."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
LAYOUT = ROOT / "release/qualification-layout-v2.json"
VERSION = "1.0.0"
DEBIAN_VERSION = "1.0.0-1"
TAG = "v1.0.0"
PACKAGE = "rp1-gpclk-dkms"
QUALIFICATION = "rp1-gpclk-dkms-qualification"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def pretty(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def ar_members(path: Path) -> dict[str, bytes]:
    data = path.read_bytes()
    if not data.startswith(b"!<arch>\n"):
        raise ValueError("product is not a Debian ar archive")
    offset = 8
    members: dict[str, bytes] = {}
    while offset < len(data):
        if offset + 60 > len(data):
            raise ValueError("truncated ar header")
        header = data[offset:offset + 60]
        if header[58:60] != b"`\n":
            raise ValueError("invalid ar member header")
        name = header[:16].decode("ascii").strip().rstrip("/")
        try:
            size = int(header[48:58].decode("ascii").strip())
        except ValueError as error:
            raise ValueError("invalid ar member size") from error
        start = offset + 60
        end = start + size
        if end > len(data) or name in members:
            raise ValueError("invalid or duplicate ar member")
        members[name] = data[start:end]
        offset = end + (size % 2)
    if set(members) != {"debian-binary", "control.tar.xz", "data.tar.xz"}:
        raise ValueError(f"unexpected Debian members: {sorted(members)}")
    if members["debian-binary"] != b"2.0\n":
        raise ValueError("unsupported Debian archive version")
    return members


def safe_name(raw: str) -> str:
    name = raw.removeprefix("./").rstrip("/")
    path = PurePosixPath(name)
    if not name or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"unsafe archive member: {raw}")
    return name


def read_tar(payload: bytes) -> tuple[list[dict], dict[str, bytes]]:
    records: list[dict] = []
    files: dict[str, bytes] = {}
    seen: set[str] = set()
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:xz") as archive:
        for member in archive.getmembers():
            name = safe_name(member.name)
            if name in seen:
                raise ValueError(f"duplicate tar member: {name}")
            seen.add(name)
            mode = stat.S_IMODE(member.mode)
            if member.isdir():
                kind = "directory"
                digest = None
                size = 0
            elif member.isfile():
                if mode not in {0o644, 0o755}:
                    raise ValueError(f"unexpected file mode {mode:04o}: {name}")
                stream = archive.extractfile(member)
                if stream is None:
                    raise ValueError(f"unreadable member: {name}")
                content = stream.read()
                files[name] = content
                kind = "file"
                digest = sha256_bytes(content)
                size = len(content)
            else:
                raise ValueError(f"links and special members are prohibited: {name}")
            record = {"path": name, "type": kind, "mode": f"{mode:04o}", "size": size}
            if digest is not None:
                record["sha256"] = digest
            records.append(record)
    return records, files


def control_fields(files: dict[str, bytes]) -> dict[str, str]:
    raw = files.get("control")
    if raw is None:
        raise ValueError("Debian control file is absent")
    fields: dict[str, str] = {}
    for line in raw.decode().splitlines():
        if not line or line.startswith((" ", "\t")):
            continue
        key, separator, value = line.partition(":")
        if separator:
            fields[key] = value.strip()
    return fields


def validate_product(path: Path) -> tuple[dict, dict[str, bytes]]:
    members = ar_members(path)
    control_records, control_files = read_tar(members["control.tar.xz"])
    data_records, data_files = read_tar(members["data.tar.xz"])
    fields = control_fields(control_files)
    if (fields.get("Package"), fields.get("Version"), fields.get("Architecture")) != (
        PACKAGE, DEBIAN_VERSION, "all"
    ):
        raise ValueError("Debian control identity differs")
    required = {
        "usr/src/rp1-gpclk-dkms-1.0.0/dkms.conf",
        "usr/src/rp1-gpclk-dkms-1.0.0/Kbuild",
        "usr/src/rp1-gpclk-dkms-1.0.0/Makefile",
        "usr/src/rp1-gpclk-dkms-1.0.0/include/uapi/linux/rp1_gpclk.h",
        "usr/src/rp1-gpclk-dkms-1.0.0/overlays/rp1-gpclk-gpio4.dts",
        "usr/src/rp1-gpclk-dkms-1.0.0/overlays/rp1-gpclk-gpio20.dts",
        "usr/lib/rp1-gpclk-dkms/overlays/rp1-gpclk-gpio4.dtbo",
        "usr/lib/rp1-gpclk-dkms/overlays/rp1-gpclk-gpio20.dtbo",
    }
    missing = required - set(data_files)
    if missing:
        raise ValueError(f"required product members absent: {sorted(missing)}")
    allowed_roots = ("usr/src/rp1-gpclk-dkms-1.0.0/", "usr/lib/rp1-gpclk-dkms/", "usr/share/doc/rp1-gpclk-dkms/")
    for name in data_files:
        if not name.startswith(allowed_roots):
            raise ValueError(f"unexpected product file root: {name}")
        if any(term in name.lower() for term in ("qualification", "evidence", "gate_d", "target-verification")):
            raise ValueError(f"qualification content in product: {name}")
    dkms = data_files["usr/src/rp1-gpclk-dkms-1.0.0/dkms.conf"].decode()
    if 'PACKAGE_VERSION="1.0.0"' not in dkms:
        raise ValueError("installed DKMS version differs")
    inventory = {
        "SPDX-License-Identifier": "MIT",
        "schemaVersion": 1,
        "kind": "release-product-member-inventory",
        "package": PACKAGE,
        "debianVersion": DEBIAN_VERSION,
        "architecture": "all",
        "packageSha256": sha256(path),
        "arMembers": sorted(members),
        "controlMembers": control_records,
        "dataMembers": data_records,
    }
    inventory["canonicalInventorySha256"] = sha256_bytes(canonical({
        "controlMembers": control_records, "dataMembers": data_records
    }))
    return inventory, data_files


def compatibility(commit: str, epoch_iso: str, product_hash: str, data: dict[str, bytes]) -> dict:
    value = json.loads((ROOT / "release/compatibility-decisions-v1.json").read_text())
    entries = value["entries"]
    for entry in entries:
        entry["state"] = "Unavailable"
        entry["liveEligible"] = False
        entry["reason"] = (
            "Historical development evidence does not bind the exact 1.0.0-1 package; "
            "final-candidate target verification and live-output qualification are absent."
        )
    return {
        "SPDX-License-Identifier": "MIT", "schemaVersion": 1,
        "manifestId": f"rp1-gpclk-dkms-1.0.0-{commit}", "generatedAt": epoch_iso,
        "module": {
            "name": "rp1_gpclk_dkms", "release": VERSION, "sourceCommit": commit,
            "sourceArchiveSha256": product_hash, "uapiAbi": 1,
            "uapiHeaderSha256": sha256_bytes(data["usr/src/rp1-gpclk-dkms-1.0.0/include/uapi/linux/rp1_gpclk.h"]),
        },
        "defaultState": "Unavailable", "entries": entries,
    }


def target_plan(product_hash: str, inventory_hash: str, identity_hash: str,
                uapi_hash: str, gpio4_hash: str, gpio20_hash: str) -> dict:
    return {
        "SPDX-License-Identifier": "MIT", "schemaVersion": 1,
        "kind": "release-candidate-target-verification", "release": VERSION,
        "debianVersion": DEBIAN_VERSION, "expectedTag": TAG,
        "productPackageSha256": product_hash,
        "productInventorySha256": inventory_hash,
        "qualificationIdentitySha256": identity_hash,
        "installedIdentities": {"uapiSha256": uapi_hash, "gpio4DtboSha256": gpio4_hash,
                                "gpio20DtboSha256": gpio20_hash},
        "authorized": False, "executed": False,
        "physicalSafety": {
            "si5351PathDisconnected": "fresh-operator-confirmation-required",
            "antennaOrTransmitterDisconnected": "fresh-operator-confirmation-required"
        },
        "steps": [
            {"id":"read-only-preflight","argv":["/usr/bin/python3","scripts/release_candidate_target.py","preflight","--expect-version","0.0.0~phase5.54-2"],"mutating":False,"requiresAuthorization":False},
            {"id":"validated-transfer","argv":["/usr/bin/sha256sum","--check","SHA256SUMS"],"mutating":False,"requiresAuthorization":False},
            {"id":"inactive-upgrade","argv":["/usr/bin/sudo","/usr/bin/dpkg","--install","rp1-gpclk-dkms_1.0.0-1_all.deb"],"mutating":True,"requiresAuthorization":True},
            {"id":"verify-inactive-install","argv":["/usr/bin/python3","scripts/release_candidate_target.py","verify-inactive","--expect-version",DEBIAN_VERSION],"mutating":False,"requiresAuthorization":True},
            {"id":"gpio4-output-disabled-lifecycle","argv":["/usr/bin/python3","scripts/release_candidate_target.py","route","--route","gpio4","--execute"],"mutating":True,"requiresAuthorization":True},
            {"id":"gpio20-output-disabled-lifecycle","argv":["/usr/bin/python3","scripts/release_candidate_target.py","route","--route","gpio20","--execute"],"mutating":True,"requiresAuthorization":True},
            {"id":"complete-removal-residue-audit","argv":["/usr/bin/python3","scripts/release_candidate_target.py","remove-audit","--execute"],"mutating":True,"requiresAuthorization":True},
            {"id":"reinstall-final-package","argv":["/usr/bin/sudo","/usr/bin/dpkg","--install","rp1-gpclk-dkms_1.0.0-1_all.deb"],"mutating":True,"requiresAuthorization":True},
            {"id":"verify-final-inactive-baseline","argv":["/usr/bin/python3","scripts/release_candidate_target.py","verify-inactive","--expect-version",DEBIAN_VERSION],"mutating":False,"requiresAuthorization":True},
        ],
        "safety": {"liveOutput":False,"clockOrRateChange":False,"dma":False,"gpioOutput":False,
                   "bootChange":False,"reboot":False,"transmissionOrRf":False},
    }


def add_bytes(archive: tarfile.TarFile, name: str, data: bytes, epoch: int, mode: int) -> None:
    member = tarfile.TarInfo(name)
    member.size = len(data)
    member.mtime = epoch
    member.uid = member.gid = 0
    member.uname = member.gname = ""
    member.mode = mode
    archive.addfile(member, io.BytesIO(data))


def build_qualification(path: Path, generated: dict[str, bytes], layout: dict, epoch: int) -> list[dict]:
    prefix = f"{QUALIFICATION}-{VERSION}"
    members: list[tuple[str, bytes, int]] = []
    for name in layout["generatedMembers"]:
        members.append((name, generated[name], 0o644))
    for name in layout["sourceMembers"]:
        source = ROOT / name
        if source.is_symlink() or not source.is_file():
            raise ValueError(f"unsafe qualification source: {name}")
        content = source.read_bytes()
        mode = 0o755 if content.startswith(b"#!") else 0o644
        members.append((name, content, mode))
    names = [name for name, _, _ in members]
    if len(names) != len(set(names)):
        raise ValueError("duplicate qualification member")
    members.sort(key=lambda item: item[0])
    inventory = [{"path": name, "type": "file", "mode": f"{mode:04o}",
                  "size": len(content), "sha256": sha256_bytes(content)}
                 for name, content, mode in members]
    with path.open("wb") as output:
        with gzip.GzipFile(filename="", mode="wb", fileobj=output, mtime=epoch, compresslevel=9) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
                for name, content, mode in members:
                    add_bytes(archive, f"{prefix}/{name}", content, epoch, mode)
    return inventory


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--product", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    product = args.product.resolve()
    output = args.output.resolve()
    if git("status", "--porcelain", "--untracked-files=all"):
        raise SystemExit("refusing release artifacts from a dirty worktree")
    commit = git("rev-parse", "HEAD")
    epoch = int(git("show", "-s", "--format=%ct", "HEAD"))
    epoch_iso = git("show", "-s", "--format=%cI", "HEAD")
    if output.exists():
        if output.is_symlink() or not output.is_dir() or any(output.iterdir()):
            raise SystemExit("output must be a new or empty real directory")
    else:
        output.mkdir(parents=True, mode=0o755)
    inventory, product_files = validate_product(product)
    product_hash = inventory["packageSha256"]
    inventory_bytes = pretty(inventory)
    layout = json.loads(LAYOUT.read_text())
    if layout["release"] != VERSION or layout["expectedTag"] != TAG:
        raise SystemExit("qualification layout release differs")
    uapi_hash = sha256_bytes(product_files["usr/src/rp1-gpclk-dkms-1.0.0/include/uapi/linux/rp1_gpclk.h"])
    gpio4_hash = sha256_bytes(product_files["usr/lib/rp1-gpclk-dkms/overlays/rp1-gpclk-gpio4.dtbo"])
    gpio20_hash = sha256_bytes(product_files["usr/lib/rp1-gpclk-dkms/overlays/rp1-gpclk-gpio20.dtbo"])
    identity = {
        "SPDX-License-Identifier":"MIT", "schemaVersion":1,
        "kind":"release-qualification-identity", "release":VERSION,
        "debianVersion":DEBIAN_VERSION, "expectedTag":TAG, "sourceCommit":commit,
        "productPackage":f"rp1-gpclk-dkms_{DEBIAN_VERSION}_all.deb",
        "productPackageSha256":product_hash,
        "productInventorySha256":sha256_bytes(inventory_bytes),
        "uapiSha256":uapi_hash, "gpio4DtboSha256":gpio4_hash,
        "gpio20DtboSha256":gpio20_hash, "liveEligible":False,
        "targetVerificationAuthorized":False,
    }
    identity_bytes = pretty(identity)
    compatibility_value = compatibility(commit, epoch_iso, product_hash, product_files)
    generated = {
        "PRODUCT-INVENTORY.json": inventory_bytes,
        "QUALIFICATION.json": identity_bytes,
        "COMPATIBILITY.json": pretty(compatibility_value),
    }
    plan = target_plan(product_hash, sha256_bytes(inventory_bytes), sha256_bytes(identity_bytes),
                       uapi_hash, gpio4_hash, gpio20_hash)
    generated["TARGET-VERIFICATION.json"] = pretty(plan)
    product_destination = output / f"rp1-gpclk-dkms_{DEBIAN_VERSION}_all.deb"
    shutil.copyfile(product, product_destination)
    for name, content in generated.items():
        (output / name).write_bytes(content)
    qualification_path = output / f"{QUALIFICATION}-{VERSION}.tar.gz"
    qualification_inventory = build_qualification(qualification_path, generated, layout, epoch)
    metadata = {
        "SPDX-License-Identifier":"MIT", "schemaVersion":1,
        "kind":"release-artifact-set", "release":VERSION, "debianVersion":DEBIAN_VERSION,
        "expectedTag":TAG, "sourceCommit":commit, "tagPresent":TAG in git("tag", "--points-at", "HEAD").splitlines(),
        "publishable":False, "productPackage":product_destination.name,
        "productPackageSha256":sha256(product_destination),
        "productInventorySha256":sha256(output / "PRODUCT-INVENTORY.json"),
        "qualificationArchive":qualification_path.name,
        "qualificationArchiveSha256":sha256(qualification_path),
        "qualificationMemberInventory":qualification_inventory,
        "qualificationMemberInventorySha256":sha256_bytes(canonical(qualification_inventory)),
        "compatibilitySha256":sha256(output / "COMPATIBILITY.json"),
        "qualificationIdentitySha256":sha256(output / "QUALIFICATION.json"),
        "targetVerificationSha256":sha256(output / "TARGET-VERIFICATION.json"),
        "uapiSha256":uapi_hash, "gpio4DtboSha256":gpio4_hash, "gpio20DtboSha256":gpio20_hash,
        "sourceDateEpoch":epoch,
    }
    (output / "release-metadata.json").write_bytes(pretty(metadata))
    distributable = sorted(path for path in output.iterdir() if path.name != "SHA256SUMS")
    (output / "SHA256SUMS").write_text("".join(f"{sha256(path)}  {path.name}\n" for path in distributable))
    print(json.dumps({"release":VERSION,"sourceCommit":commit,"productSha256":product_hash,
                      "qualificationSha256":sha256(qualification_path)}, sort_keys=True))


if __name__ == "__main__":
    main()
