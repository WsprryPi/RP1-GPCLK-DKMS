<!-- SPDX-License-Identifier: MIT -->

# Phase 5.35 freeze and representative-build execution prompt

## Objective

Freeze `0.0.0-phase5.35` from the mixed-transition integration successor at
`e62af8af7050a71d5cf1b75db1004543a7606b05`. Preserve every Phase 5.34
control, authorization, failed execution, journal, and recovery record as
immutable history.

## Local freeze

Advance only active candidate identities, packaging paths, release notes, and
deterministic fixtures from Phase 5.34 to Phase 5.35. Include the exact-path
qualification-tool transition fix and its complete-release success/recovery
regressions. Preserve the canonical UAPI, GPIO4/GPIO20 administrative-route
boundary, and the separate I2C Si5351 output path.

Run the complete offline suite and installed CLI/import rehearsals. Perform a
separate version-boundary, mixed-transition, recovery-control-flow, historical
artifact, and documentation review. Correct every actionable finding and
commit the exact freeze. Generate artifacts only from that clean commit.

## Reproducible release units

Generate two isolated, non-publishable development release units using the
freeze commit timestamp. Validate both independently and require every output
byte to match. Record the archive, DTBO, UAPI, administrator, pre-root module,
outer executor, diagnostics, and helper identities.

## Exact wspr5 representative build

Transfer one checksummed unit to a new Phase 5.35 evidence directory. Reconfirm
the inactive baseline, AArch64 architecture, exact stock kernel, canonical
header path and permissions, `.config`, `Module.symvers`, and compiler. Build
the module and helper binaries directly and unprivileged. Record module
version, SHA-256, vermagic, ELF identity, helper hashes, and final inactive
baseline.

## Safety boundary

Do not run DKMS add/build/install/remove, install files, replace retained tools,
load or bind a module, activate an overlay, alter services or boot state,
reboot, access GPIO, enable clocks, submit DMA, operate the Si5351, use an SDR
or transmitter, connect an antenna, transmit, or produce RF.

## Exit criteria

The freeze commit is clean, both release units are byte-identical, the exact
wspr5 representative build passes, adversarial review has no open finding, and
the evidence commit is pushed with a clean synchronized worktree. Phase 5.35
Gate D control-set generation remains the next separately bounded step.
