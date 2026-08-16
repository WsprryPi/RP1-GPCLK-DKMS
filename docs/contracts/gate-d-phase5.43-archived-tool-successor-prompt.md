<!-- SPDX-License-Identifier: MIT -->

# Phase 5.43 archived-tool-validated successor prompt

Freeze successor `0.0.0-phase5.43` from schema-5-capable commit
`3b0cc513db165127c59488b34b85242c746d7d22`. Preserve all Phase 5.42
authorization and failure evidence unchanged. Advance only active candidate
identities, deterministic fixtures, release paths, and new Phase 5.43 records.

The ordering is mandatory:

1. Commit and push a clean Phase 5.43 freeze containing the schema-5-capable
   outer executor, pre-root module, schemas, snapshot comparator, and tests.
2. Generate two isolated non-publishable release units using the freeze commit
   timestamp. Validate both and require byte identity.
3. Extract the exact archive and prove its own outer/pre-root graph accepts the
   final schema-5 envelope. Development-worktree imports are prohibited for
   this regression.
4. Perform the exact unprivileged representative build on `wspr5`, preserving
   input, environment, transcript, and output hashes and the inactive baseline.
5. Generate a new deterministic Phase 5.43 control set from the frozen archive
   identities and canonical snapshot. Keep target authorization and execution
   readiness false.
6. Regenerate into a clean temporary tree, independently compare every
   target-derived field with the snapshot, validate the final envelope using
   only the exact archived module bytes, run the complete offline suite, and
   correct every actionable finding.

Bind the same canonical snapshot SHA-256
`d228a5fe8eaa52a2fa44d003947d51b2a3a6798e4535c0570c3836ab5b283b9a`
only if a fresh read-only target capture remains byte-identical before later
authorization. Preserve separate predecessor and successor inventories and the
terminal `complete` Phase 5.39 administrator ledger.

Do not authorize lifecycle execution, stage lifecycle inputs, install or
administer DKMS, mutate ledgers, load or bind a module, activate an overlay,
alter services or boot, access GPIO, enable clocks, submit DMA, operate the
separate I2C Si5351 path, operate SDR or transmitter equipment, connect an
antenna, transmit, or produce RF.

Exit only with a clean pushed freeze, byte-identical releases, passing exact
representative build, deterministic snapshot-bound controls, successful
archived-tool validation of the final envelope, independent clean review,
pushed evidence/control commits, and a clean synchronized worktree.
