<!-- SPDX-License-Identifier: MIT -->

# Phase 5.38 typed control-inventory integration adversarial assessment

Status: accepted offline; a new freeze and representative build are required

Bootstrap-plan schema 4 and pre-root-envelope schema 4 now carry the complete
typed package inventory in addition to the historical regular-tool import
subset. Each regular file binds canonical path, SHA-256, mode, owner UID, and
group GID. Each symlink binds canonical path, exact relative target, observed
mode, owner UID, and group GID. Historical schema versions 1 through 3 remain
accepted for immutable earlier evidence and do not acquire new semantics.

Both documents bind the canonical serialization of their inventory with
`packagePathsSha256`. A Phase 5.38 control-set validator must require equal
digests as well as equal records, preventing two independently valid but
different inventories from being composed. The retained Python import-tool
subset must be contained in the typed package-path set.

Validation rejects empty or duplicate inventories, unsafe or non-absolute
paths, unsupported types, malformed hashes, absolute symlink targets,
wrong-type fields, invalid modes, and invalid ownership values. Runtime
verification uses `lstat`, does not follow a symlink leaf, and rejects type,
hash, target, mode, owner, or group differences. Mixed regular-file and
symlink temporary-root tests cover accepted state and adversarial mutations.

The first adversarial pass found that separate typed lists were not mutually
bound. Adding the canonical inventory digest corrected that finding. Focused
bootstrap, pre-root, schema, and historical tests passed, followed by the
complete offline suite. Linux-only UAPI client compilations remained expected
macOS skips.

No target staging, ledger or package mutation, DKMS administration, module or
overlay operation, service or boot change, GPIO, clock, DMA, separate I2C
Si5351, SDR, transmitter, antenna, reboot, transmission, or RF activity was
performed. Because the frozen Phase 5.38 archive predates these validator and
schema bytes, the next gate is a new Phase 5.38 successor freeze and exact
representative build before control-set generation.
