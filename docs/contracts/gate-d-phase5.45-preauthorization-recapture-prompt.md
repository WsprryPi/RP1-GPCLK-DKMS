<!-- SPDX-License-Identifier: MIT -->

# Phase 5.45 preauthorization canonical recapture prompt

Immediately before any Phase 5.45 authorization decision, perform a second
canonical read-only capture on `wspr5` using the committed capture
implementation and the same terminal recovery path and physical declarations
as the control-set snapshot. Do not install the capture program or create a
target evidence directory; transient `/tmp` copies must be removed.

Require the exact boot identity, stock kernel and canonical headers, signing
policy, terminal-complete Phase 5.43 administrator ledger, terminal recovery,
complete 28-path predecessor inventory, inactive runtime, and all six reviewed
services inactive. The operator-established baseline keeps `wsprrypi.service`,
`sdrplay.service`, and `soapyremote-server.service` stopped and disabled. The
separate I2C Si5351 path remains disconnected and unused, the SDR remains
unused, and no antenna is connected.

Independently validate the recapture, compare its raw bytes with
`docs/evidence/gate-d-live-target-snapshot-wspr5-phase5.45-v1.json`, and require
exact size 7,057 and SHA-256
`66208586a112792e91185a7ce67d5952427dc218fb8a392ac1bfb221ed51e4c8`.
Any byte difference retires control-set commit
`53e55780d6e1aec4551836e9c499de501a83a602` before authorization.

If and only if the bytes are identical, independently compare every
snapshot-derived field in the predecessor inventory, route decision,
representative-build manifest, and schema-5 pre-root envelope. Revalidate the
complete Phase 5.45 control set and validate the final envelope using only the
exact frozen Phase 5.45 archive bytes. Record a durable attestation and
independent review, run the complete archive-bound offline suite, and commit
and push only those preauthorization records.

Do not change authorization fields, set `targetExecutionApproved` or
`executionReady`, stage target inputs, change services, install or administer
DKMS, operate the module or overlays, access GPIO or I2C, operate the Si5351 or
SDR, enable clocks, submit DMA, connect an antenna, transmit, or produce RF.
This slice may establish eligibility for a separate digest-bound authorization
decision; it cannot grant that authorization.
