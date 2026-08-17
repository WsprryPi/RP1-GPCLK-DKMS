<!-- SPDX-License-Identifier: MIT -->

# Phase 5.51 digest-bound output-disabled authorization decision prompt

The operator may authorize only the exact Phase 5.51 Gate D control set bound
by all of these identities:

- control-set commit: `64baef473a04810627598015b32797e46e6e43a2`;
- preauthorization-attestation commit:
  `cd81650bd324ec3e8d608bfe2cc67252d34e4e88`;
- frozen source: `cc87e0cdec7195eb69de2a6606f388e23ee0799c`;
- release archive SHA-256:
  `253bd54054eb0b673f9e61c58a46b6b7ca2cf78d756fe4e80656f4ac1233f549`;
- canonical snapshot SHA-256:
  `badb3633cdf6bacce6fa3292174d3cea993a1ed4f0278f75c597bd204ee63e9a`;
- preauthorization execution-instance SHA-256:
  `37317c18c907ddd9af9856bade74fd3ec5e60aaab046fa2732cb81de8de5c81a`;
- pre-root envelope SHA-256:
  `7f64de228549c1a64748d80a6123e18c0dbc07e63861d0e192b5ddfe0098e444`;
- 38-attempt index SHA-256:
  `a1d547226090dbcb58375774983ebe7a0fa3cd05e30963b58d7dc2e5524f2960`;
- preauthorization attestation SHA-256:
  `68a9f644ffd365a3429fcd17650384243aa977977bbd5922743af350ff460f72`.

Authorization is limited to the 38 indexed schema-2 attempts in the ten ready
rows, their namespace `phase5.51-cc87e0cdec71`, the exact seven release
artifacts, the snapshot-derived 28-path Phase 5.50 predecessor inventory, the
frozen Phase 5.51 successor inventory, and the authenticated schema-6 pre-root,
ledger archival, recovery, service, stock-kernel, DKMS, overlay,
load-disabled, query, unbind/rebind, unload, bounded failure-injection, and
cleanup operations sealed in those controls. The five deferred environmental
rows remain excluded and are not substitutes.

The target baseline requires all six reviewed services inactive, the module
and endpoint absent, no route overlay, no test DKMS version, a terminal-complete
Phase 5.50 administrator ledger, exact predecessor paths and kernel identities,
authenticated recovery, an unused SDR, no antenna, and the disconnected and
unused separate I2C Si5351 path. Any authorization requires a byte-identical
canonical recapture immediately before staging.

All four attempt-controlled services are snapshot-bound to the inactive
`preserve` action. Any missing, duplicate, changed, active, or inconsistent
service state/action record invalidates authorization.

If explicitly authorized, update only the execution-instance `approved`,
`targetExecutionApproved`, approval-scope, and dependent hash edges.
Deterministically regenerate and independently validate the complete controls,
including final-envelope validation with the complete exact archived Phase
5.51 Python, schema, and executor tool graph. Commit and push the authorized
bytes before target staging. Authorization is invalid if any bound identity or
baseline changes.

Execution must use only the authenticated pre-root transition, sealed-root
policy and module graph, and installed permanent tools. Stop on the first
identity, state, timeout, service, recovery, residue, cleanup, transition, or
safety discrepancy. Use only journal-authorized recovery. Terminal pre-root
recovery must return without starting an attempt.

Output remains disabled. Active pinctrl, clock enablement, DMA submission,
GPIO output, Si5351 operation, transmitter keying, SDR operation, antenna
connection, RF, `/dev/mem`, custom-kernel qualification, forced removal,
general upgrade, and unreviewed persistent boot mutation are prohibited.

This prompt does not itself record authorization. Until the operator explicitly
authorizes these exact committed bytes, keep `approved: false`,
`targetExecutionApproved: false`, and `executionReady: false`; do not stage
inputs or begin execution.
