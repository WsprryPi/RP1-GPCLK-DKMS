#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Deterministically generate the Phase 5.43 Gate D control set."""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = ROOT / "docs/evidence/gate-d-live-target-snapshot-wspr5-v1.json"
SNAPSHOT_SHA256 = "d228a5fe8eaa52a2fa44d003947d51b2a3a6798e4535c0570c3836ab5b283b9a"
TEMPLATE_COMMIT = "3b0cc513db165127c59488b34b85242c746d7d22"
SOURCE_COMMIT = "aa92b0550acd66671fe1988510cf93987cd61c0a"
OLD_SOURCE_COMMIT = "5dc05b6e10cdb50c4f937b484fc92cf4469e54ab"
ARCHIVE_SHA256 = "a8a200d069ad433353a8812ef6a9a4c585b75a9f6af3d6501ac3672e90c997c3"
MODULE_SHA256 = "d7cfefc1cba02a92485f4cbdc8b1aa1109467a9a258f4f32773c2bd3ec18c0ae"
OLD_ARCHIVE_SHA256 = "a6baa472e907135b9066c6bbb2bceee6ec849025d7d7b157d93a45297f6c5f54"
OLD_MODULE_SHA256 = "44ec33c8dd6ae06eeb5476e43ffbc9f0359172c184b25a04d962c83fa4e4ed61"
OLD_ROOT_SUFFIX = "phase5.42-5dc05b6e10cd"
NEW_ROOT_SUFFIX = "phase5.43-aa92b0550acd"
CONTROL_NAMES = (
    "gate-d-route-compatibility-decision", "gate-d-target-operation-plan",
    "gate-d-qualification-bootstrap-plan", "gate-d-execution-instance",
    "gate-d-pre-root-bootstrap-envelope",
)
SOURCE_BY_NAME = {
    "gate-d-attempts": "scripts/gate_d_attempts.py",
    "gate-d-boot": "scripts/gate_d_boot.py",
    "gate-d-bootstrap": "scripts/gate_d_bootstrap.py",
    "gate-d-executor": "scripts/gate_d_outer.py",
    "gate-d-instance": "scripts/gate_d_instance.py",
    "gate-d-lifecycle": "scripts/gate_d_lifecycle.py",
    "gate-d-platform": "scripts/gate_d_platform.py",
    "gate-d-residue": "scripts/gate_d_residue.py",
    "gate-d-target-plan": "scripts/gate_d_target_plan.py",
    "gate_d_attempts.py": "scripts/gate_d_attempts.py",
    "gate_d_bootstrap.py": "scripts/gate_d_bootstrap.py",
    "gate_d_instance.py": "scripts/gate_d_instance.py",
    "gate_d_lifecycle.py": "scripts/gate_d_lifecycle.py",
    "gate_d_outer.py": "scripts/gate_d_outer.py",
    "gate_d_preroot.py": "scripts/gate_d_preroot.py",
    "gate_d_root.py": "scripts/gate_d_root.py",
    "gate_d_target_plan.py": "scripts/gate_d_target_plan.py",
    "lifecycle-policy": "scripts/lifecycle_policy.py",
    "rp1-gpclk-admin": "scripts/rp1-gpclk-admin.py",
    "rp1-gpclk-diagnostics": "scripts/rp1-gpclk-diagnostics.py",
}
COMPILED = {
    "gate-d-busy-injector": "c01d97301fcbad4266e6fd41c040f561da0c106affc28cf353455e4a071331dd",
    "gate-d-uapi-probe": "1ee335da403784a775efc049f49eb598e3541c625418b65015b322e29b0a1742",
}
RELEASE_NAMES = {
    "PROVENANCE.json", "SHA256SUMS", "release-metadata.json",
    "rp1-gpclk-compatibility-manifest.json",
    "rp1-gpclk-dkms-0.0.0-phase5.43.tar.gz",
    "rp1-gpclk-gpio20.dtbo", "rp1-gpclk-gpio4.dtbo",
}


