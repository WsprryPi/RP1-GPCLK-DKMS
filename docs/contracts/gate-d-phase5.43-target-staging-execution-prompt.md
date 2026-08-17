<!-- SPDX-License-Identifier: MIT -->

# Phase 5.43 authenticated target staging and execution prompt

Execute only the Phase 5.43 authorization committed at
`18c4d0cf3c98b0258533c857468728364ea9e228`. Bind staging and execution to
frozen source `aa92b0550acd66671fe1988510cf93987cd61c0a`, archive SHA-256
`a8a200d069ad433353a8812ef6a9a4c585b75a9f6af3d6501ac3672e90c997c3`,
authorized execution-instance SHA-256
`9b5b6657ef750b4b082e830426fd8db9fe0cd3edb1d50a46dcb97f64831de5c8`,
schema-5 pre-root envelope SHA-256
`8fcd182d92c1ce9d29ba0cd0a78218345d20f9ec887a30a164d966ab179b9a4b`,
attempt-index SHA-256
`7aea0b0842788831da229bfb9a28e42c98a96034e25da137819e170c3db4a6fc`,
and canonical snapshot SHA-256
`d228a5fe8eaa52a2fa44d003947d51b2a3a6798e4535c0570c3836ab5b283b9a`.

Before staging, perform another read-only capture and require raw byte identity
with the canonical snapshot. Require the inactive runtime, six inactive
services, terminal `complete` Phase 5.39 ledger, authenticated recovery,
separate disconnected and unused I2C Si5351 path, unused SDR, no antenna, and
available recovery.

Create only the exact new input directory declared by the authorized envelope.
Populate it from the checksummed release unit, committed control set, and exact
frozen archive. In addition to the envelope's 67 `inputFiles`, stage the exact
envelope document itself at the control-set release path and verify it against
the separately authorized envelope SHA-256; the document cannot recursively
list its own bytes. Verify every input path and SHA-256 against the envelope
before privileged execution. Run the staged archived outer executor in
read-only pre-root validation mode and require success.

Invoke the authenticated schema-5 pre-root transition once. It may archive only
the exact snapshot-bound administrator ledger, install the exact Phase 5.43
qualification package, remove only declared runtime residue, and create the
authenticated qualification root. Stop on failure. If its journal authorizes
recovery, run only its `--resume` recovery and return without beginning an
attempt.

After a successful transition, validate the installed permanent executor,
qualification root, execution instance, and attempt index. Execute only the 38
indexed attempts in index order. Preserve each immutable journal and evidence
directory. Stop at the first discrepancy or recovery-required result; never
skip ahead, substitute a row, or reuse a journal. Use only the sealed recovery
document and journal path when recovery is explicitly authorized.

Output remains disabled. Prohibit active pinctrl, clock enablement, DMA
submission, GPIO output, Si5351 operation, transmitter keying, SDR operation,
antenna connection, RF, `/dev/mem`, custom-kernel qualification, forced
removal, general upgrade, and unreviewed persistent boot mutation.

At the terminal boundary, require inactive runtime, no candidate DKMS test
version, no overlay, no endpoint, no live output, restored services as declared,
complete immutable evidence, and exact owned-path cleanup. Independently assess
the result, preserve failure evidence, and commit and push documentation only.
