<!-- SPDX-License-Identifier: MIT -->

# Phase 5.51 preauthorization canonical recapture prompt

Immediately before any Phase 5.51 lifecycle-authorization decision, capture
wspr5 twice with the exact frozen Phase 5.51 read-only capture-tool bytes, the
same sealed Phase 5.48 terminal lifecycle journal, and the same physical
declarations as control-set commit
`64baef473a04810627598015b32797e46e6e43a2`. Stream the tool over authenticated
SSH and create no target tool file.

Require exact boot, stock kernel and canonical headers, signing policy,
terminal-complete Phase 5.50 administrator ledger, complete 28-path predecessor
inventory, inactive runtime, and all six reviewed services inactive. The
separate I2C Si5351 path must remain disconnected and unused, the SDR unused,
and the antenna disconnected.

Require both captures to be byte-identical to the committed 7,082-byte
canonical snapshot with SHA-256
`badb3633cdf6bacce6fa3292174d3cea993a1ed4f0278f75c597bd204ee63e9a`.
Any difference retires the control set before authorization.

Only after exact equality, revalidate all snapshot-derived fields, the complete
schema-6 control set, all 38 schema-2 attempts, false authorization/readiness,
and the final qualification-root envelope using exact frozen Phase 5.51 release
archive SHA-256
`253bd54054eb0b673f9e61c58a46b6b7ca2cf78d756fe4e80656f4ac1233f549`.
Record a durable attestation and independent review.

Do not alter authorization fields or `executionReady`; stage inputs; perform a
pre-root transition; change services; administer DKMS, modules, overlays, or
boot state; access GPIO or I2C; operate Si5351 or SDR hardware; enable clocks;
submit DMA; connect an antenna; transmit; or produce RF. This slice can only
establish eligibility for a later, separate, digest-bound authorization
decision.
