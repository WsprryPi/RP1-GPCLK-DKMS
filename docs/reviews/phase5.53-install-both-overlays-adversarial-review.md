<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 install-both-overlays adversarial review

## Outcome

Pass for offline installation behavior. Both route artifacts are installed
inactive in one product transaction; route selection remains separate.

## Assertions challenged

1. Both DTBO names must be present in the authenticated checksum set before
   installation proceeds.
2. One product-only transaction installs byte-exact GPIO4 and GPIO20 artifacts
   with mode `0644` while installing the DKMS module only once.
3. The installer iterates the fixed two-entry route allowlist; no arbitrary
   route or filename can enter the installation set.
4. A symlink or different pre-existing artifact on either allowlisted
   destination fails closed. An identical existing artifact is preserved.
5. The transaction records every newly created overlay so existing recovery
   and exact-owned-file removal semantics continue to apply.
6. Installation does not invoke `dtoverlay`, edit boot configuration, reboot,
   load the module, or select an active route.

## Safety and claim ceiling

No release archive was regenerated and no target, module, overlay, GPIO,
clock, DMA, transmission, or RF operation occurred. This change is validated
offline and must be included in a new product candidate before target use.
