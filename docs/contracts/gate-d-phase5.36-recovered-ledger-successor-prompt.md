<!-- SPDX-License-Identifier: MIT -->

# Phase 5.36 recovered-ledger successor prompt

## Objective

Remove the concrete Phase 5.35 pre-root blocker by defining and implementing a
bounded authenticated handoff for the canonical terminal `recovered`
administrator ledger. Produce offline implementation and adversarial evidence;
do not freeze or execute a new candidate in this step.

## Required behavior

- Extend the pre-root envelope additively so a successor can bind the exact
  canonical ledger path, SHA-256, owner, mode, terminal semantic fields, and a
  unique historical archive path.
- Accept only `status=recovered`, `recoveryRequired=false`, and
  `liveOutput=false`; reject missing, substituted, symlinked, permission-unsafe,
  nonterminal, or already-archived state.
- Journal before moving the authenticated ledger. Move it atomically to the
  bound archive path, make the archive read-only, and leave the canonical path
  available for the new administrator transaction.
- If interrupted before administrator invocation, sealed recovery must restore
  the exact prior ledger to its canonical path. It must never discard or
  overwrite foreign bytes.
- Preserve existing schema-version-1 and schema-version-2 behavior.

## Validation and safety

Add deterministic offline tests for successful archival, interruption and
restoration, tamper rejection, nonterminal rejection, path closure, mode and
owner enforcement, and legacy-envelope behavior. Run the complete offline
suite and a separate adversarial assessment.

Do not access wspr5 except read-only identity inspection. Do not delete or move
its ledger, stage a successor, administer DKMS, load a module, activate an
overlay, touch GPIO or clocks, operate Si5351/SDR/transmitter equipment,
reboot, transmit, or produce RF.
