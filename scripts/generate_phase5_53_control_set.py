#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Deterministically generate the snapshot-bound Phase 5.53 Gate D controls."""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import tempfile

import gate_d_attempts
import generate_phase5_43_control_set as source_catalog
import generate_phase5_52_control_set as predecessor_generator

ROOT = pathlib.Path(__file__).resolve().parents[1]
OLD_RELEASE = "0.0.0-phase5.52"
RELEASE = "0.0.0-phase5.53"
OLD_COMMIT = "f710554c4697d75210cbd33c9eea13474d60557a"
COMMIT = "834d05c5c5da0c383c4a229eaeff9dae07a4359b"
PRODUCT_COMMIT = "1884c0f1c53c661495576bf10ce08d8bf7a90bc3"
PRODUCT_ARCHIVE_SHA256 = "ae6df3a66a9a26a6fb8474e5896c9053b9f69580d8c45383a5556fc397ebb549"
QUALIFICATION_ARCHIVE_SHA256 = "d931912d6ccc381b10a2a13d7f3a9122b0f748490ec8eefe0f86a28cb352c8d0"
OLD_SUFFIX = "phase5.52-f710554c4697"
SUFFIX = "phase5.53-1884c0f1c53c"
NAMESPACE = SUFFIX
SNAPSHOT = ROOT / "docs/evidence/gate-d-live-target-snapshot-wspr5-phase5.53-v1.json"
BUILD = ROOT / "release/gate-c-representative-build-manifest-phase5.53-v1.json"
INVENTORY = ROOT / "docs/evidence/gate-c-phase5.53-qualification-successor-release-input-inventory.json"
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
    for path in sorted(set(source_catalog.SOURCE_BY_NAME.values())):
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
                new_hash = sha(git_bytes(COMMIT, source_catalog.SOURCE_BY_NAME[name]))
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
    if file_sha(SNAPSHOT) != "df8e80bc4b3382d9213d52cbc273b398e85124a2d2f58169c3a6f6aa339dbcf7":
        raise ValueError("Phase 5.53 canonical snapshot differs")
    build = json.loads(BUILD.read_text())
    inventory = json.loads(INVENTORY.read_text())
    artifacts = {item["name"]: item for item in inventory["artifacts"]}
    old_inventory = json.loads((ROOT / "docs/evidence/gate-c-phase5.52-release-input-inventory.json").read_text())
    old_artifacts = {item["name"]: item for item in old_inventory["artifacts"]}
    replacements = {
        OLD_SUFFIX: SUFFIX, OLD_RELEASE: RELEASE, "phase5.52": "phase5.53",
        OLD_COMMIT: COMMIT,
        "253bd54054eb0b673f9e61c58a46b6b7ca2cf78d756fe4e80656f4ac1233f549": PRODUCT_ARCHIVE_SHA256,
        "5fcfcc41e44a3685b7051b7ea8fbcce67f0fa79fefb29b8e203a231d7295d192": build["result"]["moduleSha256"],
        file_sha(ROOT / "release/gate-c-representative-build-manifest-phase5.52-v1.json"): file_sha(BUILD),
        "449201a0a51ca8b278b7ae077410e515aa9c176eac42f4ba86bd62ef4c36451f": file_sha(SNAPSHOT),
        **source_replacements(),
    }
    for old_name, old_item in old_artifacts.items():
        new_name = old_name.replace("phase5.52", "phase5.53")
        replacements[old_item["sha256"]] = artifacts[new_name]["sha256"]

    with tempfile.TemporaryDirectory() as temporary:
        old_root = pathlib.Path(temporary)
        predecessor_generator.generate(old_root)
        controls = {}
        for name in CONTROL_NAMES:
            old_path = old_root / f"release/{name}-phase5.52-v1.json"
            controls[name] = replace(json.loads(old_path.read_text()), replacements)
    for control in controls.values():
        if "candidate" in control:
            control["candidate"]["sourceCommit"] = PRODUCT_COMMIT
            control["candidate"]["archiveSha256"] = PRODUCT_ARCHIVE_SHA256

    route = controls["gate-d-route-compatibility-decision"]
    route["candidate"]["sourceCommit"] = PRODUCT_COMMIT
    route["candidate"]["archiveSha256"] = PRODUCT_ARCHIVE_SHA256
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
        entry["reason"] = ("Exact retained Phase 5.53 representative build and accepted canonical "
                           "inactive wspr5 snapshot support Compatible-unqualified output-disabled planning; "
                           "authorization remains a separate gate.")

    packages, transitions = successor_packages(snapshot, build)
    marker = {"SPDX-License-Identifier": "MIT", "schemaVersion": 1,
              "kind": "gate-d-qualification-root-identity",
              "rootPath": f"/home/pi/gate-d-qualification/{SUFFIX}",
              "candidateRelease": RELEASE, "sourceCommit": PRODUCT_COMMIT}
    marker_hash = sha(canonical(marker))
    bootstrap = controls["gate-d-qualification-bootstrap-plan"]
    bootstrap["packagePaths"] = packages
    bootstrap["packagePathsSha256"] = sha(canonical(packages))
    bootstrap["qualificationRoot"].update(path=marker["rootPath"], identitySha256=marker_hash)

    identity = {"SPDX-License-Identifier": "MIT", "schemaVersion": 3,
                "kind": "rp1-gpclk-gate-d-qualification-install-identity",
                "release": RELEASE, "sourceCommit": PRODUCT_COMMIT,
                "archiveSha256": PRODUCT_ARCHIVE_SHA256,
                "publishable": False, "tagPresent": False, "outputDisabled": True,
                "liveOutput": False, "purpose": "gate-d-representative-system-qualification",
                "packageTransitions": transitions}
    identity_rel = "docs/evidence/gate-d-phase5.53-qualification-install-identity.json"
    identity_path = output_root / identity_rel
    identity_path.parent.mkdir(parents=True, exist_ok=True)
    identity_path.write_bytes(pretty(identity))

    inventory_rel = "docs/evidence/gate-d-phase5.53-predecessor-package-inventory.json"
    inventory_path = output_root / inventory_rel
    inventory_path.parent.mkdir(parents=True, exist_ok=True)
    inventory_path.write_bytes(pretty({"SPDX-License-Identifier": "MIT", "schemaVersion": 1,
        "kind": "gate-d-predecessor-package-inventory", "host": "wspr5",
        "capturedFor": RELEASE, "liveTargetSnapshotSha256": file_sha(SNAPSHOT),
        "paths": snapshot["packagePaths"]}))

    route_rel = "release/gate-d-route-compatibility-decision-phase5.53-v1.json"
    route_path = output_root / route_rel
    route_path.parent.mkdir(parents=True, exist_ok=True)
    route_path.write_bytes(pretty(route))

    bootstrap_rel = "release/gate-d-qualification-bootstrap-plan-phase5.53-v1.json"
    bootstrap_path = output_root / bootstrap_rel
    bootstrap_path.write_bytes(pretty(bootstrap))

    plan = controls["gate-d-target-operation-plan"]
    plan = gate_d_attempts.bind_services_to_snapshot(plan, snapshot)
    plan["qualificationRoot"].update(path=marker["rootPath"], identitySha256=marker_hash)
    plan["qualificationBootstrap"].update(path=bootstrap_rel, sha256=file_sha(bootstrap_path))
    plan_path = output_root / "release/gate-d-target-operation-plan-phase5.53-v1.json"
    plan_path.write_bytes(pretty(plan))

    instance = controls["gate-d-execution-instance"]
    instance["schemaVersion"] = 6
    instance["qualificationRoot"].update(path=marker["rootPath"], identitySha256=marker_hash)
    instance["authorization"].update(
        approved=False, targetExecutionApproved=False,
        approvalScope="No Phase 5.53 target execution authority has been requested or granted.")
    instance["executionReady"] = False
    instance["executionPolicy"].update(
        attemptPathNamespace=NAMESPACE, attemptSchemaVersion=2,
        routeDecision=route_rel, routeDecisionSha256=file_sha(route_path),
        targetPlan="release/gate-d-target-operation-plan-phase5.53-v1.json",
        targetPlanSha256=file_sha(plan_path),
        qualificationBootstrap=bootstrap_rel,
        qualificationBootstrapSha256=file_sha(bootstrap_path),
        attemptIndex="release/gate-d-attempts-phase5.53-v1/index.json")
    for row in instance["rows"]:
        row["evidenceDirectory"] = f"gate-d/runs/{NAMESPACE}/{row['id']}"

    attempts = gate_d_attempts.generate(instance, plan, schema_version=2)
    attempt_dir = output_root / "release/gate-d-attempts-phase5.53-v1"
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
    instance_path = output_root / "release/gate-d-execution-instance-phase5.53-v1.json"
    instance_path.write_bytes(pretty(instance))

    envelope = controls["gate-d-pre-root-bootstrap-envelope"]
    envelope["schemaVersion"] = 6
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
        "archivePath": "/var/lib/rp1-gpclk-dkms/recovery/phase5.53-phase5.52-transaction-complete.json",
        "archiveMode": "0400"}
    roles = {"rp1-gpclk-dkms-0.0.0-phase5.53.tar.gz": "archive",
             "rp1-gpclk-dkms-qualification-0.0.0-phase5.53.tar.gz": "qualificationArchive",
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
    # Close the qualification-root trust graph.  Policy and executable bytes
    # used after the pre-root transition must be copied into the sealed root;
    # they may not be resolved implicitly from a checkout or mutable install.
    frozen_root_paths = {instance["executionPolicy"]["matrixPolicy"]}
    frozen_root_paths.add("schema/gate-d-execution-instance-v1.schema.json")
    frozen_root_paths.update(
        module["sourcePath"] for module in plan["pythonModules"].values())
    frozen_root_paths.update(
        executor["path"] for executor in index["executors"].values())
    for relative in sorted(frozen_root_paths):
        payload = git_bytes(COMMIT, relative)
        transition_files.append({
            "sourcePath": f"{stage}/control-set/{relative}",
            "destination": relative,
            "sha256": sha(payload),
            "mode": "0400",
        })
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
    envelope_path = output_root / "release/gate-d-pre-root-bootstrap-envelope-phase5.53-v1.json"
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
        print("Phase 5.53 control-set deterministic generation: PASS")
    else:
        print(f"generated {len(generate(ROOT))} Phase 5.53 control documents")


if __name__ == "__main__":
    main()
