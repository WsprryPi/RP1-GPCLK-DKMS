<!-- SPDX-License-Identifier: MIT -->

# Phase 5.50 preauthorization canonical recapture prompt

Immediately before any Phase 5.50 lifecycle-authorization decision, perform a
second canonical read-only capture on `wspr5` using the exact frozen Phase 5.50
capture and independent-validation tool bytes, the same terminal recovery
journal, and the same physical declarations as the committed control-set
snapshot. Stream the tools over authenticated SSH; create no target tool file.
Use only transient `/tmp` data files and remove every one after validation.

Require the exact boot identity, stock kernel and canonical headers, signing
policy, terminal-complete predecessor administrator ledger, terminal recovery,
complete 28-path predecessor inventory, inactive runtime, and all six reviewed
services inactive. The separate I2C Si5351 path must remain disconnected and
unused, the SDR unused, and the antenna disconnected.

Capture twice and require byte equality. Validate independently on wspr5 and
after retrieval. Compare raw bytes with
`docs/evidence/gate-d-live-target-snapshot-wspr5-phase5.50-v1.json`; require
exact size 7,082 and SHA-256
`3db85e0ada2427c997cdca878d0f2d53fc0c61d5aab68761e65a2a6cf349a6d5`.
Any difference retires control-set commit
`8e908928642bf3a4052f13cfb087c77a9bcbc7f8` before authorization.

Only if bytes are identical, compare every snapshot-derived field in the
predecessor inventory, route decision, representative-build manifest, and
schema-5 pre-root envelope. Revalidate the complete schema-6 Phase 5.50 control
set and its final envelope using the exact frozen Phase 5.50 release archive
bytes. Record a durable attestation and independent review, run the complete
offline suite with the exact archive supplied, and commit and push only these
preauthorization records and deterministic validation.

Do not alter authorization fields or `executionReady`; stage inputs; change
services; administer DKMS, modules, overlays, or boot state; access GPIO or
I2C; operate Si5351 or SDR hardware; enable clocks; submit DMA; connect an
antenna; transmit; or produce RF. This slice may establish eligibility for a
later separate digest-bound authorization decision; it cannot grant it.
