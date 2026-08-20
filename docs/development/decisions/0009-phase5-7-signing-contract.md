<!-- SPDX-License-Identifier: MIT -->

# Decision 0009: Phase 5.7 signing contract

Status: accepted
Date: 2026-08-15

## Context

The package described manual signing after an orchestrated build and checked
only for a nonempty signer. That did not cover later DKMS autoinstall builds,
bind the signer to the selected certificate, or fully define local-key rotation
and removal ownership.

## Decision

Use DKMS's native per-build signing facility with administrator-selected
`mok_signing_key`, `mok_certificate`, and target-kernel `sign_file`. Missing
configured key material is an error; silent replacement is a new untrusted
identity. Diagnose exact module bytes, target-kernel vermagic, signature state,
signer metadata, selected certificate fingerprint/validity, and kernel trust.

Keys, certificates, tokens, DKMS-global configuration, and trust entries remain
administrator-owned. The release contains no private key. Package uninstall
retains and reports them; removing an old trust identity requires a separate
cross-module dependency audit. Rotation enrolls and proves the successor before
rebuilding retained kernels and retiring the predecessor.

## Consequences

Signing failure is `Unavailable` and never permits fallback. Passing signing
policy reaches at most `Compatible-unqualified`; compatibility and live-output
gates remain independent. Target enrollment, reboot, build, signing, loading,
and trust verification remain future separately authorized evidence.
