<!-- SPDX-License-Identifier: MIT -->

# Phase 5.34 pre-root successor execution prompt

## Objective

Create the smallest offline successor to the failed Phase 5.33 execution. Make
successful pre-root recovery terminal and establish the authoritative rule for
the next qualification identity: predecessor hashes come from the last
successfully installed retained-tool graph, Phase 5.31, not from an uninstalled
or failed Phase 5.32/5.33 candidate.

## Verified context

Phase 5.33 failed before DKMS installation because its identity expected the
Phase 5.32 successor `gate-d-executor` hash while wspr5 correctly retained the
Phase 5.31 hash. Its sealed `--resume` path cleaned the partial root but then
incorrectly began a fresh attempt. Both failures were preserved and wspr5 was
returned to an inactive baseline.

## Required changes

1. After authenticated recovery removes the partial root and preserves the
   failure journal, re-probe the inactive baseline and return `recovered`.
   Recovery must never fall through to fresh execution.
2. Extend deterministic tests to prove no second administrator invocation,
   no recreated qualification root, immutable failure evidence, and failure on
   a changed post-recovery baseline.
3. Record that Phase 5.34 control generation must source every predecessor
   path/hash from the last successful Phase 5.31 retained-tool manifest and
   independently compare it with the live read-only target inventory before
   sealing.
4. Perform a separate adversarial review and correct every actionable finding.

## Scope boundary

This slice is offline source, test, and documentation work only. Do not rewrite
historical Phase 5.33 artifacts. Do not freeze or build Phase 5.34, stage target
inputs, install or load a module, activate overlays, access GPIO, enable clocks,
submit DMA, operate the separate I2C Si5351 path, use an SDR or transmitter,
reboot, transmit, or produce RF.

## Validation and exit criteria

Run the focused pre-root tests, the complete offline suite, documentation-link
and whitespace checks, and an independent adversarial assessment. Exit only
when recovery is observably terminal, the predecessor-source rule is explicit,
all checks pass, and the commit is pushed with a clean synchronized worktree.
The next gate is a distinct Phase 5.34 freeze and representative build.
