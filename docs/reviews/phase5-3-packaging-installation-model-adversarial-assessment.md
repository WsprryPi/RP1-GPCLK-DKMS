<!-- SPDX-License-Identifier: MIT -->

# Phase 5.3 packaging and installation model adversarial assessment

## Scope and evidence class

This is a separate offline assessment of the Phase 5.3 prompt, frozen install
model, coordinator, simulated transaction tests, release integration, and
operator documentation. It covers no real DKMS registration, build,
installation, signing, module load, overlay activation, boot change, target,
GPIO, DMA, transmission, or RF work.

## Findings and reinjection

The first pass found that signing named the final installed module rather than
DKMS's kernel-and-architecture-specific built artifact, and that the frozen
libexec, command, documentation, and configuration destinations were not all
installed. Both requirements were added to the execution prompt; the
coordinator and simulator now assert them.

The second pass found that successful `modinfo` execution did not compare the
returned version, vermagic, or signer, and that recovery recognized an inactive
failure but could not repair package-owned residue. The prompt now requires
value comparisons and digest-journaled recovery. The coordinator verifies the
built and installed module identities, records every created file and
directory durably, uses exact-version DKMS removal, refuses changed files, and
preserves unrelated overlays and administrator enrollment.

The final pass attempted to falsify destination completeness, route isolation,
archive/path/symlink safety, staged hashes, signing order and secrecy, module
metadata checks, output-disabled state, overlay inactivity, enrollment
absence, checkpoint durability, failure classification, recovery ownership,
idempotent absence, and prohibited fallback or boot actions. No unresolved
objective finding remains in the offline model.

## Claim boundary

The result freezes and simulates the installation model only. Target behavior,
DKMS layout on a representative distribution, signing enforcement, actual
rollback/recovery, permissions after privileged installation, overlay boot
activation, reboot behavior, and complete removal remain Phase 5 target
lifecycle evidence. A build or simulated transaction cannot exceed
`Compatible-unqualified` and does not enable live output.
