<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 deterministic release-generation prompt

Generate the non-publishable `0.0.0-phase5.53` release twice from independent
detached worktrees at exact source freeze
`d7099814e2021a7b206dc68517be542aa94fb162`. Use the commit timestamp as the
archive epoch and the frozen build script and inputs only.

Require byte-identical seven-file inventories, archives, overlays, manifest,
metadata, provenance, and checksums. Validate each release unit and every
declared checksum. Inspect the archive for one versioned root, regular files
and directories only, no duplicate or unsafe paths, and no AppleDouble,
Finder, VCS, cache, backup, bytecode, key-like, link, device, FIFO, resource
fork, or extended-attribute content.

Extract one candidate to a fresh directory and run the archived permanent
executor regression and boot-operation construction regression using only its
archived scripts/tests. Record the complete deterministic inventory and exact
hashes as durable evidence.

This slice establishes deterministic release identity and archived offline
behavior only. Do not perform a representative target build, generate Gate D
controls, access or clean wspr5, recover or resume Phase 5.52, mutate boot
state, reboot, administer DKMS/overlays/modules, access GPIO/I2C, enable clocks,
submit DMA, operate Si5351/SDR, connect an antenna, transmit, or produce RF.
