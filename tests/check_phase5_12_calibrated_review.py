#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import copy
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
document = json.loads((ROOT / "release/calibrated-review-release-policy-v1.json").read_text())

REQUIRED_BINDINGS = {
    "source-commit", "archive-name-and-sha256", "uapi-abi-and-header-sha256",
    "gpio4-source-and-dtbo-sha256", "gpio20-source-and-dtbo-sha256",
    "compatibility-manifest-sha256", "package-and-tool-identities", "expected-tag",
}
REQUIRED_DOMAINS = {
    "module-behavior-or-source", "overlays", "uapi", "timing",
    "package-contents-or-generated-bytes", "signing", "compatibility-policy",
    "lifecycle-tooling",
}


def validate(value: dict) -> None:
    if value.get("schemaVersion") != 1 or value.get("packagingClaimCeiling") != "Experimental":
        raise ValueError("invalid Phase 5.12 policy identity or packaging ceiling")
    if value.get("packagingMayProduceExperimentalPrerelease") is not True:
        raise ValueError("Experimental prerelease policy is absent")
    prerequisites = set(value.get("experimentalPrereleaseRequires", []))
    for item in ("applicable-representative-lifecycle-gates", "release-integrity-and-adversarial-review",
                 "current-administrator-enrollment", "explicit-gate-f-publication-authority"):
        if item not in prerequisites:
            raise ValueError(f"Experimental prerequisite missing: {item}")
    for key in ("packagingNeverCreatesOrPreservesQualified", "finalReleaseRequiresNewReviewedManifest",
                "experimentalPrereleaseImmutable", "finalQualifiedRequiresCompleteCalibratedEvidence",
                "incompleteOrFailedRowsRetainTruthfulLesserState"):
        if value.get(key) is not True:
            raise ValueError(f"required fail-closed policy is false: {key}")
    if set(value.get("calibratedReviewCandidateBinding", [])) != REQUIRED_BINDINGS:
        raise ValueError("calibrated review is not bound to the complete candidate identity")
    rows = value.get("independentQualificationRows", {})
    if set(rows.get("routes", [])) != {"GPIO4", "GPIO20"}:
        raise ValueError("route qualification rows are not independent")
    if set(rows.get("modeFamilies", [])) != {"QRSS/TONE", "FSKCW", "DFCW", "WSPR"}:
        raise ValueError("mode qualification rows are incomplete")
    invalidation = value.get("changeInvalidation", {})
    for key in ("newCandidateIdentityRequired", "affectedPhase5EvidenceInvalidated",
                "affectedLifecycleTestsRepeated", "finalManifestReviewedAgain"):
        if invalidation.get(key) is not True:
            raise ValueError(f"change invalidation is incomplete: {key}")
    if set(invalidation.get("domains", [])) != REQUIRED_DOMAINS:
        raise ValueError("change invalidation domains are incomplete")
    snapshot = value.get("currentSnapshot", {})
    if snapshot != {"phase5PackagingPolicyOnly": True, "experimentalPrereleasePublished": False,
                    "calibratedReviewPerformed": False, "finalManifestReviewed": False,
                    "finalQualifiedReleasePublished": False}:
        raise ValueError("current Phase 5.12 snapshot overclaims external evidence")


validate(document)
for mutation in (
    lambda value: value.update(packagingClaimCeiling="Qualified"),
    lambda value: value.update(packagingNeverCreatesOrPreservesQualified=False),
    lambda value: value.update(finalReleaseRequiresNewReviewedManifest=False),
    lambda value: value.update(experimentalPrereleaseImmutable=False),
    lambda value: value["calibratedReviewCandidateBinding"].pop(),
    lambda value: value["changeInvalidation"]["domains"].pop(),
    lambda value: value["changeInvalidation"].update(affectedLifecycleTestsRepeated=False),
    lambda value: value["currentSnapshot"].update(calibratedReviewPerformed=True),
):
    invalid = copy.deepcopy(document)
    mutation(invalid)
    try:
        validate(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid calibrated-review release policy accepted")

print("Phase 5.12 calibrated-review release policy: PASS")
