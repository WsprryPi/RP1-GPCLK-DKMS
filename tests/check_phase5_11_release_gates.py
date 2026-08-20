#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import copy
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
PATH = ROOT / "release/release-integration-gates-v1.json"
document = json.loads(PATH.read_text())

ORDER = [
    "candidate-freeze", "offline-checks-twice", "qualification-tooling-installation",
    "representative-lifecycle-matrix",
    "independent-adversarial-review", "artifact-reproduction",
    "tag-and-internal-version-match", "real-compatibility-manifest",
    "operator-instructions-verification", "limitations-and-claim-audit",
    "module-publication", "public-download-verification",
    "wspr-transmitter-integration", "cross-repository-uapi-checks",
    "wsprrypi-exact-pin", "application-integration-qualification",
    "dependent-release-publication",
]
GATE_KEYS = {"id", "owner", "requires", "status", "evidence", "claimCeiling"}


def validate(value: dict) -> None:
    if value.get("schemaVersion") != 1:
        raise ValueError("invalid release-gate schema identity")
    if value.get("currentClassification") != "candidate":
        raise ValueError("current non-published identity must remain a candidate")
    if value.get("modulePublicationConfirmed") is not False:
        raise ValueError("module publication is not confirmed")
    if value.get("publishedReleaseRequiresPostDownloadVerification") is not True:
        raise ValueError("public download verification is mandatory")
    if value.get("gateOrder") != ORDER:
        raise ValueError("release or integration gate order changed")
    gates = value.get("gates")
    if not isinstance(gates, list) or [gate.get("id") for gate in gates] != ORDER:
        raise ValueError("gates missing, extra, duplicated, or reordered")
    for index, gate in enumerate(gates):
        if set(gate) != GATE_KEYS:
            raise ValueError(f"invalid fields for {gate.get('id')}")
        if gate["status"] not in {"planned", "blocked", "passed"}:
            raise ValueError(f"invalid status for {gate['id']}")
        if not isinstance(gate["evidence"], list) or not gate["evidence"]:
            raise ValueError(f"missing evidence contract for {gate['id']}")
        if not all(isinstance(item, str) and item.strip() for item in gate["evidence"]):
            raise ValueError(f"invalid evidence contract for {gate['id']}")
        if not isinstance(gate["claimCeiling"], str) or not gate["claimCeiling"].strip():
            raise ValueError(f"missing claim ceiling for {gate['id']}")
        expected_requires = [] if index == 0 else [ORDER[index - 1]]
        if gate["requires"] != expected_requires:
            raise ValueError(f"gate dependency is not strict for {gate['id']}")
        if index and gate["status"] == "passed" and gates[index - 1]["status"] != "passed":
            raise ValueError(f"gate passed before its prerequisite: {gate['id']}")

    by_id = {gate["id"]: gate for gate in gates}
    if "downloaded to a fresh location" not in " ".join(by_id["public-download-verification"]["evidence"]):
        raise ValueError("fresh public download evidence missing")
    public_evidence = " ".join(by_id["public-download-verification"]["evidence"])
    if not all(term in public_evidence for term in
               ("outer SHA-256", "both archives", "inner checksum", "distinct paths",
                "without the qualification archive")):
        raise ValueError("outer and inner public artifact verification incomplete")
    offline_evidence = " ".join(by_id["offline-checks-twice"]["evidence"])
    if not all(term in offline_evidence for term in
               ("product archive", "qualification archive", "ordinary-install",
                "qualification-mode")):
        raise ValueError("split-artifact offline validation is incomplete")
    qualification_install = " ".join(by_id["qualification-tooling-installation"]["evidence"])
    if not all(term in qualification_install for term in
               ("read-only target recapture", "literal transferred qualification archive",
                "separate qualification ledger", "inactive product", "stops before lifecycle attempt 1")):
        raise ValueError("qualification-only installation prerequisite is incomplete")
    lifecycle = by_id["representative-lifecycle-matrix"]
    if lifecycle["requires"] != ["qualification-tooling-installation"]:
        raise ValueError("lifecycle matrix bypasses qualification-only installation")
    reproduction = " ".join(by_id["artifact-reproduction"]["evidence"])
    if not all(term in reproduction for term in
               ("post-review", "product-archive", "qualification-archive",
                "GPIO4", "GPIO20", "candidate-freeze builds alone")):
        raise ValueError("post-review split-artifact reproduction is incomplete")
    uapi_evidence = " ".join(by_id["cross-repository-uapi-checks"]["evidence"])
    if "byte equality" not in uapi_evidence or "semantic ABI equality" not in uapi_evidence:
        raise ValueError("cross-repository UAPI checks incomplete")
    pin_evidence = " ".join(by_id["wsprrypi-exact-pin"]["evidence"])
    for term in ("module tag", "product archive SHA-256", "UAPI", "compatibility-manifest",
                 "adapter identity"):
        if term not in pin_evidence:
            raise ValueError(f"WsprryPi exact pin lacks {term}")
    if "module-before-adapter-before-application" not in " ".join(by_id["dependent-release-publication"]["evidence"]):
        raise ValueError("dependent release order is not explicit")


validate(document)
layout = json.loads((ROOT / "release/release-layout-v1.json").read_text())
qualification_layout = json.loads((ROOT / "release/qualification-layout-v1.json").read_text())
assert document["release"] == layout["release"]
assert document["expectedTag"] == layout["expectedTag"]
assert document["release"] == qualification_layout["release"]
assert any(item["path"] == "release/release-integration-gates-v1.json"
           for item in qualification_layout["artifacts"])
