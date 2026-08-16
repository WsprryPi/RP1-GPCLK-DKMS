<!-- SPDX-License-Identifier: MIT -->

# Phase 5.33 freeze and representative-build execution prompt

## Objective

Freeze successor `0.0.0-phase5.33` from the exact Phase 5.33 retained-tool
transition and pre-root recovery repair. Preserve every Phase 5.32 candidate,
control-set, authorization, execution, failure, and recovery artifact as
historical evidence.

## Local freeze

Update only active candidate version identities, packaging paths, release
notes, lifecycle data, and deterministic tests required for the distinct
successor. Do not rewrite historical Phase 5.32 controls or evidence. The
release unit must carry the versioned qualification identity support needed to
bind the complete Phase 5.31 predecessor permanent-tool graph and the exact
Phase 5.33 successor hashes, including target-built helper binaries.

Run the complete offline suite and the installed CLI/import rehearsals. Perform
a separate adversarial version-boundary and transition-graph review, correct
every actionable finding, and commit the freeze. Start artifact generation only
from that exact clean commit.

## Reproducible release units

Produce two isolated non-publishable development release units, validate each
independently, and require every generated artifact to be byte-identical.
Record the source commit, archive and DTBO hashes, canonical UAPI identity,
administrator and transition-tool source identities, and validation results.

## Exact wspr5 representative build

Transfer only the checksummed release unit required for an unprivileged,
build-only check on `wspr5`. Reconfirm the stock kernel, architecture,
canonical header path, header ownership and mode, kernel configuration,
`Module.symvers`, compiler, and inactive baseline. Extract the exact archive
into a new Phase 5.33 evidence directory and compile the module directly
against the canonical headers. Record module version, SHA-256, vermagic, ELF
identity, and final inactive baseline.

## Authority boundary

Do not run DKMS add, build, install, or remove. Do not install files, replace
permanent tools, load or bind a module, activate an overlay, change services or
boot state, reboot, access GPIO, enable clocks, submit DMA, operate the separate
I2C Si5351 path, use a transmitter or SDR, connect an antenna, transmit, or
produce RF.

Stop after representative-build evidence and its adversarial assessment. Gate
D control-set generation, target installation, lifecycle execution, tagging,
publication, pull requests, and dependent-repository changes remain later
gates requiring separate authority.
