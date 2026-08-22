#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Strictly validate a build_release_candidate.py artifact set."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import tarfile

VERSION = "1.1.1"
DEBIAN_VERSION = "1.1.1-1"
TAG = "v1.1.1"
PACKAGE = "rp1-gpclk-dkms"
QUALIFICATION = "rp1-gpclk-dkms-qualification"
FILES = {
    "COMPATIBILITY.json", "PRODUCT-INVENTORY.json", "QUALIFICATION.json",
    "TARGET-VERIFICATION.json", "release-metadata.json",
    f"{PACKAGE}_{DEBIAN_VERSION}_all.deb",
    f"{QUALIFICATION}-{VERSION}.tar.gz", "SHA256SUMS",
    "TRANSACTION-PLAN-deactivate-predecessor.json",
    "TRANSACTION-PLAN-install-inactive.json",
    "TRANSACTION-PLAN-select-gpio4.json",
    "TRANSACTION-PLAN-select-gpio20.json",
    "TRANSACTION-PLAN-restore-gpio4.json",
}


def fail(message: str) -> None:
    raise SystemExit(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        fail(f"invalid JSON {path.name}: {error}")
    if not isinstance(value, dict):
        fail(f"JSON root is not an object: {path.name}")
    return value


def safe_name(raw: str) -> str:
    name = raw.removeprefix("./").rstrip("/")
    value = PurePosixPath(name)
    if not name or value.is_absolute() or ".." in value.parts:
        fail(f"unsafe archive member: {raw}")
    return name


def tar_inventory(payload: bytes) -> tuple[list[dict], dict[str, bytes]]:
    records: list[dict] = []
    files: dict[str, bytes] = {}
    seen: set[str] = set()
    try:
        archive = tarfile.open(fileobj=io.BytesIO(payload), mode="r:*")
    except tarfile.TarError as error:
        fail(f"invalid tar payload: {error}")
    with archive:
        for member in archive.getmembers():
            name = safe_name(member.name)
            if name in seen:
                fail(f"duplicate archive member: {name}")
            seen.add(name)
            mode = stat.S_IMODE(member.mode)
            if member.isdir():
                kind, size, digest = "directory", 0, None
            elif member.isfile() and not member.issym() and not member.islnk():
                if mode not in {0o644, 0o755}:
                    fail(f"unexpected archive mode {mode:04o}: {name}")
                stream = archive.extractfile(member)
                if stream is None:
                    fail(f"unreadable archive member: {name}")
                content = stream.read()
                files[name] = content
                kind, size, digest = "file", len(content), sha256_bytes(content)
            else:
                fail(f"link or special archive member: {name}")
            record = {"path": name, "type": kind, "mode": f"{mode:04o}", "size": size}
            if digest is not None:
                record["sha256"] = digest
            records.append(record)
    return records, files


def ar_members(path: Path) -> dict[str, bytes]:
    data = path.read_bytes()
    if not data.startswith(b"!<arch>\n"):
        fail("product is not a Debian ar archive")
    offset, members = 8, {}
    while offset < len(data):
        if offset + 60 > len(data):
            fail("truncated ar header")
        header = data[offset:offset + 60]
        if header[58:60] != b"`\n":
            fail("invalid ar header")
        name = header[:16].decode("ascii").strip().rstrip("/")
        try:
            size = int(header[48:58].decode("ascii").strip())
        except (UnicodeDecodeError, ValueError):
            fail("invalid ar member size")
        start, end = offset + 60, offset + 60 + size
        if end > len(data) or name in members:
            fail("invalid or duplicate ar member")
        members[name] = data[start:end]
        offset = end + size % 2
    if set(members) != {"debian-binary", "control.tar.xz", "data.tar.xz"}:
        fail(f"unexpected Debian members: {sorted(members)}")
    if members["debian-binary"] != b"2.0\n":
        fail("unsupported Debian format")
    return members


def validate_checksums(root: Path) -> None:
    lines = (root / "SHA256SUMS").read_text().splitlines()
    expected = sorted(FILES - {"SHA256SUMS"})
    names = []
    for line in lines:
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9][A-Za-z0-9._+-]*)", line)
        if not match:
            fail("malformed checksum line")
        digest, name = match.groups()
        names.append(name)
        if name not in FILES or sha256(root / name) != digest:
            fail(f"checksum mismatch or unknown member: {name}")
    if names != expected:
        fail("checksum coverage or ordering differs")


