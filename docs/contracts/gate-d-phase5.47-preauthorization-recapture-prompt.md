<!-- SPDX-License-Identifier: MIT -->

# Phase 5.47 preauthorization canonical recapture prompt

Immediately before any Phase 5.47 lifecycle-authorization decision, perform a
second canonical read-only capture on `wspr5` using exact frozen capture and
independent-validation tool bytes, the same terminal recovery journal, and the
same physical declarations as the committed control-set snapshot. Use only
transient `/tmp` files and remove them after retrieval and validation.

Require the exact boot identity, stock kernel and canonical headers, signing
policy, terminal-complete predecessor administrator ledger, terminal recovery,
complete 28-path predecessor inventory, inactive runtime, and all six reviewed
services inactive. The separate I2C Si5351 path must remain disconnected and
unused, the SDR unused, and the antenna disconnected.

Validate independently on wspr5 and after retrieval. Compare raw bytes with
`docs/evidence/gate-d-live-target-snapshot-wspr5-phase5.47-v1.json`; require
exact size 7,057 and SHA-256
`7f018fb331c769c44eb1691fdabc4a8a6ff22e0a3debc9e1ed69404d829332b0`.
Any difference retires control-set commit
`547201f4973bc14776651962e0aba8e020b5a1f3` before authorization.

Only if bytes are identical, compare every snapshot-derived field in the
predecessor inventory, route decision, representative-build manifest, and
schema-5 pre-root envelope. Revalidate the complete Phase 5.47 control set and
the final envelope using the exact frozen Phase 5.47 archive tool bytes.
Record a durable attestation and independent review, run the complete
four-archive offline suite, and commit and push only these preauthorization
records and deterministic validation.

Do not alter authorization fields or `executionReady`; stage inputs; change
services; administer DKMS, modules, overlays, or boot state; access GPIO or
I2C; operate Si5351 or SDR hardware; enable clocks; submit DMA; connect an
antenna; transmit; or produce RF. This slice may establish eligibility for a
later separate digest-bound authorization decision; it cannot grant it.
