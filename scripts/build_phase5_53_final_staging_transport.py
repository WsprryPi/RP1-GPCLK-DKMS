#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build the final Phase 5.53 staging transport from explicit closures."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import pathlib
import tarfile
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
STAGE = "phase5.53-4e7a64a0ca35"
PREFIX = f"/home/pi/gate-d-inputs/{STAGE}/"
ENVELOPE = ROOT / "release/gate-d-pre-root-bootstrap-envelope-phase5.53-final-v1.json"
SAME_VERSION = ROOT / "release/gate-d-same-version-transition-phase5.53-final-v1.json"
SEALED_ENVELOPE = f"control-set/release/{ENVELOPE.name}"
SEALED_SAME_VERSION = SAME_VERSION.name
PRODUCT = "rp1-gpclk-dkms-0.0.0-phase5.53.tar.gz"
QUALIFICATION = "rp1-gpclk-dkms-qualification-0.0.0-phase5.53.tar.gz"
ARCHIVES = {
    PRODUCT: "rp1-gpclk-dkms-0.0.0-phase5.53",
    QUALIFICATION: "rp1-gpclk-dkms-qualification-0.0.0-phase5.53",
}


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def build(release_dir: pathlib.Path, output: pathlib.Path,
          manifest_path: pathlib.Path) -> dict:
    if output.exists() or manifest_path.exists():
        raise ValueError("output already exists")
    envelope = json.loads(ENVELOPE.read_text())
    declared = {item["path"]: item["sha256"] for item in envelope["inputFiles"]}
    release_paths = {item["path"] for item in envelope["releaseInputs"]}
    transition_paths = {item["sourcePath"] for item in envelope["transitionFiles"]}
    administrator = envelope["administrator"]["path"]
    if (len(declared) != 63 or len(release_paths) != 8 or len(transition_paths) != 54 or
            set(declared) != release_paths | transition_paths | {administrator}):
        raise ValueError("final input ownership graph differs")
    with tempfile.TemporaryDirectory() as temporary:
        tree = pathlib.Path(temporary)
        stage = tree / STAGE
        stage.mkdir()
        owners = []
        for raw, expected in sorted(declared.items()):
            if not raw.startswith(PREFIX):
                raise ValueError("input outside final staging root")
            relative = raw.removeprefix(PREFIX)
            destination = stage / relative
            if raw == administrator:
                continue
            if raw in release_paths:
                source = release_dir / pathlib.PurePosixPath(raw).name
                owner = "release-directory"
                source_id = f"release-directory/{source.name}"
            elif raw in transition_paths:
                source = ROOT / relative.removeprefix("control-set/")
                owner = "repository-control-set"
                source_id = f"repository/{relative.removeprefix('control-set/')}"
            else:
                raise ValueError(f"unowned final input: {raw}")
            if source.is_symlink() or not source.is_file():
                raise ValueError(f"missing final input: {source}")
            payload = source.read_bytes()
            if sha(payload) != expected:
                raise ValueError(f"final input hash differs: {raw}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(payload)
            owners.append({"path": raw, "owner": owner, "source": source_id,
                           "sha256": expected})
        archive_counts = {}
        for archive_name, archive_root in ARCHIVES.items():
            archive_path = stage / archive_name
            with tarfile.open(archive_path, "r:gz") as archive:
                members = archive.getmembers()
                names = [item.name.rstrip("/") for item in members]
                if (len(names) != len(set(names)) or
                        any(not (item.isdir() or item.isfile()) for item in members)):
                    raise ValueError("split archive type graph differs")
                files = [item for item in members if item.isfile()]
                archive_counts[archive_name] = len(files)
                for member in members:
                    pure = pathlib.PurePosixPath(member.name)
                    if (pure.is_absolute() or ".." in pure.parts or not pure.parts or
                            pure.parts[0] != archive_root):
                        raise ValueError("unsafe split archive member")
                    destination = stage / "extracted" / pure
                    if member.isdir():
                        destination.mkdir(parents=True, exist_ok=True)
                        continue
                    stream = archive.extractfile(member)
                    if stream is None:
                        raise ValueError("unreadable split archive member")
                    payload = stream.read()
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(payload)
                    raw = PREFIX + "extracted/" + pure.as_posix()
                    owners.append({"path": raw, "owner": "split-archive-member",
                                   "source": f"{archive_name}:{pure.as_posix()}",
                                   "sha256": sha(payload)})
        if archive_counts != {PRODUCT: 54, QUALIFICATION: 33}:
            raise ValueError("split archive file counts differ")
        for raw, expected in declared.items():
            path = tree / raw.removeprefix("/home/pi/gate-d-inputs/")
            if path.is_symlink() or not path.is_file() or sha(path.read_bytes()) != expected:
                raise ValueError(f"materialized final input differs: {raw}")
        for source, name, owner in (
                (ENVELOPE, SEALED_ENVELOPE, "separately-sealed-envelope"),
                (SAME_VERSION, SEALED_SAME_VERSION, "separately-sealed-same-version-plan")):
            destination = stage / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source.read_bytes())
            owners.append({"path": PREFIX + name, "owner": owner,
                           "source": f"repository/release/{name}",
                           "sha256": sha(destination.read_bytes())})
        files = sorted(path for path in tree.rglob("*") if path.is_file())
        directories = sorted((path for path in tree.rglob("*") if path.is_dir()),
                             key=lambda path: path.relative_to(tree).as_posix())
        if len(files) != 151 or len({item["path"] for item in owners}) != 151:
            raise ValueError("complete final staging closure differs")
        with tarfile.open(output, "w", format=tarfile.USTAR_FORMAT) as archive:
            for directory in directories:
                relative = directory.relative_to(tree)
                name = relative.as_posix()
                info = tarfile.TarInfo(name.rstrip("/") + "/")
                info.type = tarfile.DIRTYPE
                info.mode = 0o700
                info.uid = info.gid = 1000
                info.uname = info.gname = "pi"
                info.mtime = 0
                archive.addfile(info)
            for path in files:
                payload = path.read_bytes()
                info = tarfile.TarInfo(path.relative_to(tree).as_posix())
                info.size = len(payload)
                info.mode = 0o600
                info.uid = info.gid = 1000
                info.uname = info.gname = "pi"
                info.mtime = 0
                archive.addfile(info, io.BytesIO(payload))
        result = {"SPDX-License-Identifier": "MIT", "schemaVersion": 1,
                  "kind": "gate-d-phase5.53-final-staging-source-map",
                  "transportSha256": sha(output.read_bytes()),
                  "regularFileCount": 151,
                  "directoryCountIncludingRoot": len(directories),
                  "sources": sorted(owners, key=lambda item: item["path"])}
        manifest_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-directory", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--manifest", type=pathlib.Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.release_directory, args.output, args.manifest), sort_keys=True))


if __name__ == "__main__":
    main()
