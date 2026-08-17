<!-- SPDX-License-Identifier: MIT -->

# Phase 5.43 pre-authorization canonical recapture prompt

Immediately before any Phase 5.43 authorization request, perform a second
read-only canonical live-target capture on `wspr5` using the committed capture
implementation. Do not install the capture program or create target evidence
directories.

Require the exact boot identity, stock kernel and canonical headers, signing
policy, root-owned terminal `complete` administrator ledger, terminal-recovery
attestation, complete 28-path predecessor inventory, inactive runtime, and all
six exact inactive services. The operator reconfirms that the separate I2C
Si5351 path is disconnected and unused, the SDR is unused, and no antenna is
connected.

Independently validate the new capture and compare its raw bytes and SHA-256
with committed snapshot
`docs/evidence/gate-d-live-target-snapshot-wspr5-v1.json`, SHA-256
`d228a5fe8eaa52a2fa44d003947d51b2a3a6798e4535c0570c3836ab5b283b9a`.
Any difference retires the Phase 5.43 proposed control set before
authorization.

If and only if the recapture is byte-identical, record a durable attestation
bound to control-set commit
`4233960e95d35eb69295c0352a2f25c020aefc15`, run focused and complete offline
validation with the exact Phase 5.43 release archive supplied so archived-tool
validation cannot skip, independently review the evidence, and commit and push
documentation-only results.

Do not authorize lifecycle execution, regenerate controls, change services,
stage lifecycle inputs, install or administer DKMS, mutate ledgers, load or
bind a module, activate overlays, access GPIO, enable clocks, submit DMA,
operate Si5351 or SDR equipment, connect an antenna, transmit, or produce RF.
