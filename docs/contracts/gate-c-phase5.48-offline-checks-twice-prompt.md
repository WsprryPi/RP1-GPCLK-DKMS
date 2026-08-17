<!-- SPDX-License-Identifier: MIT -->

# Phase 5.48 exact-freeze offline-checks-twice prompt

Validate `offline-checks-twice` against exact Phase 5.48 source freeze
`ef96f246b66b25bb70536341b60a5f1e64708c65`, not the moving worktree or its
later representative-build evidence commit. Use a clean detached worktree and
verify its identity and cleanliness before each complete sequential run.

Bind independently generated exact copies of the sealed Phase 5.43, 5.45,
5.46, and 5.47 release archives on both runs. Verify every archive SHA-256
before execution. Run `tests/run-offline-checks.sh` twice, capture the complete
transcripts, UTC bounds, exit statuses, hashes, and PASS/SKIP/FAIL counts, and
require byte-identical transcripts.

All four archived-envelope validators must execute and pass. The only allowed
skips are the three declared macOS-host Linux-target-only UAPI client compile
checks. Independently review every skip and claim; representative build
compatibility remains separate evidence and establishes no lifecycle or
hardware qualification.

After both runs pass, mark only `offline-checks-twice` passed. Keep every later
release gate blocked. Do not construct Phase 5.48 Gate D controls, connect to
wspr5, stage target inputs, request or consume authorization, administer DKMS
or a module, change overlays, services, or boot state, access GPIO or I2C,
operate Si5351 or SDR hardware, enable clocks, submit DMA, connect an antenna,
transmit, or produce RF. Finish with independent evidence validation,
whitespace and staged-diff review, commit, push, and a clean synchronized Git
state.
