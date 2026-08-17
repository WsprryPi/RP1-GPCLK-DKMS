<!-- SPDX-License-Identifier: MIT -->

# Phase 5.43 authorized output-disabled execution prompt

Bind the operator's explicit authorization to Phase 5.43 control-set commit
`4233960e95d35eb69295c0352a2f25c020aefc15`, frozen source
`aa92b0550acd66671fe1988510cf93987cd61c0a`, recapture-attestation commit
`946c0d4635e8bcf531176dff4f85c973962c3a3e`, archive SHA-256
`a8a200d069ad433353a8812ef6a9a4c585b75a9f6af3d6501ac3672e90c997c3`,
canonical snapshot SHA-256
`d228a5fe8eaa52a2fa44d003947d51b2a3a6798e4535c0570c3836ab5b283b9a`,
pre-authorization execution-instance SHA-256
`5f092e551f195c53e683d1aed5626c0d8013961e0b9989c39519c3aa5168117f`,
and attempt-index SHA-256
`7aea0b0842788831da229bfb9a28e42c98a96034e25da137819e170c3db4a6fc`.

Authorization is limited to the 38 indexed attempts in the ten ready rows, the
exact seven-artifact representative-build inventory, the snapshot-derived
28-path Phase 5.39 predecessor inventory, the frozen Phase 5.43 successor
inventory, and authenticated schema-5 pre-root, current-ledger archival,
recovery, service, stock-kernel, DKMS, overlay, load-disabled, query,
unbind/rebind, unload, failure-injection, and cleanup operations. Five
environmental rows remain deferred and are not authorized substitutes.

The exact archived pre-root validation attestation has SHA-256
`651a126a75b1be27cc9183d9d9be5b59148f2e88a088794fe78c53bbc606fcc4`.
Recompute the authorized execution-instance and all dependent hash edges.
Deterministically regenerate the controls, repeat independent snapshot and
schema validation, and rerun the complete suite with the exact Phase 5.43
release archive supplied so archived-tool validation cannot skip. Commit and
push authorized bytes before target staging.

On `wspr5`, require the byte-identical canonical snapshot, terminal
`complete` Phase 5.39 ledger, exact predecessor inventory, inactive runtime,
six inactive services, authenticated recovery, exact release inputs, stock
kernel/header/configuration/signing identities, disconnected and unused
separate I2C Si5351 path, unused SDR, no antenna, and available recovery.

Execute only through the authenticated schema-5 pre-root transition and
installed permanent tools. Archive only the exact snapshot-bound administrator
ledger before successor installation. Stop at the first identity, state,
timeout, service, recovery, residue, cleanup, transition, archived-tool, or
safety discrepancy. Use only journal-authorized recovery; terminal pre-root
recovery must return without beginning another attempt.

Output remains disabled. Prohibit active pinctrl, clock enablement, DMA
submission, GPIO output, Si5351 operation, transmitter keying, SDR operation,
antenna connection, RF, `/dev/mem`, custom-kernel qualification, forced
removal, general upgrade, and unreviewed persistent boot mutation.

This slice records authorization only. Do not stage target lifecycle inputs or
begin execution until authorized bytes are committed, pushed, synchronized,
and revalidated.
