<!-- SPDX-License-Identifier: MIT -->

# Phase 5.49 exact-freeze offline-checks-twice prompt

Validate `offline-checks-twice` against exact Phase 5.49 source freeze
`99c4f3fa032ba7c752a3165b885b2786a89bc033`, not the moving worktree or the
later representative-build evidence commit. Use a clean detached worktree and
verify its identity and cleanliness immediately before each sequential run.

Create independent per-run copies of the sealed Phase 5.43, 5.45, 5.46, 5.47,
and 5.48 release archives. Verify each SHA-256 before execution. Bind those exact
copies to their archived-envelope validators and run
`tests/run-offline-checks.sh` twice. Capture complete transcripts, UTC bounds,
exit statuses, hashes, and PASS/SKIP/FAIL counts; require byte-identical
transcripts.

All five archived-envelope validators must execute and pass. Independently run
the Phase 5.49 representative-build evidence validator from its later evidence
commit; do not misrepresent it as part of the earlier frozen-source transcript.
The only permitted skips are the three declared macOS-host Linux-target-only
UAPI client compile checks. Independently review every skip, archive identity,
transcript claim, and final gate change.

After both runs pass, mark only `offline-checks-twice` passed. Keep all later
release gates blocked. Do not construct Phase 5.49 Gate D controls, connect to
wspr5, stage target inputs, request or consume lifecycle authorization,
administer DKMS or a module, change overlays, services, or boot state, access
GPIO or I2C, operate Si5351 or SDR hardware, enable clocks, submit DMA, connect
an antenna, transmit, or produce RF. Finish with independent evidence
validation, whitespace and staged-diff review, commit, push, and a clean
synchronized Git state.
