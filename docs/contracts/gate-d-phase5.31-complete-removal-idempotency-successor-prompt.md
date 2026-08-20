<!-- SPDX-License-Identifier: MIT -->

# Phase 5.31 complete-removal idempotency successor execution prompt

Create distinct successor `0.0.0-phase5.31` for frozen Phase 5.30. Preserve
every Phase 5.30 candidate, control-set, authorization, target staging, failure,
and recovery record. Phase 5.30 installed successfully with output disabled,
but its pre-root transition failed when `complete-removal` treated DKMS exit 3
for the already-absent historical predecessor as fatal.

Correct only the permanent lifecycle primitive's exact removal semantics.
Attempt the reviewed uninstall or remove command normally. If and only if that
command fails, query DKMS using the exact package and version; include the exact
kernel for uninstall, and require whole-version absence after `remove --all`.
Accept the failed command as already absent only when the bounded status query
succeeds and returns no state. Preserve the original failure when the status
query fails, returns any present state, names another kernel, is ambiguous, or
cannot establish the required absence. Do not parse error prose, suppress
arbitrary failures, use force, inspect unrelated packages, or weaken owned-path
identity and final-state checks.

Add deterministic tests for absent predecessor, present predecessor, a
different-kernel version remaining after whole-version removal, wrong
kernel/version scope, status-query failure, ordinary successful removal, and
repeated removal. Run the complete offline suite and a separate adversarial
assessment; correct every actionable finding and repeat affected checks.

Update lifecycle operator documentation and release notes. Commit the
implementation, freeze that exact clean commit with two isolated,
byte-identical development release builds, and record every identity. Perform
an exact build-only representative compile on `wspr5`; do not install or load
it. Do not bind, activate overlays, change services or boot state, reboot,
access GPIO, enable clocks, submit DMA, operate the separate I2C Si5351 path,
touch a transmitter or SDR, connect an antenna, or produce RF.

Stop after the representative-build result. A new Phase 5.31 Gate D control
set, independent control-set review, and explicit lifecycle authorization are
later gates. Do not tag, publish, open a pull request, or modify dependent
repositories. Report hashes, checks, target observations, cleanup, commits,
push state, and the remaining gate.
