<!-- SPDX-License-Identifier: MIT -->

# Gate D successor terminal-cleanup repair prompt

Implement an offline-only, backward-compatible successor to the terminal
cleanup defect recorded at commit `26924c0e5111b5a301a12c3480a665edaca18cbd`
and cleaned at commit `f77ef6c0dadc6e284bdc012c10e9c34456382ece`.

Preserve schema-1 generation and validation exactly so frozen Phase 5.48
controls remain reproducible. Add schema 2 as an explicit opt-in recipe. Every
schema-2 row must contain exactly one `remove-attempt-residue`, after
`restore-services` and immediately before `audit-residue`; rows that already
used the operation internally must not contain a duplicate. Retain the closed
dispatcher, exact owned-path containment, symlink rejection, bounded recursive
removal, and evidence sealing order.

For schema 2, make `audit-residue` verify the staging path is actually absent.
Use an authoritative filesystem probe that accepts only `ENOENT`; treat access
denial, an existing path, a link, or any other error as a discrepancy. Do not
use an unprivileged convenience probe to infer absence beneath a protected
parent.

Add deterministic regression coverage that generates and validates all 38
schema-2 attempts, proves one correctly ordered cleanup step per attempt,
executes a representative complete attempt against the stateful rooted fake,
requires its staging tree absent before sealing, rejects permission-denied
absence probes, and confirms schema-1 Phase 5.48 generation remains unchanged.
Run focused checks, the complete offline suite, whitespace checks, and an
adversarial diff review.

Do not regenerate or modify Phase 5.48 controls, freeze a successor release,
build or stage target inputs, install tools, modify wspr5, retry attempt 1, or
begin attempt 2. No module, overlay, GPIO, clock, DMA, Si5351, SDR, antenna,
transmission, or RF activity is authorized by this slice.
