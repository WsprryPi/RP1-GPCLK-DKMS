<!-- SPDX-License-Identifier: MIT -->

# Phase 5.52 exact-freeze offline-checks-twice prompt

Validate `offline-checks-twice` against exact Phase 5.52 source freeze
`f710554c4697d75210cbd33c9eea13474d60557a`, not the moving worktree or
representative-build evidence commit
`376e930b28eb7cb9dda78acca30afb8e4332793d`.

Use one clean detached worktree and verify its identity and cleanliness
immediately before each sequential run. Create independent per-run copies of
the sealed Phase 5.43, 5.45, 5.46, 5.47, 5.48, 5.50, and 5.51 release archives.
Verify every source and copy SHA-256 before execution. Bind those exact copies
to their archived-envelope validators and run `tests/run-offline-checks.sh`
twice. Capture complete transcripts, UTC bounds, exit statuses, hashes, and
PASS/SKIP/FAIL counts; require byte-identical transcripts.

All seven archived validators must execute and pass. The exact source freeze
must also pass the Phase 5.50 and Phase 5.51 control-set validators, the
self-contained permanent-executor schema-6 regression, and every negative
trust case. Independently run the Phase 5.52 representative-build evidence
validator from evidence commit `376e930b28eb7cb9dda78acca30afb8e4332793d`;
do not represent it as part of the earlier frozen-source transcripts. The only
permitted skips are the three declared macOS-host Linux-target-only UAPI client
compile checks.

After both runs pass, mark only `offline-checks-twice` passed. Keep every later
release gate blocked. Do not construct Phase 5.52 Gate D controls, connect to a
target, stage target inputs, request or consume lifecycle authorization,
administer DKMS or a module, change overlays, services, or boot state, access
GPIO or I2C, operate Si5351 or SDR hardware, enable clocks, submit DMA, connect
an antenna, transmit, or produce RF. Finish with independent evidence
validation, whitespace and staged-diff review, commit, push, and a clean
synchronized Git state.
