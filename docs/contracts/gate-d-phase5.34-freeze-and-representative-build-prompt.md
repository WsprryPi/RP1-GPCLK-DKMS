<!-- SPDX-License-Identifier: MIT -->

# Phase 5.34 freeze and representative-build execution prompt

## Objective

Freeze `0.0.0-phase5.34` from the terminal pre-root recovery successor at
`e4e154f150eba9a90b14841283c1dffab4d8fc59`. Preserve all Phase 5.33 controls,
execution failures, journals, and recovery evidence as immutable history.

## Local freeze

Advance only active candidate identities, packaging paths, release notes, and
deterministic fixtures from Phase 5.33 to Phase 5.34. Preserve the canonical
UAPI and the separate I2C Si5351 boundary. The later qualification identity
must bind predecessor hashes from the last successfully installed Phase 5.31
retained-tool graph, never from failed Phase 5.32 or Phase 5.33 candidates.

Run the complete offline suite and installed CLI/import rehearsals. Perform an
independent version-boundary, recovery-control-flow, and historical-artifact
review. Correct every actionable finding and commit the exact freeze. Generate
artifacts only from that clean commit.

## Reproducible release units

Generate two isolated, non-publishable development release units using the
freeze commit timestamp. Validate both independently and require every output
byte to match. Record the archive, DTBO, UAPI, administrator, pre-root module,
outer executor, and helper identities.

## Exact wspr5 representative build

Transfer one checksummed unit to a new Phase 5.34 evidence directory. Reconfirm
the inactive baseline, AArch64 architecture, exact stock kernel, canonical
header path and permissions, `.config`, `Module.symvers`, and compiler. Build
the module and helper binaries directly and unprivileged. Record module version,
SHA-256, vermagic, ELF identity, helper hashes, and final inactive baseline.

## Safety boundary

Do not run DKMS add/build/install/remove, install files, replace retained tools,
load or bind a module, activate an overlay, alter services or boot state,
reboot, access GPIO, enable clocks, submit DMA, operate the Si5351, use an SDR
or transmitter, connect an antenna, transmit, or produce RF.

## Exit criteria

The freeze commit is clean, both release units are byte-identical, the exact
wspr5 representative build passes, adversarial review has no open finding, and
the evidence commit is pushed with a clean synchronized worktree. Gate D
control-set generation remains the next separately bounded step.
