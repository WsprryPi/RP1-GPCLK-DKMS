<!-- SPDX-License-Identifier: MIT -->

# Phase 5.52 preauthorization canonical recapture prompt

Immediately before any Phase 5.52 lifecycle-authorization decision, capture
wspr5 twice with the exact frozen Phase 5.52 read-only capture-tool bytes, the
sealed Phase 5.51 GPIO20 terminal lifecycle journal, and the same physical
declarations as control-set commit
`477d0b0c62b70a56a6ca61e9b3b56114461db2e5`. Stream the tool over
authenticated SSH and create no target tool file.

Require exact boot, stock kernel and canonical headers, signing policy,
terminal-complete Phase 5.51 administrator ledger, complete 28-path predecessor
inventory, inactive runtime, and all six reviewed services inactive. The
separate I2C Si5351 path must remain disconnected and unused, the SDR unused,
and the antenna disconnected.

Require both captures to be byte-identical to the committed 7,083-byte
canonical snapshot with SHA-256
`449201a0a51ca8b278b7ae077410e515aa9c176eac42f4ba86bd62ef4c36451f`.
Any difference retires the control set before authorization.

Only after exact equality, revalidate all snapshot-derived fields, the complete
schema-6 control set, all 38 schema-2 attempts, false authorization/readiness,
and the final qualification-root envelope using exact frozen Phase 5.52 release
archive SHA-256
`0c67dee49a26bf5ab103d04bcf493bba8ae373a9f45b87e5704f52ede96bce01`.
Record a durable attestation and independent review.

Do not alter authorization fields or `executionReady`; stage inputs; perform a
pre-root transition; change services; administer DKMS, modules, overlays, or
boot state; access GPIO or I2C; operate Si5351 or SDR hardware; enable clocks;
submit DMA; connect an antenna; transmit; or produce RF. This slice can only
establish eligibility for a later, separate, digest-bound authorization
decision.
