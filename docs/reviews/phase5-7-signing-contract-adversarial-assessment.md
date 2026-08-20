<!-- SPDX-License-Identifier: MIT -->

# Phase 5.7 signing contract adversarial assessment

Date: 2026-08-15
Disposition: no unresolved objective finding

## Scope

This separate offline review attempted to falsify enforcement-case separation,
trust and certificate-fingerprint binding, certificate validity and rotation,
after-every-build coverage, missing-key and automatic-replacement handling,
signature-corruption and wrong-kernel rejection, uninstall/shared-key ownership,
secret exclusion, diagnostic completeness, read-only purity, and absence of
fallback, system mutation, or hardware action.

## Findings and reinjection

1. The initial evaluator accepted an expired, untrusted, or mismatched signed
   identity when the kernel did not enforce signatures. It now permits the
   unsigned/non-enforcing case separately but fully validates any signature
   that is present. Negative regression cases cover all three defects.
2. The initial implementation promised signer diagnosis without extending the
   packaged diagnostic command. The command now collects bounded, read-only
   `modinfo` results for module version, vermagic, signer, signature key ID,
   signature algorithm, and signature hash algorithm. Tests assert this surface
   and continue to prohibit mutating commands.
3. The inherited package coordinator manually appended a signature after its
   orchestrated DKMS build and accepted any nonempty signer. It now accepts no
   private-key/certificate arguments for normal installation, requires exact
   expected signer and signature-key IDs, and verifies those on both the DKMS
   build and installed module. The separate manual lifecycle command is
   retained only for explicitly invoked recovery.

## Final assessment

Unsigned operation is accepted only when enforcement is explicitly known to be
off. Both trusted-local cases require the exact valid trusted fingerprint and
complete signature metadata. Missing/unsafe key material, silent replacement,
expiry, revocation, distrust, corruption, incomplete metadata, absent required
signature, and wrong-kernel vermagic are unavailable and non-live. DKMS native
per-build signing covers autoinstall conceptually; target verification remains
separately gated. Operator-owned and shared identities are retained on uninstall
and rotation is overlap-first. The release excludes key-like files. No path
loads a module, mutates trust or DKMS, changes hardware, or permits backend
fallback. No objective finding remains.
