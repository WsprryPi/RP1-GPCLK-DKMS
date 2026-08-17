#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Deterministically generate the snapshot-bound Phase 5.45 Gate D controls."""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import tempfile

import gate_d_attempts
import generate_phase5_43_control_set as predecessor_generator

ROOT = pathlib.Path(__file__).resolve().parents[1]
OLD_RELEASE = "0.0.0-phase5.43"
RELEASE = "0.0.0-phase5.45"
OLD_COMMIT = "aa92b0550acd66671fe1988510cf93987cd61c0a"
COMMIT = "4b50db7868b7fe5ca9d830f51cd404c250192188"
OLD_SUFFIX = "phase5.43-aa92b0550acd"
SUFFIX = "phase5.45-4b50db7868b7"
NAMESPACE = SUFFIX
SNAPSHOT = ROOT / "docs/evidence/gate-d-live-target-snapshot-wspr5-phase5.45-v1.json"
BUILD = ROOT / "release/gate-c-representative-build-manifest-phase5.45-v1.json"
INVENTORY = ROOT / "docs/evidence/gate-c-phase5.45-release-input-inventory.json"
CONTROL_NAMES = (
    "gate-d-route-compatibility-decision", "gate-d-target-operation-plan",
    "gate-d-qualification-bootstrap-plan", "gate-d-execution-instance",
    "gate-d-pre-root-bootstrap-envelope",
)


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def file_sha(path: pathlib.Path) -> str:
    return sha(path.read_bytes())


