<!-- SPDX-License-Identifier: MIT -->

# Phase 5.47 exact-freeze offline-checks-twice prompt

Validate the `offline-checks-twice` release gate against the exact Phase 5.47
source freeze `c5320ac5419a04d17345370204524f219b7ff403`, not the moving
worktree or later build-evidence commit. Use a clean detached worktree at that
commit and verify its identity and cleanliness before each run.

Run `tests/run-offline-checks.sh` twice as complete sequential executions.
Bind the exact retained Phase 5.43, Phase 5.45, and Phase 5.46 release archives
on both runs so all archived-envelope validators execute rather than skip.
Verify every archive hash before execution. Capture each complete transcript,
UTC start and finish, exit status, transcript hash, PASS/SKIP/FAIL counts, and
worktree identity. Require zero exit status, no missing output, and
byte-identical transcripts.

Independently compare the transcripts and adversarially review every skip and
claim. Only the three declared macOS-host Linux-target-only UAPI client compile
skips are acceptable. Representative stock-kernel build compatibility is
separate sealed evidence and must not be broadened into lifecycle or hardware
qualification. Record the complete common transcript durably.

Only after both runs pass may `offline-checks-twice` be marked passed. Retain
every later release gate as blocked. Do not construct Phase 5.47 Gate D
controls, connect to wspr5, stage target inputs, request authorization,
administer DKMS or a module, change overlays, services, or boot state, access
GPIO or I2C, operate the Si5351 or SDR, enable clocks, submit DMA, connect an
antenna, transmit, or produce RF.

Finish with focused and repository validation, adversarial review, staged-diff
inspection, commit and push only this slice, and report both run identities,
archive identities, skips, gate change, safety boundary, Git state, and next
gate.
