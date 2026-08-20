<!-- SPDX-License-Identifier: MIT -->

# Phase 5.51 exact-freeze offline-checks-twice prompt

Validate `offline-checks-twice` against exact Phase 5.51 source freeze
`cc87e0cdec7195eb69de2a6606f388e23ee0799c`, not the moving worktree or
representative-build evidence commit `7e61c9e3359916481dda744175fa57b9f0a10733`.
Use one clean detached worktree and verify its identity and cleanliness
immediately before each sequential run.

Create independent per-run copies of the sealed Phase 5.43, 5.45, 5.46, 5.47,
5.48, and 5.50 release archives. Verify every source and copy SHA-256 before
execution. Bind those exact copies to their archived-envelope validators and
run `tests/run-offline-checks.sh` twice. Capture complete transcripts, UTC
bounds, exit statuses, hashes, and PASS/SKIP/FAIL counts; require byte-identical
transcripts.

All six archived validators must execute and pass. The exact source freeze must
also pass the Phase 5.50 schema-2 control-set validator and the
self-contained permanent-executor schema-6 regression. Independently run the
Phase 5.51 representative-build evidence validator from evidence commit
`7e61c9e3359916481dda744175fa57b9f0a10733`; do not represent it as part of the
earlier frozen-source transcript. The only permitted skips are the three
declared macOS-host Linux-target-only UAPI client compile checks.

After both runs pass, mark only `offline-checks-twice` passed. Keep every later
release gate blocked. Do not construct Phase 5.51 Gate D controls, connect to
wspr5, stage target inputs, request or consume lifecycle authorization,
administer DKMS or a module, change overlays, services, or boot state, access
GPIO or I2C, operate Si5351 or SDR hardware, enable clocks, submit DMA, connect
an antenna, transmit, or produce RF. Finish with independent evidence
validation, whitespace and staged-diff review, commit, push, and a clean
synchronized Git state.
