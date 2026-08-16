<!-- SPDX-License-Identifier: MIT -->

# Phase 5.36 freeze and representative-build execution prompt

## Objective

Freeze `0.0.0-phase5.36` from recovered-ledger successor commit
`709d062bf0e1436518b8d3a5dcc4547cc5c3202d`. Preserve all Phase 5.35
controls, authorization, staging, failed execution, and review evidence as
immutable history.

## Local freeze and reproducibility

Advance only active candidate identities, packaging paths, release notes, and
deterministic fixtures. Include schema-version-3 authenticated terminal-ledger
archival and recovery while preserving schema-version-1/2 behavior, the
canonical UAPI, separate GPIO4/GPIO20 administrative routes, and the separate
I2C Si5351 output path.

Run the complete offline suite and independent adversarial review. Commit the
clean freeze, then generate two isolated non-publishable development release
units using the freeze timestamp. Validate both and require byte-for-byte
identity.

## Exact wspr5 representative build

Transfer one checksummed unit to a new Phase 5.36 evidence directory. Require
the inactive baseline, AArch64, the exact stock kernel and canonical headers,
safe header ownership/mode, `.config`, `Module.symvers`, and compiler identity.
Build the module and helper binaries directly and unprivileged. Record module,
UAPI, administrator, diagnostics, pre-root, executor, and helper identities and
the final inactive baseline.

## Safety boundary and exit

Do not administer DKMS, install files, move the live recovered ledger, replace
tools, load or bind a module, activate an overlay, alter services or boot state,
reboot, access GPIO, enable clocks, submit DMA, operate Si5351/SDR/transmitter
equipment, connect an antenna, transmit, or produce RF.

Exit only with a clean freeze, identical release units, passing exact build,
no adversarial finding, pushed commits, and a clean synchronized worktree. A
new Phase 5.36 control set remains the next separate gate.
