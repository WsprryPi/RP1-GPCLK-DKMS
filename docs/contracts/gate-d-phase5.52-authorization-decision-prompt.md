<!-- SPDX-License-Identifier: MIT -->

# Phase 5.52 digest-bound output-disabled authorization decision prompt

The operator may authorize only the exact Phase 5.52 Gate D control set bound
by all of these identities:

- control-set commit: `477d0b0c62b70a56a6ca61e9b3b56114461db2e5`;
- preauthorization-attestation commit:
  `38861a81155242caac79dcecc3cfcc722843d0c2`;
- frozen source: `f710554c4697d75210cbd33c9eea13474d60557a`;
- release archive SHA-256:
  `0c67dee49a26bf5ab103d04bcf493bba8ae373a9f45b87e5704f52ede96bce01`;
- canonical snapshot SHA-256:
  `449201a0a51ca8b278b7ae077410e515aa9c176eac42f4ba86bd62ef4c36451f`;
- preauthorization execution-instance SHA-256:
  `735a57afd22879f6818fe727341f4c7d5dc4c9d13f0600ce404991bfb3f46c45`;
- pre-root envelope SHA-256:
  `5de1a85eafa53a50829d19799655a8f680760e16bb83a39ffdd284b9aafaaf52`;
- 38-attempt index SHA-256:
  `744427cc21988c73558dd7a2c89fdbf97915288bf539941e67a8cf080c0e90d8`;
- preauthorization attestation SHA-256:
  `39319ae9025ce37d935e06d33fa8bcb8401c8db70fab7d3b38a97d50578c9a8a`.

Authorization is limited to the 38 indexed schema-2 attempts in the ten ready
rows, their namespace `phase5.52-f710554c4697`, the exact seven release
artifacts, the snapshot-derived 28-path Phase 5.51 predecessor inventory, the
frozen Phase 5.52 successor inventory, and the authenticated schema-6 pre-root,
ledger archival, recovery, service, stock-kernel, DKMS, overlay, load-disabled,
query, unbind/rebind, unload, bounded failure-injection, and cleanup operations
sealed in those controls. The five deferred environmental rows remain excluded
and are not substitutes.

The target baseline requires all six reviewed services inactive, the module
and endpoint absent, no route overlay, no test DKMS version, a terminal-complete
Phase 5.51 administrator ledger, exact predecessor paths and kernel identities,
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
5.52 Python, schema, and executor tool graph. Commit and push the authorized
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
