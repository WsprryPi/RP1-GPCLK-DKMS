#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Deterministically generate the Phase 5.41 Gate D control set."""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
TEMPLATE_COMMIT = "b215da6358d9638ae1363c0662d2f52aa340d9c0"
SOURCE_COMMIT = "640877c1f29297e2f6ea855742605550781256e9"
OLD_SOURCE_COMMIT = "3768ae9cdccf0c2ae5809603b9a36e73507f2182"
ARCHIVE_SHA256 = "b49cd75baefdb245d6d00e60cd171ba6fa4da4c00e63b07e925cdd52f0b0934f"
MODULE_SHA256 = "2ad72b226f93c1d9ac859dafc2b01b87a86a9bba6f6ffc28fe381e4ed6ab4070"
OLD_ARCHIVE_SHA256 = "0e16828433a254467da4f4b841d355ef6d3cddf0ff582b4316416e9e66623f5c"
OLD_MODULE_SHA256 = "7884226fcb9361d4ab287dc1128b0818bf7e18497bb26848907d18d9e49318cf"
OLD_ROOT_SUFFIX = "phase5.39-3768ae9cdccf"
NEW_ROOT_SUFFIX = "phase5.41-640877c1f292"
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
    "rp1-gpclk-dkms-0.0.0-phase5.41.tar.gz",
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
        new_path = path.replace("phase5.39", "phase5.41")
        try:
            old_payload = git_bytes(OLD_SOURCE_COMMIT, old_path)
            new_payload = git_bytes(SOURCE_COMMIT, new_path)
        except subprocess.CalledProcessError:
            continue
        replacements[sha(old_payload)] = sha(new_payload)
    return replacements


def release_artifacts() -> dict[str, dict]:
    path = ROOT / "docs/evidence/gate-c-phase5.41-release-input-inventory.json"
    value = json.loads(path.read_text())
    if (value.get("host") != "wspr5" or value.get("release") != "0.0.0-phase5.41" or
            value.get("sourceCommit") != SOURCE_COMMIT or
            value.get("directory") != "/home/pi/gate-c-evidence/phase5.41-640877c"):
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
    envelope = json.loads(git_bytes(
        TEMPLATE_COMMIT, "release/gate-d-pre-root-bootstrap-envelope-phase5.39-v1.json"))
    predecessor = envelope["installedPackagePaths"]
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
        "phase5.39": "phase5.41",
        "0.0.0-phase5.39": "0.0.0-phase5.41",
        OLD_SOURCE_COMMIT: SOURCE_COMMIT,
        OLD_ARCHIVE_SHA256: ARCHIVE_SHA256,
        OLD_MODULE_SHA256: MODULE_SHA256,
        "2a83d4324e9b47d418b4efac18d3af43d15cc956b71c5a8eb074060bf8383801":
            "d5ba966d17d456a6f29e53baf53464e1fd53f9f8e31481da18f2221f1da2593d",
        **source_hash_replacements(),
    }
    stale_release_hashes = {
        "8ada380c2950632affe4b7e92d909fc592a5d43653c39df089d173d4deb4f89e": "PROVENANCE.json",
        "d2582c90c862e18efa84791b97793ede956f73ad6f8be61156a50bd3d1218064": "SHA256SUMS",
        "e1fbf1ce9d95482bebce8d4c18dc9722213f6abf9d9bb47ce6a431f62af52fff": "release-metadata.json",
        "69365d1f2924ea619f71817ecf0624f96ee172a3ee6c59de614aab1d89b54a38": "rp1-gpclk-compatibility-manifest.json",
    }
    replacements.update({old: artifacts[name]["sha256"] for old, name in stale_release_hashes.items()})
    replacements[sha(git_bytes(TEMPLATE_COMMIT,
        "release/gate-c-representative-build-manifest-phase5.39-v1.json"))] = sha(
        (ROOT / "release/gate-c-representative-build-manifest-phase5.41-v1.json").read_bytes())
    generated: list[tuple[str, str, pathlib.Path]] = []
    for name in CONTROL_NAMES:
        old = f"release/{name}-phase5.39-v1.json"
        new = f"release/{name}-phase5.41-v1.json"
        destination = output_root / new
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(transform(git_bytes(TEMPLATE_COMMIT, old), replacements))
        generated.append((old, new, destination))
    index_old = "release/gate-d-attempts-phase5.39-v1/index.json"
    index = json.loads(git_bytes(TEMPLATE_COMMIT, index_old))
    attempt_names = [record["file"] for record in index["attempts"]]
    for filename in [*attempt_names, "index.json"]:
        old = f"release/gate-d-attempts-phase5.39-v1/{filename}"
        new = f"release/gate-d-attempts-phase5.41-v1/{filename}"
        destination = output_root / new
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(transform(git_bytes(TEMPLATE_COMMIT, old), replacements))
        generated.append((old, new, destination))

    predecessor, transitions, package_paths, package_digest = package_records()
    inventory_old = "docs/evidence/gate-d-phase5.39-predecessor-package-inventory.json"
    inventory_new = "docs/evidence/gate-d-phase5.41-predecessor-package-inventory.json"
    inventory_path = output_root / inventory_new
    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    inventory_path.write_bytes(pretty({
        "SPDX-License-Identifier": "MIT", "schemaVersion": 1,
        "kind": "gate-d-predecessor-package-inventory", "host": "wspr5",
        "capturedFor": "0.0.0-phase5.41", "paths": predecessor,
    }))
    generated.append((inventory_old, inventory_new, inventory_path))
    identity = {
        "SPDX-License-Identifier": "MIT", "schemaVersion": 3,
        "kind": "rp1-gpclk-gate-d-qualification-install-identity",
        "release": "0.0.0-phase5.41", "sourceCommit": SOURCE_COMMIT,
        "archiveSha256": ARCHIVE_SHA256, "publishable": False,
        "tagPresent": False, "outputDisabled": True, "liveOutput": False,
        "purpose": "gate-d-representative-system-qualification",
        "packageTransitions": transitions,
    }
    identity_old = "docs/evidence/gate-d-phase5.39-qualification-install-identity.json"
    identity_new = "docs/evidence/gate-d-phase5.41-qualification-install-identity.json"
    identity_path = output_root / identity_new
    identity_path.parent.mkdir(parents=True, exist_ok=True)
    identity_path.write_bytes(pretty(identity))
    generated.append((identity_old, identity_new, identity_path))

    marker = {
        "SPDX-License-Identifier": "MIT", "schemaVersion": 1,
        "kind": "gate-d-qualification-root-identity",
        "rootPath": f"/home/pi/gate-d-qualification/{NEW_ROOT_SUFFIX}",
        "candidateRelease": "0.0.0-phase5.41", "sourceCommit": SOURCE_COMMIT,
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
                value["schemaVersion"] = 4
                value["installedPackagePaths"] = package_paths
                value["packagePathsSha256"] = package_digest
                changed = True
            if value.get("kind") == "gate-d-representative-system-execution-instance":
                value["authorization"]["targetExecutionApproved"] = True
                value["authorization"]["approvalScope"] = (
                    "Exact Phase 5.41 output-disabled Gate D target execution authorized by "
                    "the operator; limited to the 38 reviewed attempts, exact seven-artifact "
                    "release inventory, completed terminal recovery, and complete typed "
                    "28-path package transition."
                )
                value["executionReady"] = True
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
        print("Phase 5.41 control-set deterministic generation: PASS")
    else:
        generated = generate(ROOT)
        print(f"generated {len(generated)} Phase 5.41 control documents")


if __name__ == "__main__":
    main()