decisions = json.loads((ROOT / "release/compatibility-decisions-v1.json").read_text())
assert decisions["entries"]
assert all(entry["state"] == "Unavailable" and entry["liveEligible"] is False for entry in decisions["entries"])
assert set(document["candidateSnapshot"]["knownBlockers"]) == {
    "qualification-tooling-not-installed-for-final-split-candidate",
    "representative-lifecycle-matrix-not-executed-for-final-product",
    "public-artifact-download-verification-not-performed",
    "module-release-not-published",
}
assert document["candidateSnapshot"]["archiveIdentity"] == \
    "product sha256:032a0ca214427ebb6115b933042e7135f03c2ed6ce4f5c399686b2cf61395a76; qualification successor identity is recorded in external freeze evidence because this graph is inside that archive; product source 4e7a64a0ca353d2fcab6e25891f5254746e2b91a"
assert document["candidateSnapshot"]["sealedArchiveMayBeTested"] is True
freeze_gate = next(gate for gate in document["gates"]
                   if gate["id"] == "candidate-freeze")
assert freeze_gate["status"] == "passed"
assert freeze_gate["claimCeiling"] == \
    "frozen final product and qualification-successor artifacts only; no representative lifecycle claim"
offline_gate = next(gate for gate in document["gates"]
                    if gate["id"] == "offline-checks-twice")
assert offline_gate["status"] == "passed"
assert offline_gate["claimCeiling"] == \
    "two complete offline passes on the exact frozen split candidate; no target lifecycle or output qualification"
phase524 = json.loads((ROOT / "release/gate-d-successor-offline-identities-phase5.24-v1.json").read_text())
assert phase524["release"] == "0.0.0-phase5.24"
assert phase524["sourceCommit"] == "2a6ddeb8e0f7d31a26bbe4ebdc4bc0458a41c8c5"
assert phase524["builds"]["count"] == 2
assert phase524["builds"]["byteIdentical"] is True
assert phase524["builds"]["archiveSha256"] == \
    "0da181f1ccfa9fb9edbd34456cec95730be8922283d1c5b207af376491413d8a"
assert phase524["publishedSchemas"]["targetPlanSha256"] == \
    "43b716aaa4d4b666a2f99ea139f6a317938b0604bed9a0807bec33f528950edc"
assert "representative-build compatible" in phase524["claimCeiling"]
phase525 = json.loads((ROOT / "release/gate-d-successor-offline-identities-phase5.25-v1.json").read_text())
assert phase525["release"] == "0.0.0-phase5.25"
assert phase525["sourceCommit"] == "d9f8fd8b17f1c2ee9324704c6b6630dfccfb5e4e"
assert phase525["builds"]["count"] == 2 and phase525["builds"]["byteIdentical"] is True
assert phase525["builds"]["archiveSha256"] == \
    "e615750897009b79d0ead1e3bbf4133e0c4d5c157cc259d513a76ad65bd993e4"
assert phase525["publishedSchemas"]["preRootEnvelopeSha256"] == \
    "85293e1425f07ceb7cd92d92d6c884eeb8f71e4495c8176fec4e9dca2521ec11"
assert phase525["residueRecovery"]["executed"] is False
assert "no representative build" in phase525["claimCeiling"]
phase526 = json.loads((ROOT / "release/gate-d-successor-offline-identities-phase5.26-v1.json").read_text())
assert phase526["release"] == "0.0.0-phase5.26"
assert phase526["sourceCommit"] == "9f009240eecd55940d53d6f13cb9567aa76cd4ce"
assert phase526["builds"]["count"] == 2 and phase526["builds"]["byteIdentical"] is True
assert phase526["builds"]["archiveSha256"] == \
    "f43422342fc03c402eb0602949cc317aea239defc6544534ea98bc40d2c505bc"
assert phase526["builds"]["uapiHeaderSha256"] == phase525["builds"]["uapiHeaderSha256"]
assert phase526["builds"]["gpio4DtboSha256"] == phase525["builds"]["gpio4DtboSha256"]
assert phase526["builds"]["gpio20DtboSha256"] == phase525["builds"]["gpio20DtboSha256"]
assert "no representative build" in phase526["claimCeiling"]


def gate(value: dict, identity: str) -> dict:
    return next(item for item in value["gates"] if item["id"] == identity)

for mutation in (
    lambda value: value.update(currentClassification="published-release"),
    lambda value: value.update(modulePublicationConfirmed=True),
    lambda value: value.update(publishedReleaseRequiresPostDownloadVerification=False),
    lambda value: value["gates"].pop(),
    lambda value: gate(value, "offline-checks-twice").update(requires=[]),
    lambda value: gate(value, "qualification-tooling-installation").update(
        evidence=["qualification tools appear installed"]),
    lambda value: gate(value, "representative-lifecycle-matrix").update(
        requires=["offline-checks-twice"]),
    lambda value: value["gates"][0].update(status="unknown"),
    lambda value: gate(value, "public-download-verification").update(
        evidence=["checksums passed before upload"]),
    lambda value: gate(value, "cross-repository-uapi-checks").update(
        evidence=["header looks compatible"]),
):
    invalid = copy.deepcopy(document)
    mutation(invalid)
    try:
        validate(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid release or integration gate contract accepted")

print("Phase 5.11 release and integration gates: PASS")