def validate_product(root: Path, inventory: dict, metadata: dict) -> dict[str, bytes]:
    product = root / metadata["productPackage"]
    if product.name != f"{PACKAGE}_{DEBIAN_VERSION}_all.deb":
        fail("product filename differs")
    if sha256(product) != metadata["productPackageSha256"]:
        fail("product metadata hash differs")
    if inventory.get("packageSha256") != sha256(product):
        fail("product inventory hash differs")
    members = ar_members(product)
    control_records, control_files = tar_inventory(members["control.tar.xz"])
    data_records, data_files = tar_inventory(members["data.tar.xz"])
    if control_records != inventory.get("controlMembers") or data_records != inventory.get("dataMembers"):
        fail("Debian member inventory differs")
    control = control_files.get("control", b"").decode(errors="strict")
    fields = {}
    for line in control.splitlines():
        key, separator, value = line.partition(":")
        if separator and not line.startswith((" ", "\t")):
            fields[key] = value.strip()
    if (fields.get("Package"), fields.get("Version"), fields.get("Architecture")) != (PACKAGE, DEBIAN_VERSION, "all"):
        fail("Debian control identity differs")
    base = f"usr/src/{PACKAGE}-{VERSION}"
    required = {
        f"{base}/dkms.conf", f"{base}/Kbuild", f"{base}/Makefile",
        f"{base}/include/uapi/linux/rp1_gpclk.h",
        f"{base}/overlays/rp1-gpclk-gpio4.dts",
        f"{base}/overlays/rp1-gpclk-gpio20.dts",
        "usr/lib/rp1-gpclk-dkms/overlays/rp1-gpclk-gpio4.dtbo",
        "usr/lib/rp1-gpclk-dkms/overlays/rp1-gpclk-gpio20.dtbo",
    }
    if not required <= set(data_files):
        fail(f"required package members absent: {sorted(required-set(data_files))}")
    if any(any(term in name.lower() for term in ("qualification", "evidence", "target-verification")) for name in data_files):
        fail("qualification content leaked into product package")
    if f'PACKAGE_VERSION="{VERSION}"' not in data_files[f"{base}/dkms.conf"].decode():
        fail("installed DKMS version differs")
    return data_files