def pretty(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def git_bytes(commit: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT)


def replace(value: object, replacements: dict[str, str]) -> object:
    text = json.dumps(value, sort_keys=True)
    for old, new in replacements.items():
        text = text.replace(old, new)
    return json.loads(text)


def source_replacements() -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(set(predecessor_generator.SOURCE_BY_NAME.values())):
        result[sha(git_bytes(OLD_COMMIT, path))] = sha(git_bytes(COMMIT, path))
    return result


def successor_packages(snapshot: dict, build: dict) -> tuple[list[dict], list[dict]]:
    compiled = {
        "gate-d-busy-injector": build["result"]["busyInjectorSha256"],
        "gate-d-uapi-probe": build["result"]["uapiProbeSha256"],
    }
    successor, transitions = [], []
    for item in snapshot["packagePaths"]:
        name = pathlib.PurePosixPath(item["path"]).name
        common = {key: item[key] for key in ("path", "type", "mode", "ownerUid", "groupGid")}
        if item["type"] == "symlink":
            current = {**common, "target": item["target"]}
            transition = {"path": item["path"], "type": "symlink",
                          "predecessorTarget": item["target"],
                          "successorTarget": item["target"],
                          "ownerUid": item["ownerUid"], "groupGid": item["groupGid"]}
        else:
            if item["path"].startswith("/usr/share/doc/"):
                new_hash = sha(git_bytes(COMMIT, f"docs/operator/{name}"))
            elif name in compiled:
                new_hash = compiled[name]
            else:
                new_hash = sha(git_bytes(COMMIT, predecessor_generator.SOURCE_BY_NAME[name]))
            current = {**common, "sha256": new_hash}
            transition = {"path": item["path"], "type": "file",
                          "predecessorSha256": item["sha256"],
                          "successorSha256": new_hash, "mode": item["mode"],
                          "ownerUid": item["ownerUid"], "groupGid": item["groupGid"]}
        successor.append(current)
        transitions.append(transition)
    return successor, transitions


def generate(output_root: pathlib.Path) -> list[pathlib.Path]:
    snapshot = json.loads(SNAPSHOT.read_text())
    if file_sha(SNAPSHOT) != "66208586a112792e91185a7ce67d5952427dc218fb8a392ac1bfb221ed51e4c8":
        raise ValueError("Phase 5.45 canonical snapshot differs")
    build = json.loads(BUILD.read_text())
    inventory = json.loads(INVENTORY.read_text())
    artifacts = {item["name"]: item for item in inventory["artifacts"]}
    old_inventory = json.loads((ROOT / "docs/evidence/gate-c-phase5.43-release-input-inventory.json").read_text())
    old_artifacts = {item["name"]: item for item in old_inventory["artifacts"]}
    replacements = {
        OLD_SUFFIX: SUFFIX, OLD_RELEASE: RELEASE, "phase5.43": "phase5.45",
        OLD_COMMIT: COMMIT,
        "a8a200d069ad433353a8812ef6a9a4c585b75a9f6af3d6501ac3672e90c997c3": build["candidate"]["archiveSha256"],
        "d7cfefc1cba02a92485f4cbdc8b1aa1109467a9a258f4f32773c2bd3ec18c0ae": build["result"]["moduleSha256"],
        file_sha(ROOT / "release/gate-c-representative-build-manifest-phase5.43-v1.json"): file_sha(BUILD),
        "d228a5fe8eaa52a2fa44d003947d51b2a3a6798e4535c0570c3836ab5b283b9a": file_sha(SNAPSHOT),
        **source_replacements(),
    }
    for old_name, old_item in old_artifacts.items():
        new_name = old_name.replace("phase5.43", "phase5.45")
        replacements[old_item["sha256"]] = artifacts[new_name]["sha256"]

    with tempfile.TemporaryDirectory() as temporary:
        old_root = pathlib.Path(temporary)
        predecessor_generator.generate(old_root)
        controls = {}
        for name in CONTROL_NAMES:
            old_path = old_root / f"release/{name}-phase5.43-v1.json"
            controls[name] = replace(json.loads(old_path.read_text()), replacements)

    route = controls["gate-d-route-compatibility-decision"]
    build_hash = file_sha(BUILD)
    route["candidate"]["representativeBuildManifestSha256"] = build_hash
    route["evidence"].update({
        "kernelRelease": snapshot["kernel"]["release"],
        "kernelConfigSha256": snapshot["kernel"]["configSha256"],
        "moduleSymversSha256": snapshot["kernel"]["moduleSymversSha256"],
        "moduleSha256": build["result"]["moduleSha256"],
        "representativeBuildEvidenceManifestSha256": build_hash,
    })
    for entry in route["routes"]:
        entry["reason"] = ("Exact Phase 5.45 representative build and canonical inactive "
                           "wspr5 snapshot support Compatible-unqualified output-disabled planning; "
                           "fresh byte-identical recapture remains required before authorization.")

    packages, transitions = successor_packages(snapshot, build)
    marker = {"SPDX-License-Identifier": "MIT", "schemaVersion": 1,
              "kind": "gate-d-qualification-root-identity",
              "rootPath": f"/home/pi/gate-d-qualification/{SUFFIX}",
              "candidateRelease": RELEASE, "sourceCommit": COMMIT}
    marker_hash = sha(canonical(marker))
    bootstrap = controls["gate-d-qualification-bootstrap-plan"]
    bootstrap["packagePaths"] = packages
    bootstrap["packagePathsSha256"] = sha(canonical(packages))
    bootstrap["qualificationRoot"].update(path=marker["rootPath"], identitySha256=marker_hash)

    identity = {"SPDX-License-Identifier": "MIT", "schemaVersion": 3,
                "kind": "rp1-gpclk-gate-d-qualification-install-identity",
                "release": RELEASE, "sourceCommit": COMMIT,
                "archiveSha256": build["candidate"]["archiveSha256"],
                "publishable": False, "tagPresent": False, "outputDisabled": True,
                "liveOutput": False, "purpose": "gate-d-representative-system-qualification",
                "packageTransitions": transitions}
    identity_rel = "docs/evidence/gate-d-phase5.45-qualification-install-identity.json"
    identity_path = output_root / identity_rel
    identity_path.parent.mkdir(parents=True, exist_ok=True)
    identity_path.write_bytes(pretty(identity))

    inventory_rel = "docs/evidence/gate-d-phase5.45-predecessor-package-inventory.json"
    inventory_path = output_root / inventory_rel
    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    inventory_path.write_bytes(pretty({"SPDX-License-Identifier": "MIT", "schemaVersion": 1,
        "kind": "gate-d-predecessor-package-inventory", "host": "wspr5",
        "capturedFor": RELEASE, "liveTargetSnapshotSha256": file_sha(SNAPSHOT),
        "paths": snapshot["packagePaths"]}))

    route_rel = "release/gate-d-route-compatibility-decision-phase5.45-v1.json"
    route_path = output_root / route_rel
    route_path.parent.mkdir(parents=True, exist_ok=True)
    route_path.write_bytes(pretty(route))

    bootstrap_rel = "release/gate-d-qualification-bootstrap-plan-phase5.45-v1.json"
    bootstrap_path = output_root / bootstrap_rel
    bootstrap_path.write_bytes(pretty(bootstrap))

    plan = controls["gate-d-target-operation-plan"]
    plan["qualificationRoot"].update(path=marker["rootPath"], identitySha256=marker_hash)
    plan["qualificationBootstrap"].update(path=bootstrap_rel, sha256=file_sha(bootstrap_path))
    plan_path = output_root / "release/gate-d-target-operation-plan-phase5.45-v1.json"
    plan_path.write_bytes(pretty(plan))

    instance = controls["gate-d-execution-instance"]
    instance["schemaVersion"] = 5
    instance["qualificationRoot"].update(path=marker["rootPath"], identitySha256=marker_hash)
    instance["authorization"].update(
        approved=True, targetExecutionApproved=True,
        approvalScope=("Operator-authorized exact Phase 5.45 output-disabled Gate D scope "
                       "committed at d25abbf877fb889435b16e0b7d033291d0388af5; limited to "
                       "the 38 indexed namespaced attempts, ten ready rows, exact snapshot, "
                       "release inputs, predecessor and successor inventories, authenticated "
                       "schema-5 transition, recovery, and mandatory prohibitions."))
    instance["executionReady"] = True
    instance["executionPolicy"].update(
        attemptPathNamespace=NAMESPACE,
        routeDecision=route_rel, routeDecisionSha256=file_sha(route_path),
        targetPlan="release/gate-d-target-operation-plan-phase5.45-v1.json",
        targetPlanSha256=file_sha(plan_path),
        qualificationBootstrap=bootstrap_rel,
        qualificationBootstrapSha256=file_sha(bootstrap_path),
        attemptIndex="release/gate-d-attempts-phase5.45-v1/index.json")
    for row in instance["rows"]:
        row["evidenceDirectory"] = f"gate-d/runs/{NAMESPACE}/{row['id']}"

    attempts = gate_d_attempts.generate(instance, plan)
    attempt_dir = output_root / "release/gate-d-attempts-phase5.45-v1"
    attempt_dir.mkdir(parents=True, exist_ok=True)
    index_records = []
    for document in attempts:
        filename = f"{document['operationId']}.json"
        path = attempt_dir / filename
        path.write_bytes(pretty(document))
        index_records.append({"file": filename, "operationId": document["operationId"],
                              "sha256": file_sha(path)})
    index = {"SPDX-License-Identifier": "MIT", "schemaVersion": 2,
             "kind": "gate-d-attempt-index", "attemptCount": 38,
             "qualificationRoot": instance["qualificationRoot"],
             "executors": {
                 "attemptGenerator": {"path": "scripts/gate_d_attempts.py",
                                      "sha256": sha(git_bytes(COMMIT, "scripts/gate_d_attempts.py"))},
                 "permanentExecutor": {"path": "scripts/gate_d_outer.py",
                                       "sha256": sha(git_bytes(COMMIT, "scripts/gate_d_outer.py"))}},
             "attempts": index_records}
    index_path = attempt_dir / "index.json"
    index_path.write_bytes(pretty(index))
    instance["executionPolicy"]["attemptIndexSha256"] = file_sha(index_path)
    instance_path = output_root / "release/gate-d-execution-instance-phase5.45-v1.json"
    instance_path.write_bytes(pretty(instance))

    envelope = controls["gate-d-pre-root-bootstrap-envelope"]
    envelope["proposedRoot"].update(path=marker["rootPath"], marker=marker,
                                     markerSha256=marker_hash)
    envelope["installedPackagePaths"] = packages
    envelope["packagePathsSha256"] = sha(canonical(packages))
    envelope["predecessorPackagePaths"] = snapshot["packagePaths"]
    envelope["predecessorPackagePathsSha256"] = snapshot["packagePathsSha256"]
    envelope["liveTargetSnapshotSha256"] = file_sha(SNAPSHOT)
    ledger = snapshot["administratorLedger"]
    envelope["priorTerminalState"] = {
        "path": ledger["path"], "sha256": ledger["sha256"], "status": ledger["status"],
        "recoveryRequired": False, "liveOutput": False, "ownerUid": ledger["ownerUid"],
        "mode": ledger["mode"],
        "archivePath": "/var/lib/rp1-gpclk-dkms/recovery/phase5.45-phase5.43-transaction-complete.json",
        "archiveMode": "0400"}
    roles = {"rp1-gpclk-dkms-0.0.0-phase5.45.tar.gz": "archive",
             "rp1-gpclk-gpio4.dtbo": "gpio4Dtbo", "rp1-gpclk-gpio20.dtbo": "gpio20Dtbo",
             "rp1-gpclk-compatibility-manifest.json": "compatibilityManifest",
             "PROVENANCE.json": "provenance", "release-metadata.json": "releaseMetadata",
             "SHA256SUMS": "checksums"}
    stage = f"/home/pi/gate-d-inputs/{SUFFIX}"
    envelope["releaseInputs"] = [{"path": f"{stage}/{name}", "role": roles[name],
                                  "sha256": artifacts[name]["sha256"]} for name in roles]
    transition_paths = [identity_path, BUILD, *sorted(attempt_dir.glob("*.json")),
                        route_path, plan_path, bootstrap_path, instance_path]
    transition_files = []
    for path in transition_paths:
        relative = path.relative_to(output_root) if path.is_relative_to(output_root) else path.relative_to(ROOT)
        transition_files.append({"sourcePath": f"{stage}/control-set/{relative.as_posix()}",
                                 "destination": relative.as_posix(), "sha256": file_sha(path),
                                 "mode": "0400"})
    envelope["transitionFiles"] = sorted(transition_files, key=lambda item: item["destination"])
    identity_source = next(item["sourcePath"] for item in envelope["transitionFiles"]
                           if item["destination"] == identity_rel)
    envelope["qualificationIdentity"] = {"path": identity_source,
                                           "sha256": file_sha(identity_path)}
    envelope["argv"][envelope["argv"].index(
        next(item for item in envelope["argv"] if item.endswith("qualification-install-identity.json")))] = identity_source
    envelope["inputFiles"] = sorted(
        [{"path": item["path"], "sha256": item["sha256"]} for item in envelope["releaseInputs"]] +
        [{"path": item["sourcePath"], "sha256": item["sha256"]} for item in envelope["transitionFiles"]] +
        [{"path": envelope["administrator"]["path"], "sha256": envelope["administrator"]["sha256"]}],
        key=lambda item: item["path"])
    envelope_path = output_root / "release/gate-d-pre-root-bootstrap-envelope-phase5.45-v1.json"
    envelope_path.write_bytes(pretty(envelope))
    return [identity_path, inventory_path, route_path, plan_path, bootstrap_path,
            instance_path, envelope_path, *sorted(attempt_dir.glob("*.json"))]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        with tempfile.TemporaryDirectory() as temporary:
            generated = generate(pathlib.Path(temporary))
            for path in generated:
                relative = path.relative_to(temporary)
                expected = ROOT / relative
                if not expected.is_file() or expected.read_bytes() != path.read_bytes():
                    raise SystemExit(f"generated control differs: {relative}")
        print("Phase 5.45 control-set deterministic generation: PASS")
    else:
        print(f"generated {len(generate(ROOT))} Phase 5.45 control documents")


if __name__ == "__main__":
    main()
