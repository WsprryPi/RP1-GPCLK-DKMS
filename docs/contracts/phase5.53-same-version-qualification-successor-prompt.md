<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 same-version qualification orchestration successor prompt

## Objective

Create a qualification-owned, authorization-free orchestration primitive for
transitioning from an installed product-only Phase 5.53 state to qualification
mode at the same version.

## Exact context

Preserve product archive
`032a0ca214427ebb6115b933042e7135f03c2ed6ce4f5c399686b2cf61395a76`
and the byte-identical target snapshot
`cbaed5a7972bb317a9dc27cabead9419ffde2db474df4de493373b6aa474524f`.
The target begins with terminal ledger `d4fe02f8...`, 72 owned product paths,
installed DKMS state, and no module, endpoint, overlay, or live output.

## Requirements

1. Model ledger-bound product removal, verified absence, qualification
   installation, verified output-disabled qualification state, and commit.
   Include a sealed-plan executable consumer; a library without a path-bearing
   entrypoint does not satisfy this requirement.
2. Distinguish command failure before a transition commits from interruption
   after it commits. Never invoke recovery against a terminal removed or
   installed ledger.
3. After every failure or interruption, recover the active administrator
   transaction if needed, remove any completed qualification installation,
   and restore the exact product-only prestate.
4. Keep `approved`, `targetExecutionApproved`, and `executionReady` false.
5. Include the primitive and its contract only in the qualification archive.
   Preserve the product archive and every historical control byte.
6. Generate the qualification successor twice, validate it independently, run
   one complete offline suite, record evidence and an adversarial review, and
   stop before new control construction or target access.

## Non-goals

Do not contact or mutate `wspr5`; stage inputs; perform a pre-root transition;
execute removal or installation; load a module; apply an overlay; reboot;
access GPIO; enable clocks; submit DMA; transmit; or produce RF.

## Exit criteria

Every command-failure and post-command interruption boundary restores the
product-only prestate in the fake system, the successor is deterministic and
independently valid, the complete offline suite passes, and no authority leaks
into the new qualification artifact.