def validate(root: Path, expected_source_commit: str | None) -> dict:
    if root.is_symlink() or not root.is_dir():
        fail("candidate set must be a real directory")
    actual = {path.name for path in root.iterdir()}
    if actual != FILES:
        fail(f"candidate set differs: missing={sorted(FILES-actual)} extra={sorted(actual-FILES)}")
    if any(path.is_symlink() or not path.is_file() for path in root.iterdir()):
        fail("candidate set contains a symlink or non-file")
    validate_checksums(root)
    metadata = load_json(root / "release-metadata.json")
    inventory = load_json(root / "PRODUCT-INVENTORY.json")
    identity = load_json(root / "QUALIFICATION.json")
    compatibility = load_json(root / "COMPATIBILITY.json")
    plan = load_json(root / "TARGET-VERIFICATION.json")
    if (metadata.get("kind"), metadata.get("release"), metadata.get("debianVersion"), metadata.get("expectedTag")) != ("release-artifact-set", VERSION, DEBIAN_VERSION, TAG):
        fail("release metadata identity differs")
    source_commit = metadata.get("sourceCommit")
    if not isinstance(source_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        fail("invalid source commit")
    if expected_source_commit and source_commit != expected_source_commit:
        fail("source commit differs from expectation")
    if metadata.get("publishable") is not False or metadata.get("tagPresent") is not False:
        fail("preliminary candidate claims publication or tag identity")
    if inventory.get("kind") != "release-product-member-inventory" or inventory.get("debianVersion") != DEBIAN_VERSION:
        fail("product inventory identity differs")
    if sha256(root / "PRODUCT-INVENTORY.json") != metadata.get("productInventorySha256"):
        fail("product inventory sidecar hash differs")
    data_files = validate_product(root, inventory, metadata)
    uapi = data_files[f"usr/src/{PACKAGE}-{VERSION}/include/uapi/linux/rp1_gpclk.h"]
    gpio4 = data_files["usr/lib/rp1-gpclk-dkms/overlays/rp1-gpclk-gpio4.dtbo"]
    gpio20 = data_files["usr/lib/rp1-gpclk-dkms/overlays/rp1-gpclk-gpio20.dtbo"]
    expected_hashes = (sha256_bytes(uapi), sha256_bytes(gpio4), sha256_bytes(gpio20))
    if expected_hashes != (metadata.get("uapiSha256"), metadata.get("gpio4DtboSha256"), metadata.get("gpio20DtboSha256")):
        fail("installed UAPI or overlay identity differs")
    if (identity.get("kind"), identity.get("release"), identity.get("debianVersion"), identity.get("expectedTag"), identity.get("sourceCommit")) != ("release-qualification-identity", VERSION, DEBIAN_VERSION, TAG, source_commit):
        fail("qualification identity differs")
    if identity.get("productPackageSha256") != metadata.get("productPackageSha256") or identity.get("productInventorySha256") != metadata.get("productInventorySha256"):
        fail("qualification product identity differs")
    if (identity.get("uapiSha256"), identity.get("gpio4DtboSha256"), identity.get("gpio20DtboSha256")) != expected_hashes:
        fail("qualification installed identities differ")
    if identity.get("liveEligible") is not False or identity.get("targetVerificationAuthorized") is not False:
        fail("qualification identity exceeds offline scope")
    if sha256(root / "QUALIFICATION.json") != metadata.get("qualificationIdentitySha256"):
        fail("qualification identity sidecar hash differs")
    module = compatibility.get("module", {})
    if (compatibility.get("defaultState"), module.get("release"), module.get("sourceCommit"), module.get("uapiAbi"), module.get("uapiHeaderSha256")) != ("Unavailable", VERSION, source_commit, 2, expected_hashes[0]):
        fail("compatibility module identity differs")
    entries = compatibility.get("entries")
    if not isinstance(entries, list) or {entry.get("route") for entry in entries} != {"GPIO4", "GPIO20"}:
        fail("compatibility route inventory differs")
    if any(entry.get("state") != "Unavailable" or entry.get("liveEligible") is not False for entry in entries):
        fail("candidate compatibility is not fully fail-closed")
    if sha256(root / "COMPATIBILITY.json") != metadata.get("compatibilitySha256"):
        fail("compatibility sidecar hash differs")
    if (plan.get("kind"), plan.get("release"), plan.get("debianVersion"), plan.get("expectedTag")) != ("release-candidate-target-verification", VERSION, DEBIAN_VERSION, TAG):
        fail("target plan identity differs")
    if plan.get("authorized") is not False or plan.get("executed") is not False:
        fail("target plan claims authorization or execution")
    if plan.get("productPackageSha256") != metadata.get("productPackageSha256") or plan.get("productInventorySha256") != metadata.get("productInventorySha256") or plan.get("qualificationIdentitySha256") != metadata.get("qualificationIdentitySha256"):
        fail("target plan artifact identity differs")
    if any(plan.get("safety", {}).get(field) is not False for field in
           ("liveOutput", "endpointAcquire", "clockOrRateChange", "dma",
            "gpioOutput", "carrier", "sdrCapture", "transmissionOrRf")):
        fail("target plan exceeds hardware-free scope")
    if any(plan.get("safety", {}).get(field) is not True for field in
           ("bootChange", "reboot")):
        fail("route-validation plan omits boot transaction or reboot")
    if any(step.get("mutating") and not step.get("requiresAuthorization") for step in plan.get("steps", [])):
        fail("mutating target step lacks authorization gate")
    if sha256(root / "TARGET-VERIFICATION.json") != metadata.get("targetVerificationSha256"):
        fail("target plan sidecar hash differs")
    transaction_names = sorted(name for name in FILES if name.startswith("TRANSACTION-PLAN-"))
    if set(metadata.get("transactionPlans", {})) != set(transaction_names):
        fail("transaction plan inventory differs")
    for name in transaction_names:
        transaction = load_json(root / name)
        claimed = transaction.pop("planSha256", None)
        if claimed != sha256_bytes(canonical(transaction)):
            fail(f"transaction plan digest differs: {name}")
        if (transaction.get("kind"), transaction.get("sourceCommit"),
            transaction.get("qualificationArchiveSha256")) != (
                "rp1-gpclk-1.1.1-route-transaction", source_commit,
                sha256(root / metadata["qualificationArchive"])):
            fail(f"transaction plan identity differs: {name}")
        if metadata["transactionPlans"].get(name) != sha256(root / name):
            fail(f"transaction plan sidecar hash differs: {name}")
    qualification = root / metadata.get("qualificationArchive", "")
    if qualification.name != f"{QUALIFICATION}-{VERSION}.tar.gz" or sha256(qualification) != metadata.get("qualificationArchiveSha256"):
        fail("qualification archive identity differs")
    records, members = tar_inventory(qualification.read_bytes())
    prefix = f"{QUALIFICATION}-{VERSION}/"
    if any(not record["path"].startswith(prefix) for record in records):
        fail("qualification archive root differs")
    normalized = [{**record, "path": record["path"].removeprefix(prefix)} for record in records]
    if normalized != metadata.get("qualificationMemberInventory"):
        fail("qualification archive member inventory differs")
    if sha256_bytes(canonical(normalized)) != metadata.get("qualificationMemberInventorySha256"):
        fail("qualification canonical inventory hash differs")
    for name in ("COMPATIBILITY.json", "PRODUCT-INVENTORY.json", "QUALIFICATION.json", "TARGET-VERIFICATION.json"):
        archived = members.get(prefix + name)
        if archived != (root / name).read_bytes():
            fail(f"qualification sidecar byte mismatch: {name}")
    print(json.dumps({"release": VERSION, "sourceCommit": source_commit,
                      "productSha256": metadata["productPackageSha256"],
                      "qualificationSha256": metadata["qualificationArchiveSha256"],
                      "status": "PASS"}, sort_keys=True))
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate_directory", type=Path)
    parser.add_argument("--expect-source-commit")
    args = parser.parse_args()
    validate(args.candidate_directory.resolve(), args.expect_source_commit)


if __name__ == "__main__":
    main()
