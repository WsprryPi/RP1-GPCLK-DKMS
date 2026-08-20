<!-- SPDX-License-Identifier: MIT -->

# Phase 5.45 phase-scoped successor construction prompt

Implement the prerequisite path contract for the next frozen Gate D successor.
Extend execution-instance schema 5 with a mandatory
`attemptPathNamespace` equal to the candidate release plus the first twelve
hexadecimal characters of its source commit. Require every ready matrix row's
evidence root to be exactly below that namespace.

Generate all 38 attempt evidence directories, journals, staging directories,
owned-path inventories, subordinate transition and recovery evidence, and
reboot-resume journals within
`/var/lib/rp1-gpclk-dkms/gate-d/runs/<attemptPathNamespace>/`. Preserve
historical schema 1 through 4 controls without rewriting them.

Add deterministic positive and negative tests. Independently enumerate every
path in the Phase 5.42 and Phase 5.43 attempt bundles and the retained Phase
5.42 archive destination. Prove that the complete proposed successor path set
is internally unique and has an empty intersection with all historical paths.
Reject a candidate-mismatched namespace or any unscoped row.

Run the complete offline suite and a separate adversarial review. Correct every
actionable finding before commit. Do not bump the module version, freeze a
candidate, build release artifacts, use `wspr5`, stage target inputs, install
or remove DKMS state, operate a module or overlay, change services or boot
state, use GPIO, enable clocks, submit DMA, operate the separate I2C Si5351
path, use an SDR, connect an antenna, transmit, or produce RF. The next slice
may freeze a successor only after this prerequisite is committed and clean.
