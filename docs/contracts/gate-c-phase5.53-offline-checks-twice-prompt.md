<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 exact-freeze split-artifact offline-checks-twice prompt

Validate `offline-checks-twice` against exact Phase 5.53 split-artifact source
freeze `1884c0f1c53c661495576bf10ce08d8bf7a90bc3`, not the moving worktree or
the later artifact-recording and roadmap commits.

Use one clean detached worktree and verify its identity and cleanliness before
both sequential runs. Give each run independent copies of the sealed product
and qualification release unit and all exact Phase 5.43, 5.45, 5.46, 5.47,
5.48, 5.50, 5.51, and 5.52 historical archives. Verify every archive SHA-256.
For each run, independently validate the complete Phase 5.53 release unit so
both split archives, their roots, inventories, metadata, checksums, and source
bytes are checked. Then bind all eight historical archives to their archived
validators and run `tests/run-offline-checks.sh`.

Require the ordinary-install regression to prove the product archive neither
requires nor installs qualification tooling. Require qualification mode to
fail closed without its separate archive and to bind both exact archives when
enabled. Capture complete transcripts, UTC bounds, exit statuses, hashes, and
PASS/SKIP/FAIL counts; require byte-identical transcripts. The only permitted
skips are the three declared macOS-host Linux-target-only UAPI client compile
checks.

After both runs and an independent evidence review pass, mark only
`offline-checks-twice` passed and remove only its candidate blocker. Keep every
later gate blocked. Do not perform a representative build or lifecycle matrix,
connect to a target, stage target inputs, administer DKMS, modules, overlays,
services, or boot state, access GPIO or I2C, enable clocks, submit DMA, operate
SDR or Si5351 hardware, connect an antenna, transmit, or produce RF. Finish
with whitespace, documentation-link, machine-readable evidence, and staged-
diff checks, then commit and push only the attributable files.
