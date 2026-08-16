<!-- SPDX-License-Identifier: MIT -->

# Phase 5.31 installed-tool identity control-set correction prompt

Correct the Phase 5.31 Gate D control set exposed by the authorized pre-root
execution. Preserve the frozen candidate, reproducible release, representative
build, failed envelope, authorization commit, target staging, failure evidence,
and recovery record. Do not create a new candidate or repeat target execution.

Bind the bootstrap administrator `installedSha256`, its retained-tool entry,
the target-plan installed-tool identity, and the pre-root envelope
`installedTools` entry to the same frozen installed bytes. Generalize the
offline validator so every envelope installed tool equals the corresponding
bootstrap retained/administrator or target-plan tooling/import identity. Add a
negative mutation that recreates the stale administrator hash and require the
cross-document review to reject it.

Regenerate every dependent bootstrap, target-plan, attempt, index, execution-
instance, input-file, transition-file, and envelope hash. The corrected
instance must have `inputsReady=true`, `executionReady=false`, and
`targetExecutionApproved=false`; the failed authorization must not be reused.
Independently validate deterministic regeneration, all 38 fake attempts,
installed import closure, exact transition graph, and adversarial mutations.

This slice is offline only. Do not contact wspr5, install DKMS, load or bind a
module, activate an overlay, change services or boot state, access GPIO, enable
clocks, submit DMA, operate the separate I2C Si5351 path, touch a transmitter
or SDR, connect an antenna, or produce RF. Run the complete offline suite,
commit and push attributable changes, and stop for fresh target authorization.
