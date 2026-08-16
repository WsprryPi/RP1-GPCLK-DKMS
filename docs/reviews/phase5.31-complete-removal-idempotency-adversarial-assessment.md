<!-- SPDX-License-Identifier: MIT -->

# Phase 5.31 complete-removal idempotency adversarial assessment

Status: implementation review passed; representative build still required

The review challenged arbitrary error suppression, reliance on DKMS error
prose, package/version/kernel scope, `remove --all` semantics, status-query
failure, present and other-kernel state, ordinary success, repeated removal,
and output or ownership-policy drift.

The implementation catches only a failed DKMS `uninstall` or `remove` command.
It queries the same exact package and version, includes the exact kernel after
uninstall, and deliberately omits the kernel after `remove --all` so any
remaining version registration on another kernel blocks acceptance. The
original failure is accepted only when that query itself succeeds and its
complete output is empty. Any nonempty output or query failure stops the
primitive. Successful removals do not issue a compensating status query; the
existing final-state audit remains authoritative.

Tests cover fully absent state, present exact state, another-kernel state,
status-query failure, ordinary success, and repeated removal. The change does
not add force, parse diagnostics, inspect unrelated packages, weaken owned-path
hashes, load or bind a module, activate an overlay, access GPIO, or enable
clock, DMA, Si5351, transmitter, SDR, antenna, transmission, or RF behavior.
