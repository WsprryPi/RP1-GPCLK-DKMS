<!-- SPDX-License-Identifier: MIT -->

# Phase 5.7 signing contract execution prompt

## Authority and exit condition

Execute only the module-signing contract portion of Phase 5A through Phase 5C
in `phase5-packaging-operator-enablement-execution-prompt.md`. Repository
changes, deterministic release generation, and offline tests are authorized.
Target access, key generation, key enrollment, DKMS registration/build/install,
module signing/loading/binding, boot changes, reboot, GPIO, clock, DMA,
transmission, RF, tagging, release publication, and consuming-repository changes
are not authorized.

Phase 5.7 closes when signing ownership, selection/generation, permissions,
enrollment, build integration, diagnosis, rotation, retention, and removal are
machine-readable; every required signing case fails closed or reaches only its
permitted state; release inputs exclude private key material; deterministic
offline tests pass twice; and a separate adversarial assessment has no finding.

## Governing inputs and boundary

Follow `AGENTS.md`, the module contract, the full Phase 5 prompt, the release
layout, installation model, permissions/enrollment policy, compatibility/update
policy, and upstream DKMS module-signing behavior. Signing establishes artifact
provenance and possible kernel load eligibility only. It never establishes
hardware compatibility, cleanup safety, enrollment, live eligibility, or RF
qualification. Do not weaken signature enforcement or select another physical
backend after signing failure.

## Signing identities and cases

Evaluate these cases separately and report a stable reason:

1. enforcement is not active: an unsigned exact-kernel module may be
   load-eligible under signature policy, but remains bounded by compatibility
   and enrollment gates;
2. the system accepts locally signed modules and the exact selected certificate
   is trusted: require a valid signature and exact signer fingerprint;
3. enforcement is active and a previously enrolled exact local certificate is
   trusted: require a valid signature and exact signer fingerprint;
4. the selected private key or certificate is missing: `Unavailable`;
5. the certificate is expired, replaced, revoked, or untrusted: `Unavailable`;
6. the signature is corrupt or cryptographically rejected: `Unavailable`;
7. the signed module's vermagic does not match the target kernel:
   `Unavailable`, regardless of signature validity.

Unknown enforcement, trust, signature, signer, fingerprint, vermagic, or target
kernel identity fails closed. A nonempty `modinfo signer` field alone is not
sufficient.

## Key ownership, generation, and enrollment

The release ships no private signing key, public certificate presented as a
pre-enrolled trust identity, passphrase, token, or key-generating side effect.
The administrator owns the local key and certificate outside source, release,
evidence, and package-owned paths. A filesystem private key must be a real
root-owned `0600` regular file in an administrator-selected directory; its
certificate must be a real root-owned regular file no broader than `0644`.
Hardware-backed/PKCS#11 keys require a separately reviewed provider contract.

The administrator may select an existing local module-signing identity or use
the installed distribution/DKMS procedure to generate one. Record the public
certificate SHA-256 fingerprint, subject, validity interval, extended-key-usage
result when enforced, and key location identifier without recording private
bytes or passphrases. If configured DKMS key paths are missing, stop; do not
accept silent generation of a replacement identity.

Enrollment imports only the intended public certificate using the platform's
documented MOK or firmware workflow. Password entry, firmware UI confirmation,
reboot, and post-reboot trust verification are separate administrator actions.
No install, update, or diagnostic command performs them automatically.

## DKMS build and verification contract

Use DKMS's native per-build signing mechanism, configured by the administrator
with exact `mok_signing_key`, `mok_certificate`, and target-kernel `sign_file`
paths. Verify supported DKMS behavior before relying on it. Every DKMS build,
including autoinstall after a kernel update, must either produce an exactly
signed module or fail closed. A project coordinator's one-time manual signature
does not cover later automatic rebuilds.

After each build and after installation, diagnose the exact file bytes and
record: file SHA-256, module release, vermagic, signer, signature key ID,
signature/hash algorithms, certificate fingerprint, target kernel, enforcement
state, and trust result. Reject mismatched build/installed hashes except for a
reviewed packaging transformation. Manual target-kernel `scripts/sign-file` is
an explicit recovery operation followed by the same complete verification; it
is not an enrollment or trust operation.

## Rotation, uninstall, and retention

Rotation is overlap-first: generate/select the successor, validate permissions
and validity, enroll and verify successor trust, configure DKMS to use it,
rebuild/sign/verify every retained target-kernel module, then retire the prior
identity only after no installed module depends on it. Any interruption leaves
live eligibility disabled and records which identity signed each module.

Package uninstall removes only package-owned signing policy/configuration and
records. It never deletes administrator-owned private keys, certificates,
tokens, firmware/MOK trust entries, or DKMS-global configuration. Complete
removal reports retained operator-owned identities. A key that signs other
local modules is intentionally retained. Trust-entry deletion is a separate
administrator action after a cross-module dependency audit.

## Offline implementation and validation

Add a machine-readable policy and pure deny-by-default evaluator, package both
in the release inventory, expand operator guidance, and add deterministic tests.
Cover every case above, unknown/malformed inputs, private-key permissions,
certificate validity/trust, exact fingerprint matching, corrupt signatures,
wrong-kernel vermagic, native DKMS per-build configuration, missing configured
keys, rotation ordering/interruption, uninstall retention, shared-key retention,
secret exclusion, no fallback, and no system/hardware effects. Inspect commands
before running them. Run SPDX, whitespace, links, release checks, and the full
offline suite twice.

## Adversarial reinjection loop

Separately try to falsify enforcement detection, trust and fingerprint binding,
certificate time/rotation handling, after-every-build coverage, automatic-key
replacement rejection, wrong-kernel rejection, removal ownership, shared-key
retention, secret exclusion, read-only purity, and absence of fallback/system/
hardware actions. Record each objective finding below, correct it, rerun affected
checks, and repeat until none remains.

### Reinjected findings

1. The first evaluator treated certificate validity, trust, and exact
   fingerprint as irrelevant whenever enforcement was disabled, even when a
   signature was present. Optional unsigned operation remains a separate case;
   a present signature now must satisfy the exact signed-identity contract.
2. The first implementation specified complete signer diagnosis but left the
   packaged diagnostic tool reporting only load state. Add bounded read-only
   `modinfo` collection for version, vermagic, signer, signature key ID,
   signature algorithm, and signature hash algorithm.
3. The inherited Phase 5.3 coordinator manually signed immediately after its
   own build and accepted any nonempty signer. Remove that normal-install
   signing path; require exact expected signer and signature-key IDs and verify
   the DKMS-native build and installed copies. Keep manual `sign-file` only as
   the separately invoked recovery operation.

All three findings were reinjected into implementation and regression tests.

## Completion report

Report changed behavior/files, exact test results, all signing cases, unresolved
target validation, licensing/documentation/UAPI impact, every system/hardware/RF
and publication action not performed, final Git state, and the next gated step.
Do not call all of Phase 5 complete.