def git_bytes(commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT)


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def pretty(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def transform(payload: bytes, replacements: dict[str, str]) -> bytes:
    text = payload.decode()
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode()


def source_hash_replacements() -> dict[str, str]:
    replacements = {}
    paths = set(SOURCE_BY_NAME.values()) | {
        "scripts/gate_d_preroot.py", "scripts/gate_d_bootstrap.py",
        "scripts/rp1-gpclk-admin.py", "scripts/rp1-gpclk-diagnostics.py",
    }
    for path in sorted(paths):
        old_path = path
        new_path = path.replace("phase5.42", "phase5.43")
        try:
            old_payload = git_bytes(OLD_SOURCE_COMMIT, old_path)
            new_payload = git_bytes(SOURCE_COMMIT, new_path)
        except subprocess.CalledProcessError:
            continue
        replacements[sha(old_payload)] = sha(new_payload)
    return replacements


def release_artifacts() -> dict[str, dict]:
    path = ROOT / "docs/evidence/gate-c-phase5.43-release-input-inventory.json"
    value = json.loads(path.read_text())
    if (value.get("host") != "wspr5" or value.get("release") != "0.0.0-phase5.43" or
            value.get("sourceCommit") != SOURCE_COMMIT or
            value.get("directory") != "/home/pi/gate-c-evidence/phase5.43-aa92b05"):
        raise ValueError("representative release-input inventory identity differs")
    artifacts = value.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != len(RELEASE_NAMES):
        raise ValueError("representative release-input inventory count differs")
    result = {item["name"]: item for item in artifacts}
    if set(result) != RELEASE_NAMES or len(result) != len(artifacts):
        raise ValueError("representative release-input inventory names differ")
    for item in result.values():
        if (item.get("type") != "file" or item.get("mode") != "0644" or
                item.get("owner") != "pi" or item.get("group") != "pi" or
                not isinstance(item.get("size"), int) or item["size"] <= 0 or
                len(item.get("sha256", "")) != 64):
            raise ValueError("representative release-input inventory record differs")
    return result


def package_records() -> tuple[list[dict], list[dict], list[dict], str]:
    if sha(SNAPSHOT_PATH.read_bytes()) != SNAPSHOT_SHA256:
        raise ValueError("canonical live-target snapshot identity differs")
    snapshot = json.loads(SNAPSHOT_PATH.read_text())
    predecessor = snapshot["packagePaths"]
    transitions, successor = [], []
    for item in predecessor:
        name = pathlib.PurePosixPath(item["path"]).name
        if item["type"] == "file":
            if item["path"].startswith("/usr/share/doc/"):
                successor_sha = sha(git_bytes(SOURCE_COMMIT, f"docs/operator/{name}"))
            elif name in COMPILED:
                successor_sha = COMPILED[name]
            else:
                successor_sha = sha(git_bytes(SOURCE_COMMIT, SOURCE_BY_NAME[name]))
            transitions.append({
                "path": item["path"], "type": "file",
                "predecessorSha256": item["sha256"], "successorSha256": successor_sha,
                "mode": item["mode"], "ownerUid": item["ownerUid"],
                "groupGid": item["groupGid"],
            })
            successor.append({
                "path": item["path"], "type": "file", "sha256": successor_sha,
                "mode": item["mode"], "ownerUid": item["ownerUid"],
                "groupGid": item["groupGid"],
            })
        else:
            transitions.append({
                "path": item["path"], "type": "symlink",
                "predecessorTarget": item["target"], "successorTarget": item["target"],
                "ownerUid": item["ownerUid"], "groupGid": item["groupGid"],
            })
            successor.append({
                "path": item["path"], "type": "symlink", "target": item["target"],
                "mode": item["mode"], "ownerUid": item["ownerUid"],
                "groupGid": item["groupGid"],
            })
    transitions.sort(key=lambda item: item["path"])
    successor.sort(key=lambda item: item["path"])
    return predecessor, transitions, successor, sha(canonical(successor))


def generate(output_root: pathlib.Path) -> list[pathlib.Path]:
    artifacts = release_artifacts()
    replacements = {
        OLD_ROOT_SUFFIX: NEW_ROOT_SUFFIX,
        "phase5.42": "phase5.43",
        "0.0.0-phase5.42": "0.0.0-phase5.43",
        OLD_SOURCE_COMMIT: SOURCE_COMMIT,
        OLD_ARCHIVE_SHA256: ARCHIVE_SHA256,
        OLD_MODULE_SHA256: MODULE_SHA256,
        "d5ba966d17d456a6f29e53baf53464e1fd53f9f8e31481da18f2221f1da2593d":
            "d5ba966d17d456a6f29e53baf53464e1fd53f9f8e31481da18f2221f1da2593d",
        **source_hash_replacements(),
    }
    stale_release_hashes = {
        "38cc463391df167950a7c282f17468d15b18494dab7dd6f4aef45fd3560a2fa4": "PROVENANCE.json",
        "72b811fe73fa86bece8af3d27a21bf2a4913cab276e92027e262fad5019d3fb0": "SHA256SUMS",
        "f99a36e17a8bbe9b68b6e034b1c37c0aa095ca6fb212d1180356d0dc353dbb5f": "release-metadata.json",
        "9ec395b87aacee77a75aeab6e069ba3e1dc5e6f5cd50be5e51a6f53a65a95779": "rp1-gpclk-compatibility-manifest.json",
    }
    replacements.update({old: artifacts[name]["sha256"] for old, name in stale_release_hashes.items()})
    replacements[sha(git_bytes(TEMPLATE_COMMIT,
        "release/gate-c-representative-build-manifest-phase5.42-v1.json"))] = sha(
        (ROOT / "release/gate-c-representative-build-manifest-phase5.43-v1.json").read_bytes())
    generated: list[tuple[str, str, pathlib.Path]] = []
    for name in CONTROL_NAMES:
        old = f"release/{name}-phase5.42-v1.json"
        new = f"release/{name}-phase5.43-v1.json"
        destination = output_root / new
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(transform(git_bytes(TEMPLATE_COMMIT, old), replacements))
        generated.append((old, new, destination))
    index_old = "release/gate-d-attempts-phase5.42-v1/index.json"
    index = json.loads(git_bytes(TEMPLATE_COMMIT, index_old))
    attempt_names = [record["file"] for record in index["attempts"]]
    for filename in [*attempt_names, "index.json"]:
        old = f"release/gate-d-attempts-phase5.42-v1/{filename}"
        new = f"release/gate-d-attempts-phase5.43-v1/{filename}"
        destination = output_root / new
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(transform(git_bytes(TEMPLATE_COMMIT, old), replacements))
        generated.append((old, new, destination))

    predecessor, transitions, package_paths, package_digest = package_records()
    inventory_old = "docs/evidence/gate-d-phase5.42-predecessor-package-inventory.json"
    inventory_new = "docs/evidence/gate-d-phase5.43-predecessor-package-inventory.json"
    inventory_path = output_root / inventory_new
    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    inventory_path.write_bytes(pretty({
        "SPDX-License-Identifier": "MIT", "schemaVersion": 1,
        "kind": "gate-d-predecessor-package-inventory", "host": "wspr5",
        "capturedFor": "0.0.0-phase5.43", "paths": predecessor,
    }))
    generated.append((inventory_old, inventory_new, inventory_path))
    identity = {
        "SPDX-License-Identifier": "MIT", "schemaVersion": 3,
        "kind": "rp1-gpclk-gate-d-qualification-install-identity",
        "release": "0.0.0-phase5.43", "sourceCommit": SOURCE_COMMIT,
        "archiveSha256": ARCHIVE_SHA256, "publishable": False,
        "tagPresent": False, "outputDisabled": True, "liveOutput": False,
        "purpose": "gate-d-representative-system-qualification",
        "packageTransitions": transitions,
    }
    identity_old = "docs/evidence/gate-d-phase5.42-qualification-install-identity.json"
    identity_new = "docs/evidence/gate-d-phase5.43-qualification-install-identity.json"
    identity_path = output_root / identity_new
    identity_path.parent.mkdir(parents=True, exist_ok=True)
    identity_path.write_bytes(pretty(identity))
    generated.append((identity_old, identity_new, identity_path))

    marker = {
        "SPDX-License-Identifier": "MIT", "schemaVersion": 1,
        "kind": "gate-d-qualification-root-identity",
        "rootPath": f"/home/pi/gate-d-qualification/{NEW_ROOT_SUFFIX}",
        "candidateRelease": "0.0.0-phase5.43", "sourceCommit": SOURCE_COMMIT,
    }
    marker_sha = sha(canonical(marker))
    for _, _, path in generated:
        value = json.loads(path.read_text())
        changed = False
        if isinstance(value, dict):
            for key in ("qualificationRoot", "proposedRoot"):
                if key in value:
                    if key == "proposedRoot": value[key]["marker"] = marker
                    value[key]["identitySha256" if key == "qualificationRoot" else "markerSha256"] = marker_sha
                    value[key]["path"] = marker["rootPath"]
                    changed = True
            if value.get("kind") == "gate-d-qualification-bootstrap-plan":
                value["schemaVersion"] = 4
                value["packagePaths"] = package_paths
                value["packagePathsSha256"] = package_digest
                changed = True
            if value.get("kind") == "gate-d-pre-root-bootstrap-envelope":
                snapshot = json.loads(SNAPSHOT_PATH.read_text())
                ledger = snapshot["administratorLedger"]
                value["schemaVersion"] = 5
                value["installedPackagePaths"] = package_paths
                value["packagePathsSha256"] = package_digest
                value["predecessorPackagePaths"] = predecessor
                value["predecessorPackagePathsSha256"] = snapshot["packagePathsSha256"]
                value["liveTargetSnapshotSha256"] = SNAPSHOT_SHA256
                value["priorTerminalState"] = {
                    "path": ledger["path"], "sha256": ledger["sha256"],
                    "status": ledger["status"],
                    "recoveryRequired": ledger["recoveryRequired"],
                    "liveOutput": ledger["liveOutput"],
                    "ownerUid": ledger["ownerUid"], "mode": ledger["mode"],
                    "archivePath": "/var/lib/rp1-gpclk-dkms/recovery/phase5.43-phase5.39-transaction-complete.json",
                    "archiveMode": "0400",
                }
                changed = True
            if value.get("kind") == "gate-d-representative-system-execution-instance":
                value["authorization"]["approved"] = True
                value["authorization"]["targetExecutionApproved"] = False
                value["authorization"]["approvalScope"] = (
                    "Offline Phase 5.43 construction and archived-tool validation only; "
                    "target lifecycle execution requires separate authorization."
                )
                value["executionReady"] = False
                changed = True
        if changed:
            path.write_bytes(pretty(value))

    # Close every cross-document hash edge. Each pass replaces the previous
    # identity of a generated node with its current identity; an acyclic graph
    # converges to stable bytes.
    old_hash = {new: sha(git_bytes(TEMPLATE_COMMIT, old)) for old, new, _ in generated}
    previous = dict(old_hash)
    for _ in range(32):
        current = {new: sha(path.read_bytes()) for _, new, path in generated}
        mapping = {previous[name]: current[name] for name in current if previous[name] != current[name]}
        if not mapping:
            break
        for _, _, path in generated:
            text = path.read_text()
            for old_sha, new_sha in mapping.items(): text = text.replace(old_sha, new_sha)
            path.write_text(text)
        previous = current
    else:
        raise RuntimeError("control-set hash closure did not converge")
    return [path for _, _, path in generated]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        with tempfile.TemporaryDirectory() as temporary:
            temp = pathlib.Path(temporary)
            generated = generate(temp)
            for path in generated:
                relative = path.relative_to(temp)
                expected = ROOT / relative
                if not expected.is_file() or expected.read_bytes() != path.read_bytes():
                    raise SystemExit(f"generated control differs: {relative}")
        print("Phase 5.43 control-set deterministic generation: PASS")
    else:
        generated = generate(ROOT)
        print(f"generated {len(generated)} Phase 5.43 control documents")


if __name__ == "__main__":
    main()
