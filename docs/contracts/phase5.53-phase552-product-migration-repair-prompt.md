<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 Phase 5.52 product-migration repair prompt

## Objective

Repair and prove the one real deployment path: the exact terminal Phase 5.52
installation currently on `wspr5` to a fresh Phase 5.53 product-only inactive
installation. The real target ledger closure, not a blank synthetic root, is
the predecessor authority.

## Requirements

- Capture the complete target predecessor read-only and require ledger SHA-256
  `0261c25f785458a0ee3cd270e4a7afcb606f5a86fdb99fc019aae231388c78f1`,
  782 owned files, 28 committed replacements, 26 owned directories, no live
  identity mismatches, and no registered DKMS row.
- Permit removal only for the explicit Phase 5.52 or current Phase 5.53
  predecessor release recorded in a valid terminal ledger. Derive versioned
  deletion roots and DKMS commands from that authenticated predecessor release.
- Query exact-version DKMS state before mutation. If the row is absent, perform
  no DKMS uninstall/remove command; if present, run only the exact predecessor
  uninstall/remove pair. Any command failure remains recovery-required.
- Exercise Phase 5.52 path topology, DKMS-present and DKMS-absent removal,
  tamper rejection, failure injection, and product-only Phase 5.53 reinstall
  with both inactive overlays and no qualification archive.
- Build the repaired candidate twice from a clean committed source, validate
  both, and rerun the migration through the extracted packaged administrator.

## Boundary

Target inspection in this slice is read-only. Do not transfer files or mutate
the target. Do not load a module, apply an overlay, edit boot configuration,
reboot, access GPIO/clock/DMA, transmit, or perform RF activity. Stop for one
final target-mutation authorization after the repaired candidate is committed.
