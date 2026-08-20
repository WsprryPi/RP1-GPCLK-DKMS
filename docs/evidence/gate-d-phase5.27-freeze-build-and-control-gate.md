<!-- SPDX-License-Identifier: MIT -->

# Phase 5.27 freeze, representative build, and control gate

The implementation commit `bfb92725631748db3f7f7def8d331442872cab7d`
passed the complete offline suite. Two isolated development builds were
byte-identical at archive SHA-256
`c623a8ebf6b5dc01a6e85a17e8709c479ad349aa2a08b34a86d71a2dc2a6adbb`.

On `wspr5`, that exact archive passed every sidecar checksum and built against
stock kernel `6.18.34+rpt-rpi-2712` with Debian GCC 14.2.0. The resulting module
SHA-256 is `0d0401ce932ca2b5020cce20e6cafbd8ee8d3133f8046ec12c8dc53a1e0541d6`;
its version and vermagic match. Nothing was installed or loaded, no endpoint or
overlay appeared, and no GPIO, clock, DMA, transmitter, or RF action occurred.

Adversarial review confirms the generic resolver remains symlink-free and the
new exception is confined to the final stock `build` link, strict `/usr/src`
containment, target-root ownership, and non-writable-directory checks. The
remaining gate is a newly generated, hash-closed Phase 5.27 Gate D control set.
Phase 5.26 controls embed the prior source/archive/module identities and must
not be relabeled or reused. Therefore authorized lifecycle mutation has not
started and must fail closed until the new control set is independently
validated.
