<!-- SPDX-License-Identifier: MIT -->

# Phase 5.26 packaged topology adversarial assessment

Status: offline implementation review passed; clean-commit freeze pending

Phase 5.26 advances the release identity because the corrected target runbook
and authorization dossier are source-archive members. Both now state that the
Si5351 is a separate I2C-controlled RF output path, is not wired to GPIO4 or
GPIO20, and remains disabled, unkeyed, and isolated from the antenna or
test-output path during output-disabled lifecycle qualification. GPIO4 and
GPIO20 remain reserved for the RP1 GPCLK DKMS module.

The review challenged whether the correction was merely external prose. It is
not: deterministic release construction includes both corrected documents in
the source archive, and the Phase 5.26 regression rejects the former wording.
Phase 5.25 artifacts, representative-build records, qualification identity,
38-attempt bundle, execution instance, and reviews remain immutable historical
evidence and retain their original identities.

The first complete-suite pass exposed a version-coupled permanent-validator
assumption: `gate_d_preroot.py` hard-coded the current archive filename, which
made the checked Phase 5.25 schema-2 envelope uninspectable after the successor
version changed. The finding was classified as a packaged permanent-tool
defect and corrected without weakening validation. The archive filename is now
derived from the envelope's authenticated candidate release, while every
other role keeps its exact allowlisted filename; checksum membership is
derived from the already validated seven-role graph. Regression through the
complete Phase 5.25 control-set test proves historical validation remains
closed and byte-exact.

No kernel-module source, UAPI header, overlay source, route policy, schema, GPIO
behavior, GPCLK behavior, DMA behavior, or live-output eligibility changed.
Release-version identities, generic tests, release notes, candidate status,
and package paths changed as required. A successful offline build cannot exceed
offline reproducible and adversarially reviewed, and cannot reuse Phase 5.25
representative-build or lifecycle evidence.

The complete offline suite passed after reinjection of the validator finding.
The final implementation must pass the suite twice, then be committed. Two
release units must be built from that exact clean commit in separate
directories, validate independently, and be byte-identical before the freeze
record is committed. No Pi, package installation, DKMS mutation, module or
overlay administration, service or boot change, GPIO, GPCLK, DMA, helper,
Si5351, SDR, transmission, or RF work is authorized by this assessment.
