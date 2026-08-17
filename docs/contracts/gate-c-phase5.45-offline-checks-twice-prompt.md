<!-- SPDX-License-Identifier: MIT -->

# Phase 5.45 exact-freeze offline-checks-twice prompt

Validate the `offline-checks-twice` release gate against the exact Phase 5.45
source freeze `4b50db7868b7fe5ca9d830f51cd404c250192188`, not against a moving worktree
or a later evidence-only commit. Start from a clean, detached worktree at that
commit and verify its identity and cleanliness before either run.

Run `tests/run-offline-checks.sh` twice as two complete, sequential executions.
For both runs, supply an independently retained copy of the exact sealed Phase
5.43 archive with SHA-256
`a8a200d069ad433353a8812ef6a9a4c585b75a9f6af3d6501ac3672e90c997c3`
so the archived pre-root validator is exercised rather than skipped. Capture
each complete transcript, UTC start and finish, exit status, transcript hash,
PASS/SKIP/FAIL counts, and the worktree identity. Require both runs to exit
zero. Treat any omitted check, undeclared skip, archive mismatch, changed
worktree, nondeterministic release output, missing output, or differing
transcript as a blocker.

Independently compare the two transcripts and adversarially review every skip
and claim. The only acceptable skips are the three already declared macOS-host
Linux-only UAPI client compiles; the target representative build remains
separate evidence and must not be inferred from host compilation. Record the
complete common transcript durably so its reported checks remain inspectable.

If and only if both runs and the independent review pass, mark
`offline-checks-twice` passed with exact evidence and retain every later gate as
blocked. Do not construct or freeze a Phase 5.45 Gate D control set, request
target authorization, connect to or mutate `wspr5`, install or operate DKMS or
the module, change overlays or services, access GPIO or I2C, operate Si5351 or
SDR hardware, enable a clock, submit DMA, transmit, or produce RF.

Finish with repository validation, an explicit staged-diff review, commit and
push only the attributable slice on the current branch, verify a clean
synchronized worktree, and report the two run identities, skips, gate change,
safety boundary, commit, push, and next gated step.
