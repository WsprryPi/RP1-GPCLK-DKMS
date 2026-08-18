#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate the exact non-authorizing Phase 5.53 staging decision prompt."""
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
prompt=(ROOT/"docs/contracts/gate-d-phase5.53-staging-preroot-authorization-decision-prompt.md").read_text()
expected={"2d1a5c3e5ca2388679423aa4f2f0f07a56c2d830","2838380a639d7af71ddc53be20829efd56cedc1d","1884c0f1c53c661495576bf10ce08d8bf7a90bc3","ae6df3a66a9a26a6fb8474e5896c9053b9f69580d8c45383a5556fc397ebb549","834d05c5c5da0c383c4a229eaeff9dae07a4359b","d931912d6ccc381b10a2a13d7f3a9122b0f748490ec8eefe0f86a28cb352c8d0","df8e80bc4b3382d9213d52cbc273b398e85124a2d2f58169c3a6f6aa339dbcf7","b53c07ac634936339469a6f1345717f20ec7d1e40855656df83ffd9c1780a6d7","6b9125621ed7047feaf5649798edaca73c72c9685d08848bbe95f7b9ed857027","aa07ee829ee01d0bdcdfbc3c0882b2ddd582c9f48c5e8b69253b315522a47e9c","3a6a6047dc8e3ca5c77488a5029bb2165f5b9e71bf32fdc94ec60dcf15ec15e2","c4bdf3e066527941e5762229d0162b738bea542ec8d47a2cdfda0e66ef7a0ebb","17220ae534936e55fc1710edcd8cebff88add93adb82bd607e020714569a175d","b3ae7d71aa1eb8881450b068f9c3525ecf33925ab797419c735b9f4f5aca18cb"}
assert all(value in prompt for value in expected)
envelope=json.loads((ROOT/"release/gate-d-pre-root-bootstrap-envelope-phase5.53-v1.json").read_text())
assert len(envelope["inputFiles"])==64 and len(envelope["releaseInputs"])==8
assert len(envelope["transitionFiles"])==55 and len(envelope["installedTools"])==22
attestation=json.loads((ROOT/"docs/evidence/gate-d-phase5.53-preauthorization-recapture-attestation.json").read_text())
assert hashlib.sha256((ROOT/"docs/evidence/gate-d-phase5.53-preauthorization-recapture-attestation.json").read_bytes()).hexdigest() in prompt
assert attestation["authorization"]["targetStagingAuthorized"] is False
assert attestation["authorization"]["preRootTransitionAuthorized"] is False
assert "This prompt does not itself authorize staging" in prompt
assert "Stop before lifecycle attempt 1" in prompt
print("Phase 5.53 staging and pre-root authorization decision: PASS")
