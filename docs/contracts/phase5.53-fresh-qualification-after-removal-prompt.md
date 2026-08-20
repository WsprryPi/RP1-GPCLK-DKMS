<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 fresh qualification after removal prompt

## Objective

Add an authenticated qualification-install identity for the exact state where
the same-version product has been completely removed and therefore no package
path remains to transition in place.

## Requirements

1. Introduce additive qualification identity schema 4 without changing schema
   1–3 behavior.
2. Bind the identity to the original ledger SHA-256 and a canonical complete
   predecessor path inventory.
3. Require a terminal `removed`, `inactive-clean`, recovery-free,
   output-disabled administrator ledger for the same package and release.
4. Require exact semantic equality between the removed ledger inventory and
   the sealed identity inventory. Reject missing, duplicated, changed, or
   malformed paths.
5. Exercise complete fake-system removal, fresh qualification installation,
   qualification removal, and product-only reinstall.
6. Reproduce and independently validate the qualification successor twice.

## Non-goals

No target access, staging, pre-root transition, lifecycle attempt, module or
overlay activity, GPIO, clock, DMA, transmission, or RF activity.

## Exit criteria

The administrator accepts a fresh qualification installation only after the
exact authenticated removal state, all fake-system cleanup succeeds, and the
new qualification archive is deterministic.
