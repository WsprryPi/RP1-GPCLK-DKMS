#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build the final Phase 5.53 controls from the two sealed artifact closures."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import pathlib
import tarfile
import tempfile

import gate_d_attempts
import gate_d_preroot
import gate_d_same_version

ROOT = pathlib.Path(__file__).resolve().parents[1]
RELEASE = "0.0.0-phase5.53"
PRODUCT_COMMIT = "4e7a64a0ca353d2fcab6e25891f5254746e2b91a"
QUALIFICATION_COMMIT = "2f5769e3d80fbd4b232efc1a72b1e932935d08b3"
PRODUCT_SHA = "032a0ca214427ebb6115b933042e7135f03c2ed6ce4f5c399686b2cf61395a76"
QUALIFICATION_SHA = "916a5522e3998ae43f203c217fedce90ad8d4c2d52ae0bd4491407e3cf17211d"
SNAPSHOT = ROOT / "docs/evidence/gate-d-live-target-snapshot-wspr5-phase5.53-final-v1.json"
SNAPSHOT_SHA = "cbaed5a7972bb317a9dc27cabead9419ffde2db474df4de493373b6aa474524f"
LEDGER_SHA = "d4fe02f8d66ac298f2076b37be297097f392095904cc3809717713cd01a14f8d"
BUILD = ROOT / "release/gate-c-representative-build-manifest-phase5.53-v1.json"
TRANSFER = ROOT / "docs/evidence/phase5.53-representative-build-transfer.json"
NAMESPACE = "phase5.53-4e7a64a0ca35"
TAG = "phase5.53-final-v1"
STAGE = f"/home/pi/gate-d-inputs/{NAMESPACE}"


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest(path: pathlib.Path) -> str:
    return digest_bytes(path.read_bytes())


def encoded(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text())


def write(root: pathlib.Path, relative: str, value: object) -> pathlib.Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded(value))
    return path


def archive_files(path: pathlib.Path) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    with tarfile.open(path, "r:gz") as archive:
        roots = {pathlib.PurePosixPath(item.name).parts[0] for item in archive if item.isfile()}
        if len(roots) != 1:
            raise ValueError("archive root differs")
        prefix = next(iter(roots))
        for item in archive.getmembers():
            if not item.isfile():
                continue
            stream = archive.extractfile(item)
            if stream is None:
                raise ValueError("archive member is unreadable")
            relative = pathlib.PurePosixPath(item.name).relative_to(prefix).as_posix()
            if relative in result:
                raise ValueError("duplicate split-archive member")
            result[relative] = stream.read()
    return result


def deep_replace(value: object, replacements: dict[str, str]) -> object:
    text = json.dumps(value, sort_keys=True)
    for old, new in replacements.items():
        text = text.replace(old, new)
    return json.loads(text)


