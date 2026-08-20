#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the frozen Phase 5.53 archives at their literal boundaries."""
from __future__ import annotations

import ast
import hashlib
import json
import os
import pathlib
import tarfile

PRODUCT = "032a0ca214427ebb6115b933042e7135f03c2ed6ce4f5c399686b2cf61395a76"
QUALIFICATION = "916a5522e3998ae43f203c217fedce90ad8d4c2d52ae0bd4491407e3cf17211d"
PRODUCT_NAME = "rp1-gpclk-dkms-0.0.0-phase5.53.tar.gz"
QUALIFICATION_NAME = "rp1-gpclk-dkms-qualification-0.0.0-phase5.53.tar.gz"
release_raw = os.environ.get("PHASE5_53_WRAPUP_RELEASE_DIRECTORY")
if not release_raw:
    print("Phase 5.53 bounded wrap-up archive readiness: SKIP (release directory not supplied)")
    raise SystemExit(0)
release = pathlib.Path(release_raw).resolve()
metadata = json.loads((release / "release-metadata.json").read_text())
provenance = json.loads((release / "PROVENANCE.json").read_text())


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(name: str, expected_hash: str, expected_count: int,
            expected_files: list[str], expected_mtime: int) -> tuple[set[str], dict[str, bytes]]:
    path = release / name
    assert digest(path) == expected_hash
    with tarfile.open(path, "r:gz") as source:
        members = source.getmembers()
        assert len(members) == expected_count
        raw_names = [member.name for member in members]
        canonical = [member.name.rstrip("/") for member in members]
        assert raw_names == sorted(raw_names)
        assert len(canonical) == len(set(canonical))
        roots = {pathlib.PurePosixPath(member.name).parts[0] for member in members}
        assert len(roots) == 1
        root = next(iter(roots))
        relative = [member.name.removeprefix(root + "/") for member in members]
        assert relative == expected_files
        payloads: dict[str, bytes] = {}
        for member, rel in zip(members, relative, strict=True):
            pure = pathlib.PurePosixPath(member.name)
            assert not pure.is_absolute() and ".." not in pure.parts and rel
            assert member.isfile() and not member.issym() and not member.islnk()
            assert member.uid == member.gid == 0
            assert member.uname == member.gname == ""
            assert member.mode in {0o644, 0o755}
            assert member.mtime == expected_mtime
            # Python tarfile uses a PAX path record only for names that exceed
            # the USTAR name field. No other extended metadata is accepted.
            assert set(member.pax_headers) <= {"path"}
            if "path" in member.pax_headers:
                assert member.pax_headers == {"path": member.name}
                assert len(member.name.encode()) > 100
            extracted = source.extractfile(member)
            assert extracted is not None
            payloads[rel] = extracted.read()
        return set(relative), payloads


product_expected = sorted(provenance["sourceFiles"])
qualification_expected = sorted(provenance["qualificationSourceFiles"])
product_names, product = inspect(PRODUCT_NAME, PRODUCT, 54, product_expected,
                                 metadata["sourceDateEpoch"])
qualification_names, qualification = inspect(
    QUALIFICATION_NAME, QUALIFICATION, 33, qualification_expected,
    metadata["qualificationSourceDateEpoch"])
assert not product_names & qualification_names
assert metadata["archiveSha256"] == PRODUCT
assert metadata["qualificationArchiveSha256"] == QUALIFICATION
assert {"dkms.conf", "Kbuild", "scripts/rp1-gpclk-admin.py",
        "overlays/rp1-gpclk-gpio4.dts",
        "overlays/rp1-gpclk-gpio20.dts"} <= product_names
assert not any(path.startswith("scripts/gate_d_") for path in product_names)
assert any(path.startswith("scripts/gate_d_") for path in qualification_names)
assert not {"dkms.conf", "Kbuild"} & qualification_names

admin = product["scripts/rp1-gpclk-admin.py"].decode()
for argv in ('["dkms", "add", "-m", PACKAGE, "-v", VERSION]',
             '["dkms", "build", "-m", PACKAGE, "-v", VERSION, "-k", kernel]',
             '["dkms", "install", "-m", PACKAGE, "-v", VERSION, "-k", kernel]'):
    assert argv in admin
assert "for overlay_name in ROUTES.values():" in admin
for prohibited in ('["modprobe"', '["dtoverlay"', '["reboot"'):
    assert prohibited not in admin

# The ordinary product installation is closed and conventional, but the final
# qualification control closure is not: it supplies a schema-4 identity to the
# frozen product administrator, which accepts schemas 1 through 3 only.
root = pathlib.Path(__file__).resolve().parents[1]
identity = json.loads((root / "docs/evidence/gate-d-phase5.53-final-qualification-install-identity.json").read_text())
assert identity["schemaVersion"] == 4
assert "schema not in {1, 2, 3}" in admin

layout = json.loads(qualification["release/qualification-layout-v1.json"])
archive_paths = {item["path"] for item in layout["artifacts"]
                 if item["kind"] in {"archive", "archive-tree"}}
assert archive_paths <= qualification_names
destinations = [item["destination"] for item in layout["artifacts"]]
assert len(destinations) == len(set(destinations))

# Resolve imports among qualification-owned Python consumers from the archive,
# never from the repository checkout.
python_files = {path for path in qualification if path.endswith(".py")}
module_paths = {pathlib.PurePosixPath(path).stem: path for path in python_files}
for path in sorted(python_files):
    tree = ast.parse(qualification[path], filename=path)
    for node in ast.walk(tree):
        names = ([alias.name.split(".")[0] for alias in node.names]
                 if isinstance(node, ast.Import) else
                 [node.module.split(".")[0]]
                 if isinstance(node, ast.ImportFrom) and node.module else [])
        for imported in names:
            if imported.startswith("gate_d_"):
                assert imported in module_paths, f"{path}: missing {imported}.py"

print("Phase 5.53 bounded wrap-up archive assessment: PASS "
      "(literal inventories valid; schema-4 lifecycle consumer blocked)")
