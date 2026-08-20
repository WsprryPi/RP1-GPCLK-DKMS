#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
evidence = json.loads((ROOT / "docs/evidence/release-1.0.0-final-review-claim-audit.json").read_text())
roadmap = json.loads((ROOT / "release/release-integration-gates-v1.json").read_text())
prompt = (ROOT / "docs/contracts/release-1.0.0-module-publication-authorization-prompt.md").read_text()
gates = {gate["id"]: gate for gate in roadmap["gates"]}

assert all(evidence["audit"].values())
assert evidence["archiveStatusBoundary"]["sealedArtifactsRebuiltDuringReview"] is False
assert evidence["publicationFinalizer"]["changesOnlyOuterMetadataAndChecksums"] is True
assert evidence["publicationFinalizer"]["preservesProductSha256"] is True
assert evidence["publicationFinalizer"]["preservesQualificationSha256"] is True
assert evidence["remoteState"]["localTagAbsent"] is True
assert evidence["remoteState"]["remoteTagAbsent"] is True
assert evidence["remoteState"]["publicReleaseApiStatus"] == 404
assert evidence["remoteState"]["githubCliAuthenticationValid"] is True
assert evidence["remoteState"]["githubCliAuthenticationSource"] == "macOS keyring verified outside sandbox"
assert {"repo", "workflow"} <= set(evidence["remoteState"]["githubCliTokenScopes"])
assert evidence["remoteState"]["publicationAuthenticationPrerequisiteSatisfied"] is True
assert evidence["publicationAuthorized"] is False
assert evidence["published"] is False
assert evidence["publicDownloadVerified"] is False
assert roadmap["currentClassification"] == "published-release-awaiting-fresh-download-verification"
assert gates["release-review-and-claim-audit"]["status"] == "passed"
assert gates["module-publication"]["status"] == "passed"
for identity in (evidence["productPackageSha256"], evidence["qualificationArchiveSha256"]):
    assert identity in prompt
for phrase in ("GitHub CLI", "annotated `v1.0.0` tag", "attach exactly", "do not delete", "treating the release"):
    assert phrase in prompt

print("Release 1.0.0 final review and claim audit: PASS")
