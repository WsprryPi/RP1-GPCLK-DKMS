<!-- SPDX-License-Identifier: MIT -->

# Phase 5.42 pre-authorization canonical recapture prompt

Immediately before any Phase 5.42 lifecycle authorization request, perform a
second read-only canonical live-target snapshot capture on `wspr5`. Execute the
committed capture implementation from commit
`71a9c3a6a27967d6c30398af9f9b01ef087738d7` without installing it on the
target or creating target evidence directories.

Require the same boot identity, stock kernel and canonical headers, signing
policy, current root-owned administrator ledger, terminal-recovery attestation,
complete package inventory, inactive runtime, and all six exact inactive
services. The operator reconfirms that the separate I2C Si5351 path is
disconnected and unused, the SDR is unused, and no antenna is connected.

Independently validate the newly captured document structurally and compare
its raw bytes and SHA-256 with committed canonical snapshot
`docs/evidence/gate-d-live-target-snapshot-wspr5-v1.json`, SHA-256
`d228a5fe8eaa52a2fa44d003947d51b2a3a6798e4535c0570c3836ab5b283b9a`.
Any byte, identity, state, service, inventory, ledger, recovery, signing, or
safety difference retires the Phase 5.42 proposed control set before
authorization.

If and only if the recapture is byte-identical, record a durable attestation
of the comparison, run focused and complete offline validation, independently
review the evidence, and commit and push those documentation-only bytes.

Do not freeze another successor, rebuild artifacts, regenerate controls,
change services, stage lifecycle inputs, request or record lifecycle
authorization, install or administer DKMS, load or bind a module, activate an
overlay, access GPIO, enable clocks, submit DMA, operate Si5351 or SDR
equipment, connect an antenna, transmit, or produce RF.
