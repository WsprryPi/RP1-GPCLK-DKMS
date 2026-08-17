<!-- SPDX-License-Identifier: MIT -->

# Phase 5.47 digest-bound output-disabled authorization decision prompt

The operator may authorize only the exact Phase 5.47 Gate D control set bound
by all of these identities:

- control-set commit: `547201f4973bc14776651962e0aba8e020b5a1f3`;
- preauthorization-attestation commit:
  `0bcacf062762afe01891a01f10fb83c57796af2c`;
- frozen source: `c5320ac5419a04d17345370204524f219b7ff403`;
- release archive SHA-256:
  `497368ac11b32e5491dab76103ad3bb2da0975c086e9898a801c5c2df1be82be`;
- canonical snapshot SHA-256:
  `7f018fb331c769c44eb1691fdabc4a8a6ff22e0a3debc9e1ed69404d829332b0`;
- preauthorization execution-instance SHA-256:
  `616fc066cde992c28dc2c9647dd93fc5bdf8ca9e70938642379017bae591cc16`;
- pre-root envelope SHA-256:
  `6d5aa62b1c4a0611ea97fcc7568b4b2b0d7448d5cd1bea36d0f9a5c59e738d1c`;
- 38-attempt index SHA-256:
  `dc68030fa86386659f92a93f56a96d05979af2c541d1be7bfc3e3b33c2e4651d`;
- preauthorization attestation SHA-256:
  `ad5c71fda19ff38c8f7e1823095de7e6c8df39b39222030d8b91928f1c0f5b5a`.

Authorization is limited to the 38 indexed attempts in the ten ready rows,
their namespace `phase5.47-c5320ac5419a`, the exact seven release artifacts,
the snapshot-derived 28-path Phase 5.45 predecessor inventory, the frozen
Phase 5.47 successor inventory, and the authenticated schema-5 pre-root,
ledger archival, recovery, service, stock-kernel, DKMS, overlay,
load-disabled, query, unbind/rebind, unload, bounded failure-injection, and
cleanup operations sealed in those controls. The five deferred environmental
rows remain excluded and are not substitutes.

The target baseline requires all six reviewed services inactive, the module
and endpoint absent, no route overlay, no test DKMS version, a
terminal-complete Phase 5.45 ledger, exact predecessor paths and kernel
identities, authenticated recovery, an unused SDR, no antenna, and the
disconnected and unused separate I2C Si5351 path. Any authorization requires a
byte-identical canonical recapture immediately before staging.

If explicitly authorized, update only the execution-instance authorization
fields and dependent hash edges. Deterministically regenerate and
independently validate the complete controls, including final-envelope
validation with the complete exact archived Phase 5.47 Python and executor
tool graph. Commit and push the authorized bytes before target staging.
Authorization is invalid if any bound identity or baseline changes.

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
authorizes these exact committed bytes, keep `targetExecutionApproved: false`
and `executionReady: false`; do not stage inputs or begin execution.
