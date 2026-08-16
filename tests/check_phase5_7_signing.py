#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Deterministic offline checks for the Phase 5.7 signing contract."""

from __future__ import annotations

import importlib.util
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("signing_policy", ROOT / "scripts/signing_policy.py")
policy_module = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(policy_module)

policy = json.loads((ROOT / "release/signing-policy-v1.json").read_text())
assert policy["schemaVersion"] == 1
assert policy["releasePrivateKeyPolicy"] == "prohibited"
assert policy["buildIntegration"]["mechanism"] == "dkms-native-per-build-signing"
assert set(policy["buildIntegration"]["requiredConfiguration"]) == {
    "mok_signing_key", "mok_certificate", "sign_file"}
assert policy["buildIntegration"]["missingConfiguredIdentity"] == "fail-closed-no-automatic-replacement"
assert policy["ownership"]["privateKey"]["mode"] == "0600"
assert policy["uninstall"] == {"removePackagePolicy": True, "removeOperatorKeys": False,
                                "removeCertificates": False, "removeTrustEntries": False,
                                "reportRetainedIdentities": True}
assert policy["rotationOrder"].index("verify-successor-trust") < policy["rotationOrder"].index("configure-dkms-successor")
assert policy["rotationOrder"].index("rebuild-sign-verify-retained-kernels") < policy["rotationOrder"].index("retire-prior-identity-if-unused")

fingerprint = "11:22:33:44"
base = {
    "targetKernel": "6.18.1+rpt", "moduleVersion": "0.0.0-phase5.39",
    "vermagicKernel": "6.18.1+rpt", "moduleSha256": "a" * 64,
    "enforcement": "enforced", "signatureStatus": "valid", "signer": "Local DKMS",
    "signatureKeyId": "1234", "signatureAlgorithm": "PKCS#7",
    "signatureHashAlgorithm": "sha256", "certificateFingerprint": fingerprint,
    "expectedCertificateFingerprint": fingerprint, "certificateValidity": "valid",
    "certificateTrust": "trusted", "privateKeyState": "available-secure",
    "dkmsPerBuildSigningConfigured": True, "configuredIdentityReplacement": "none"
}


def result(**changes):
    return policy_module.evaluate({**base, **changes})


accepted = result()
assert accepted["state"] == "Compatible-unqualified" and accepted["liveEligible"] is False
assert accepted["fallbackPermitted"] is False and accepted["readOnly"] is True

unsigned = result(enforcement="not-enforced", signatureStatus="unsigned", signer="none",
                  signatureKeyId="none", signatureAlgorithm="none", signatureHashAlgorithm="none",
                  certificateFingerprint="none", expectedCertificateFingerprint="none",
                  certificateValidity="unknown", certificateTrust="not-required",
                  privateKeyState="not-required", dkmsPerBuildSigningConfigured=False)
assert unsigned["signaturePolicyAccepted"] is True
assert unsigned["reason"] == "unsigned-accepted-by-nonenforcing-kernel-policy"

for changes, reason in (({"enforcement": "not-enforced", "certificateTrust": "untrusted"}, "certificate-untrusted"),
                        ({"enforcement": "not-enforced", "certificateValidity": "expired"}, "certificate-expired"),
                        ({"enforcement": "not-enforced", "certificateFingerprint": "AA:BB"}, "certificate-fingerprint-mismatch")):
    assert result(**changes)["reason"] == reason

cases = (
    ({"enforcement": "accepts-trusted-local"}, None),
    ({"privateKeyState": "missing"}, "private-key-missing"),
    ({"privateKeyState": "unsafe-permissions"}, "private-key-unsafe-permissions"),
    ({"certificateValidity": "expired"}, "certificate-expired"),
    ({"certificateValidity": "not-yet-valid"}, "certificate-not-yet-valid"),
    ({"certificateTrust": "untrusted"}, "certificate-untrusted"),
    ({"certificateTrust": "revoked"}, "certificate-revoked"),
    ({"signatureStatus": "corrupt"}, "signature-corrupt"),
    ({"signatureStatus": "unsigned"}, "required-signature-absent"),
    ({"vermagicKernel": "6.17.0+rpt"}, "wrong-kernel-vermagic"),
    ({"certificateFingerprint": "AA:BB"}, "certificate-fingerprint-mismatch"),
    ({"signer": "none"}, "signature-metadata-incomplete"),
    ({"dkmsPerBuildSigningConfigured": False}, "dkms-per-build-signing-not-configured"),
    ({"configuredIdentityReplacement": "silent-replacement-detected"}, "configured-signing-identity-replaced"),
)
for changes, reason in cases:
    evaluated = result(**changes)
    if reason is None:
        assert evaluated["signaturePolicyAccepted"] is True
    else:
        assert evaluated["state"] == "Unavailable" and evaluated["reason"] == reason
        assert evaluated["loadPermittedBySigningPolicy"] is False and evaluated["fallbackPermitted"] is False

for mutation in ({"enforcement": "unknown"}, {"certificateTrust": "maybe"},
                 {"moduleSha256": "bad"}, {"unexpected": "field"}):
    try:
        policy_module.evaluate({**base, **mutation})
    except ValueError:
        pass
    else:
        raise AssertionError(f"malformed signing snapshot passed: {mutation}")

layout = json.loads((ROOT / "release/release-layout-v1.json").read_text())
paths = {item["path"] for item in layout["artifacts"]}
assert {"release/signing-policy-v1.json", "scripts/signing_policy.py"} <= paths
installation = json.loads((ROOT / "release/installation-model-v1.json").read_text())
admin = installation["ownership"]["administratorFiles"] if "ownership" in installation else installation["administratorFiles"]
assert admin["packageUninstall"] == "retain-and-report"

for path in ROOT.rglob("*"):
    if path.is_file() and ".git" not in path.parts:
        assert path.suffix.lower() not in {".key", ".pem", ".p12", ".pfx", ".der"}, path

prompt = (ROOT / "docs/contracts/phase5-7-signing-contract-execution-prompt.md").read_text()
operator = (ROOT / "docs/operator/signing.md").read_text()
for phrase in ("no shared private signing key", "every DKMS build", "wrong kernel", "shared with another module"):
    assert phrase.lower() in (prompt + operator).lower()
for prohibited in ("modprobe ", "dtoverlay ", "/dev/mem"):
    assert prohibited not in (ROOT / "scripts/signing_policy.py").read_text()

diagnostics = (ROOT / "scripts/rp1-gpclk-diagnostics.py").read_text()
for field in ("vermagic", "signer", "sig_key", "sig_id", "sig_hashalgo"):
    assert field in diagnostics

administrator = (ROOT / "scripts/rp1-gpclk-admin.py").read_text()
assert "scripts/sign-file" not in administrator
assert "exact expected DKMS signer and signature key ID are required" in administrator
assert "required module signer identity differs" in administrator
assert "required module signature key ID differs" in administrator

print("Phase 5.7 signing contracts: PASS")
