<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 product-only reinstall-reset prompt

## Objective

Provide the bounded reset required to replace an already installed development
candidate with a new candidate that has the same DKMS package version. Use the
existing terminal installation ledger as the complete ownership authority,
remove that owned installation, and then permit an ordinary fresh product-only
installation. Do not reconstruct qualification transition controls.

## Requirements

- Add an explicit root-only `remove --execute` administrator action.
- Accept only a terminal `complete` installation ledger with
  `liveOutput=false`, `checkpoint=commit-state`, and no recovery requirement.
- Before mutation, validate every ledger-owned file, symlink, and committed
  replacement against its recorded current identity. Reject missing, changed,
  ambiguous, duplicate, non-absolute, or unsafe paths.
- Run only the bounded DKMS uninstall/remove commands for the exact recorded
  package, version, and kernel, then remove only ledger-owned current files and
  empty ledger-owned directories. Never restore superseded predecessors after
  a completed installation.
- Leave a terminal removal ledger and preserve fail-closed recovery-required
  state on an interrupted or failed removal.
- Prove offline that a complete product installation can be removed and the
  unpublished product-only candidate reinstalled without the qualification
  archive, with both inactive overlays present and no Gate D tools installed.
- Prove tampered and foreign files stop removal before any external command or
  filesystem mutation.

## Constraints

This slice is offline only. Do not contact a target, run real DKMS, install or
load a module, apply an overlay, edit boot configuration, reboot, access GPIO,
clock, or DMA state, transmit, or perform RF activity. Do not regenerate a
release candidate in this slice.

## Exit criteria

Focused tests and the complete offline suite pass, an adversarial review finds
no unresolved ownership or recovery defect, and the next gated action is a new
deterministic product-candidate build from the repaired source.