def load_admin(files: dict[str, bytes]):
    with tempfile.TemporaryDirectory() as temporary:
        path = pathlib.Path(temporary) / "rp1-gpclk-admin.py"
        path.write_bytes(files["scripts/rp1-gpclk-admin.py"])
        spec = importlib.util.spec_from_file_location("phase553_final_admin", path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def installed_paths(admin, product: pathlib.Path, qualification: pathlib.Path,
                    files: dict[str, bytes], build: dict) -> list[dict]:
    result = []
    for path, spec in sorted(admin.qualification_package_paths(product, qualification).items()):
        if spec["kind"] == "installed-directory":
            continue
        common = {"path": path, "ownerUid": 0, "groupGid": 0}
        if spec["kind"] == "installed-link":
            result.append({**common, "type": "symlink", "mode": "0777",
                           "target": f"../libexec/rp1-gpclk-dkms/{spec['source']}"})
        else:
            if spec["kind"] == "installed-build":
                key = "busyInjectorSha256" if "busy-injector" in path else "uapiProbeSha256"
                value = build["result"][key]
            else:
                value = digest_bytes(files[spec["source"]])
            result.append({**common, "type": "file", "mode": spec["mode"], "sha256": value})
    gate_d_preroot.validate_package_paths(result)
    return result


def generate(output: pathlib.Path, release_directory: pathlib.Path) -> list[pathlib.Path]:
    product = release_directory / f"rp1-gpclk-dkms-{RELEASE}.tar.gz"
    qualification = release_directory / f"rp1-gpclk-dkms-qualification-{RELEASE}.tar.gz"
    if digest(product) != PRODUCT_SHA or digest(qualification) != QUALIFICATION_SHA:
        raise ValueError("final split archive identity differs")
    metadata = load(release_directory / "release-metadata.json")
    if (metadata.get("sourceCommit") != PRODUCT_COMMIT or
            metadata.get("qualificationSourceCommit") != QUALIFICATION_COMMIT):
        raise ValueError("final split source identity differs")
    snapshot = load(SNAPSHOT)
    if digest(SNAPSHOT) != SNAPSHOT_SHA or snapshot["administratorLedger"]["sha256"] != LEDGER_SHA:
        raise ValueError("final retained target identity differs")
    build = load(BUILD)
    transfer = load(TRANSFER)
    if (transfer["gitDiffEmpty"] is not True or
            build["result"]["moduleSha256"] != transfer["representativeModuleSha256"]):
        raise ValueError("representative build transfer is absent")
    files = archive_files(product)
    qualification_files = archive_files(qualification)
    if set(files) & set(qualification_files):
        raise ValueError("split archive ownership overlaps")
    files.update(qualification_files)
    admin = load_admin(files)
    package_paths = installed_paths(admin, product, qualification, files, build)

    replacements = {
        "phase5.53-1884c0f1c53c": NAMESPACE,
        "1884c0f1c53c661495576bf10ce08d8bf7a90bc3": PRODUCT_COMMIT,
        "ae6df3a66a9a26a6fb8474e5896c9053b9f69580d8c45383a5556fc397ebb549": PRODUCT_SHA,
        "df8e80bc4b3382d9213d52cbc273b398e85124a2d2f58169c3a6f6aa339dbcf7": SNAPSHOT_SHA,
        "gate-d-attempts-phase5.53-v1": f"gate-d-attempts-{TAG}",
        "gate-d-route-compatibility-decision-phase5.53-v1": f"gate-d-route-compatibility-decision-{TAG}",
        "gate-d-target-operation-plan-phase5.53-v1": f"gate-d-target-operation-plan-{TAG}",
        "gate-d-qualification-bootstrap-plan-phase5.53-v1": f"gate-d-qualification-bootstrap-plan-{TAG}",
        "gate-d-execution-instance-phase5.53-v1": f"gate-d-execution-instance-{TAG}",
        "gate-d-phase5.53-qualification-install-identity": "gate-d-phase5.53-final-qualification-install-identity",
    }
    def template(name: str) -> dict:
        return deep_replace(load(ROOT / name), replacements)

    marker = {"SPDX-License-Identifier": "MIT", "schemaVersion": 1,
              "kind": "gate-d-qualification-root-identity",
              "rootPath": f"/home/pi/gate-d-qualification/{NAMESPACE}",
              "candidateRelease": RELEASE, "sourceCommit": PRODUCT_COMMIT}
    root_reference = {"path": marker["rootPath"], "identityFile": ".gate-d-root.json",
                      "identitySha256": digest_bytes(canonical(marker)), "ownerUid": 1000,
                      "mode": "0700"}
    identity_simple = []
    for item in snapshot["packagePaths"]:
        record = {"path": item["path"], "type": item["type"]}
        record["sha256" if item["type"] == "file" else "target"] = item[
            "sha256" if item["type"] == "file" else "target"]
        identity_simple.append(record)
    identity_simple.sort(key=lambda item: item["path"])
    identity = {"SPDX-License-Identifier": "MIT", "schemaVersion": 4,
                "kind": "rp1-gpclk-gate-d-qualification-install-identity",
                "release": RELEASE, "sourceCommit": PRODUCT_COMMIT,
                "archiveSha256": PRODUCT_SHA, "publishable": False, "tagPresent": False,
                "outputDisabled": True, "liveOutput": False,
                "purpose": "gate-d-representative-system-qualification",
                "preRemovalLedgerSha256": LEDGER_SHA,
                "predecessorPackagePaths": identity_simple,
                "predecessorPackagePathsSha256": digest_bytes(canonical(identity_simple))}
    identity_rel = "docs/evidence/gate-d-phase5.53-final-qualification-install-identity.json"
    identity_path = write(output, identity_rel, identity)

    route = template("release/gate-d-route-compatibility-decision-phase5.53-v1.json")
    route["candidate"].update(sourceCommit=PRODUCT_COMMIT, archiveSha256=PRODUCT_SHA)
    route["candidate"]["representativeBuildManifestSha256"] = digest(BUILD)
    route["evidence"]["representativeBuildEvidenceManifestSha256"] = digest(BUILD)
    route_rel = f"release/gate-d-route-compatibility-decision-{TAG}.json"
    route_path = write(output, route_rel, route)

    bootstrap = template("release/gate-d-qualification-bootstrap-plan-phase5.53-v1.json")
    bootstrap["candidate"].update(sourceCommit=PRODUCT_COMMIT, archiveSha256=PRODUCT_SHA,
                                  archive=f"{STAGE}/{product.name}")
    bootstrap["qualificationRoot"] = root_reference
    bootstrap["packagePaths"] = package_paths
    bootstrap["packagePathsSha256"] = digest_bytes(canonical(package_paths))
    installed_by_path = {item["path"]: item for item in package_paths}
    for item in bootstrap["retainedTools"]:
        item["sha256"] = installed_by_path[item["path"]]["sha256"]
    admin_source = f"{STAGE}/extracted/rp1-gpclk-dkms-{RELEASE}/scripts/rp1-gpclk-admin.py"
    bootstrap["administrator"].update(bootstrapPath=admin_source,
                                      sourceSha256=digest_bytes(files["scripts/rp1-gpclk-admin.py"]),
                                      installedSha256=digest_bytes(files["scripts/rp1-gpclk-admin.py"]))
    bootstrap["qualificationIdentity"] = {
        "path": f"{STAGE}/control-set/{identity_rel}", "sha256": digest(identity_path)}
    bootstrap["argv"] = ["/usr/bin/python3", admin_source, "install", "--execute",
                         "--release-directory", STAGE, "--route", "gpio4",
                         "--qualification-install", "--qualification-identity",
                         bootstrap["qualificationIdentity"]["path"]]
    bootstrap_rel = f"release/gate-d-qualification-bootstrap-plan-{TAG}.json"
    bootstrap_path = write(output, bootstrap_rel, bootstrap)

    plan = template("release/gate-d-target-operation-plan-phase5.53-v1.json")
    plan["qualificationRoot"] = root_reference
    plan["qualificationBootstrap"] = {"path": bootstrap_rel, "sha256": digest(bootstrap_path)}
    plan["artifacts"]["successor"].update(archive=f"{STAGE}/{product.name}", sha256=PRODUCT_SHA)
    for item in [*plan["pythonModules"].values(), *plan["tooling"].values()]:
        source = item["sourcePath"]
        item["sourceSha256"] = digest_bytes(files[source])
        if item["installKind"] == "copied":
            item["installedSha256"] = item["sourceSha256"]
        elif "busy" in item["installedPath"]:
            item["installedSha256"] = build["result"]["busyInjectorSha256"]
        else:
            item["installedSha256"] = build["result"]["uapiProbeSha256"]
    plan_rel = f"release/gate-d-target-operation-plan-{TAG}.json"
    plan_path = write(output, plan_rel, plan)

    instance = template("release/gate-d-execution-instance-phase5.53-v1.json")
    instance["candidate"].update(sourceCommit=PRODUCT_COMMIT, archiveSha256=PRODUCT_SHA)
    instance["qualificationRoot"] = root_reference
    instance["authorization"].update(approved=False, targetExecutionApproved=False,
        approvalScope="Offline construction only; target staging, pre-root, lifecycle, and hardware activity are unauthorized.")
    instance["executionReady"] = False
    instance["executionPolicy"].update(attemptPathNamespace=NAMESPACE,
        routeDecision=route_rel, routeDecisionSha256=digest(route_path), targetPlan=plan_rel,
        targetPlanSha256=digest(plan_path), qualificationBootstrap=bootstrap_rel,
        qualificationBootstrapSha256=digest(bootstrap_path),
        attemptIndex=f"release/gate-d-attempts-{TAG}/index.json")
    for row in instance["rows"]:
        row["evidenceDirectory"] = f"gate-d/runs/{NAMESPACE}/{row['id']}"
    attempts = gate_d_attempts.generate(instance, plan, schema_version=2)
    attempt_dir = output / f"release/gate-d-attempts-{TAG}"
    records = []
    for document in attempts:
        path = write(output, f"release/gate-d-attempts-{TAG}/{document['operationId']}.json", document)
        records.append({"file": path.name, "operationId": document["operationId"], "sha256": digest(path)})
    index = {"SPDX-License-Identifier": "MIT", "schemaVersion": 2,
             "kind": "gate-d-attempt-index", "attemptCount": len(records),
             "qualificationRoot": root_reference,
             "executors": {"attemptGenerator": {"path": "scripts/gate_d_attempts.py",
                 "sha256": digest_bytes(files["scripts/gate_d_attempts.py"])},
                 "permanentExecutor": {"path": "scripts/gate_d_outer.py",
                 "sha256": digest_bytes(files["scripts/gate_d_outer.py"])}}, "attempts": records}
    index_path = write(output, f"release/gate-d-attempts-{TAG}/index.json", index)
    instance["executionPolicy"]["attemptIndexSha256"] = digest(index_path)
    instance_rel = f"release/gate-d-execution-instance-{TAG}.json"
    instance_path = write(output, instance_rel, instance)

    envelope = template("release/gate-d-pre-root-bootstrap-envelope-phase5.53-v1.json")
    envelope["schemaVersion"] = 7
    envelope["candidate"].update(sourceCommit=PRODUCT_COMMIT, archiveSha256=PRODUCT_SHA,
                                 archivePath=f"{STAGE}/{product.name}")
    envelope["proposedRoot"].update(path=marker["rootPath"], marker=marker,
                                    markerSha256=root_reference["identitySha256"])
    envelope["installedPackagePaths"] = package_paths
    envelope["packagePathsSha256"] = digest_bytes(canonical(package_paths))
    envelope["predecessorPackagePaths"] = snapshot["packagePaths"]
    envelope["predecessorPackagePathsSha256"] = snapshot["packagePathsSha256"]
    envelope["liveTargetSnapshotSha256"] = SNAPSHOT_SHA
    for item in envelope["installedTools"]:
        item["sha256"] = installed_by_path[item["path"]]["sha256"]
    envelope["priorTerminalState"].update(status="removed", sha256=LEDGER_SHA,
        archivePath="/var/lib/rp1-gpclk-dkms/recovery/phase5.53-final-product-removed.json")
    artifacts = {path.name: digest(path) for path in release_directory.iterdir() if path.is_file()}
    roles = {product.name: "archive", qualification.name: "qualificationArchive",
             "rp1-gpclk-gpio4.dtbo": "gpio4Dtbo", "rp1-gpclk-gpio20.dtbo": "gpio20Dtbo",
             "rp1-gpclk-compatibility-manifest.json": "compatibilityManifest",
             "PROVENANCE.json": "provenance", "release-metadata.json": "releaseMetadata",
             "SHA256SUMS": "checksums"}
    envelope["releaseInputs"] = [{"path": f"{STAGE}/{name}", "role": role,
                                   "sha256": artifacts[name]} for name, role in roles.items()]
    transitions = [identity_path, route_path, bootstrap_path, plan_path, instance_path, index_path,
                   *sorted(attempt_dir.glob("gd-*.json"))]
    frozen = {instance["executionPolicy"]["matrixPolicy"],
              "schema/gate-d-execution-instance-v1.schema.json",
              *[item["sourcePath"] for item in plan["pythonModules"].values()],
              *[item["path"] for item in index["executors"].values()]}
    transition_files = []
    for path in transitions:
        relative = path.relative_to(output).as_posix()
        transition_files.append({"sourcePath": f"{STAGE}/control-set/{relative}",
                                 "destination": relative, "sha256": digest(path), "mode": "0400"})
    for relative in sorted(frozen):
        transition_files.append({"sourcePath": f"{STAGE}/control-set/{relative}",
                                 "destination": relative, "sha256": digest_bytes(files[relative]),
                                 "mode": "0400"})
    envelope["transitionFiles"] = sorted(transition_files, key=lambda item: item["destination"])
    by_destination = {item["destination"]: item for item in envelope["transitionFiles"]}
    envelope["stagedExecutor"] = {"path": by_destination["scripts/gate_d_outer.py"]["sourcePath"],
                                  "sha256": by_destination["scripts/gate_d_outer.py"]["sha256"]}
    envelope["preRootModule"] = {"path": by_destination["scripts/gate_d_preroot.py"]["sourcePath"],
                                 "sha256": by_destination["scripts/gate_d_preroot.py"]["sha256"]}
    envelope["administrator"] = {"path": admin_source,
                                 "sha256": digest_bytes(files["scripts/rp1-gpclk-admin.py"])}
    envelope["qualificationIdentity"] = {"path": f"{STAGE}/control-set/{identity_rel}",
                                          "sha256": digest(identity_path)}
    envelope["argv"] = bootstrap["argv"]
    envelope["inputFiles"] = sorted(
        [{"path": item["path"], "sha256": item["sha256"]} for item in envelope["releaseInputs"]] +
        [{"path": item["sourcePath"], "sha256": item["sha256"]} for item in envelope["transitionFiles"]] +
        [envelope["administrator"]], key=lambda item: item["path"])
    envelope_rel = f"release/gate-d-pre-root-bootstrap-envelope-{TAG}.json"
    envelope_path = write(output, envelope_rel, envelope)
    gate_d_preroot.validate(envelope)

    probe = f"{STAGE}/extracted/rp1-gpclk-dkms-qualification-{RELEASE}/scripts/gate_d_same_version_probe.py"
    staged_admin = admin_source
    same = {"SPDX-License-Identifier": "MIT", "schemaVersion": 1,
            "kind": "gate-d-same-version-transition", "productArchiveSha256": PRODUCT_SHA,
            "qualificationArchiveSha256": QUALIFICATION_SHA, "ledgerSha256": LEDGER_SHA,
            "preState": {"product": True, "qualification": False, "liveOutput": False},
            "absentState": {"product": False, "qualification": False, "liveOutput": False},
            "qualifiedState": {"product": True, "qualification": True, "liveOutput": False},
            "authorization": {"approved": False, "targetExecutionApproved": False, "executionReady": False},
            "probeArgv": ["/usr/bin/python3", probe, "--product-marker",
                f"/usr/src/rp1-gpclk-dkms-{RELEASE}/dkms.conf", "--qualification-marker",
                "/usr/libexec/rp1-gpclk-dkms/gate-d-same-version"],
            "removeArgv": ["/usr/bin/python3", "/usr/libexec/rp1-gpclk-dkms/rp1-gpclk-admin", "remove", "--execute"],
            "removeRecoveryArgv": ["/usr/bin/python3", "/usr/libexec/rp1-gpclk-dkms/rp1-gpclk-admin", "recover", "--execute"],
            "qualificationInstallArgv": ["/usr/bin/python3", envelope["stagedExecutor"]["path"],
                "pre-root-bootstrap", f"{STAGE}/control-set/{envelope_rel}", "--execute",
                "--envelope-sha256", digest(envelope_path)],
            "qualificationRecoveryArgv": ["/usr/bin/python3", envelope["stagedExecutor"]["path"],
                "pre-root-bootstrap", f"{STAGE}/control-set/{envelope_rel}", "--resume",
                "--envelope-sha256", digest(envelope_path)],
            "qualificationRemoveArgv": ["/usr/bin/python3", "/usr/libexec/rp1-gpclk-dkms/rp1-gpclk-admin", "remove", "--execute"],
            "productRollbackArgv": ["/usr/bin/python3", staged_admin, "install", "--execute",
                "--release-directory", STAGE, "--route", "gpio4", "--allow-development"]}
    gate_d_same_version.validate(same)
    same_path = write(output, f"release/gate-d-same-version-transition-{TAG}.json", same)
    return [identity_path, route_path, bootstrap_path, plan_path, instance_path, index_path,
            envelope_path, same_path, *sorted(attempt_dir.glob("gd-*.json"))]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-directory", required=True, type=pathlib.Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        with tempfile.TemporaryDirectory() as temporary:
            for generated in generate(pathlib.Path(temporary), args.release_directory):
                expected = ROOT / generated.relative_to(temporary)
                if not expected.is_file() or expected.read_bytes() != generated.read_bytes():
                    raise SystemExit(f"generated control differs: {generated.relative_to(temporary)}")
        print("Phase 5.53 final control deterministic generation: PASS")
    else:
        print(f"generated {len(generate(ROOT, args.release_directory))} final control documents")


if __name__ == "__main__":
    main()
