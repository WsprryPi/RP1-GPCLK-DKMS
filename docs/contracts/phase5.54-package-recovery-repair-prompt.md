<!-- SPDX-License-Identifier: MIT -->

# Phase 5.54 package-recovery repair prompt

## Objective

Produce one conventional Debian DKMS package revision that recovers the exact
half-configured `0.0.0~phase5.54-1` target state without attempting the
unrelated historical custom kernel and without requiring hard-link support on
`/boot/firmware`. Freeze module source, UAPI, and overlay contents.

## Bound evidence

- target failure capture:
  `74028d8a3ea0b620d37fc370eb1e53d8f70584bd09c2243fe52cfe941f7ed112`;
- failed package: `0.0.0~phase5.54-1`, SHA-256
  `a6bcc854bb807c298b07d81a0405960fbdc7e053df80802e2e95ebc2ca02f095`;
- target package state: `install ok half-configured`;
- allowed stock kernel suffixes: `+rpt-rpi-2712` and `+rpt-rpi-v8`;
- excluded historical custom kernel: `6.18.44-v8-16k+`.

## Required repair

1. Add an anchored `BUILD_EXCLUSIVE_KERNEL` rule for the two stock Raspberry
   Pi kernel-package identities. Prove the four captured stock identities are
   accepted and custom/local/RT variants are rejected. Exercise real DKMS and
   require the excluded case to return 77 while an allowed case passes kernel
   selection.
2. Keep canonical inactive DTBOs as package members below `/usr/lib`. Install
   them into `/boot/firmware/overlays` through minimal guarded maintainer
   scripts. Refuse to overwrite different bytes and remove only copies that
   still match the package canonical files.
3. Build revision `0.0.0~phase5.54-2` twice from one committed source identity
   and require byte-identical packages and literal member inventories.
4. In disposable Debian environments, prove both exact recovery paths:
   the half-configured `-1` package upgrades to configured `-2`, and the same
   upgrade succeeds while `link(2)` and `linkat(2)` beneath `/boot/firmware`
   are forced to fail. Verify both inactive overlays and clean purge.
5. Run package contract, kernel-scope, SPDX, whitespace, and applicable
   offline checks. Review the complete path-bearing package closure rather
   than treating deterministic generation as behavioral proof. Historical
   Phase 5.53 release-archive checks remain historical and are not rewritten
   to describe the Phase 5.54 Debian package.

## Boundaries

This slice is offline only. Do not contact a target; stage or install a target
artifact; load a module; activate an overlay; alter boot state; reboot; access
GPIO, clock, or DMA resources; transmit; or produce RF. Do not change module,
UAPI, DTS, or DTBO semantics. Stop on any identity, inventory, recovery,
ownership, or cleanup mismatch.

## Exit

Commit and push attributable source, tests, documentation, exact evidence, and
the separately bounded target-recovery authorization prompt. Target recovery
remains unauthorized until the operator explicitly authorizes the final
commit, package digest, failure capture, and operations.
