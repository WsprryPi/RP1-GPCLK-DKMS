<!-- SPDX-License-Identifier: MIT -->

# Phase 5.38 complete package-path closure execution prompt

## Objective

Create the offline Phase 5.38 successor that prevents another incremental
retained-path discovery failure. Replace the hand-maintained retained-tool
subset with one mechanically derived, fail-closed manifest of every
unversioned package-owned canonical destination that the qualification
installer can encounter or mutate.

## Bound context

Phase 5.37 stopped before lifecycle execution because the authenticated
22-tool transition omitted existing operator documentation. Recovery completed
and preserved the Phase 5.34 and Phase 5.36 archives plus the recovered Phase
5.37 canonical ledger. The observed retained surface includes 22 files under
`/usr/libexec/rp1-gpclk-dkms`, four files under
`/usr/share/doc/rp1-gpclk-dkms`, and two command symlinks under `/usr/sbin`.
Those observations are regression inputs, not a new hand-maintained list.

## Required implementation

1. Define one authoritative installation-plan expansion used by installation,
   qualification-transition validation, recovery, and tests. Expand archive
   trees and installed links to concrete canonical destinations. Do not keep a
   separate retained-path constant that can drift from installer behavior.
2. Before creating a transaction or invoking DKMS, compare the authenticated
   transition graph with the exact existing subset of all unversioned
   package-owned destinations in that expanded plan. Reject missing, extra,
   duplicate, non-canonical, wrong-type, wrong-owner, wrong-group, wrong-mode,
   wrong-hash, wrong-link-target, or symlink-substituted entries.
3. Represent regular files and symlinks explicitly. Bind predecessor and
   successor SHA-256 for regular files and exact relative link targets for
   symlinks. Directories must be checked for type, ownership, and mode; preserve
   administrator-owned contents where the release contract requires it.
4. Transition each authenticated retained destination exactly once through an
   atomic, journaled operation. Recovery must restore predecessor bytes or link
   target, mode, owner, and group. A successor may commit only after the entire
   expanded graph is exhausted and verified.
5. Add deterministic temporary-root tests that derive expected paths from the
   installation plan and prove: the current 28 observed retained destinations
   are covered; every single omission fails before transaction creation and
   before external commands; extra and duplicate entries fail; each supported
   type substitution and identity mutation fails; and injected failure at
   every replacement boundary recovers the full predecessor graph byte for
   byte and link for link.
6. Add an explicit regression proving that adding a future unversioned
   package-owned installer destination without a corresponding manifest
   expansion makes validation fail. No allowlist count alone is sufficient.
7. Document the Phase 5.37 root cause, Phase 5.38 invariants, evidence, and
   remaining gates. Correct every actionable adversarial finding and repeat
   affected checks until clean.

## Constraints and non-goals

This is offline repository work only. Do not connect to or mutate `wspr5`; do
not install, load, bind, unbind, or unload a module; do not invoke DKMS against
the host; do not change overlays, boot, services, GPIO, clocks, DMA, Si5351,
SDR, antenna, transmission, or RF state. Do not retry or modify the sealed
Phase 5.37 execution. Do not create a Phase 5.38 freeze, representative build,
control set, or execution authorization in this step.

## Validation and exit criteria

Run focused installation/transition/recovery tests, the complete offline test
suite, whitespace and SPDX checks, and available documentation-link checks.
Independently challenge source-of-truth drift, path expansion, type confusion,
pre-mutation ordering, journal completeness, recovery at every boundary, and
the separate I2C Si5351 versus GPIO4/GPIO20 documentation contract. Exit only
with a mechanically complete path closure, clean adversarial assessment, no
target activity, and an explicit statement that the next gate is a new
Phase 5.38 freeze and representative build.
