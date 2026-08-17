<!-- SPDX-License-Identifier: MIT -->

# Phase 5.46 preauthorization canonical recapture prompt

Immediately before any Phase 5.46 lifecycle-authorization decision, perform a
second canonical read-only capture on `wspr5` using the committed capture
implementation, the same terminal recovery journal, and the same physical
declarations as the control-set snapshot. Use transient `/tmp` copies only and
remove them after the evidence has been retrieved and validated.

Require the exact boot identity, stock kernel and canonical headers, signing
policy, terminal-complete Phase 5.45 administrator ledger, terminal recovery,
complete 28-path predecessor inventory, inactive runtime, and all six reviewed
services inactive. The separate I2C Si5351 path must remain disconnected and
unused, the SDR unused, and the antenna disconnected.

Independently validate the recapture on the target and again after retrieval.
Compare its raw bytes with
`docs/evidence/gate-d-live-target-snapshot-wspr5-phase5.46-v1.json`; require
exact size 7,057 and SHA-256
`bc4c307350d6e74c9cbb85ef890fbaf0e8ad969ecdeb661a98703b70bd4a1859`.
Any byte difference retires control-set commit
`f1e5fa27bed175533f6a291152fa70700b88285b` before authorization.

Only if the bytes are identical, compare every snapshot-derived field in the
predecessor inventory, route decision, representative-build manifest, and
schema-5 pre-root envelope. Revalidate the complete Phase 5.46 control set and
the final envelope with the exact frozen Phase 5.46 archive bytes. Record a
durable attestation and independent review, run the complete archive-bound
offline suite, and commit and push only those preauthorization records and
their deterministic validator.

Do not alter authorization fields or `executionReady`; stage inputs; change
services; administer DKMS, modules, overlays, or boot state; access GPIO or
I2C; operate the Si5351 or SDR; enable clocks; submit DMA; connect an antenna;
transmit; or produce RF. This slice may establish eligibility for a later,
separate digest-bound authorization decision. It cannot grant authorization.
