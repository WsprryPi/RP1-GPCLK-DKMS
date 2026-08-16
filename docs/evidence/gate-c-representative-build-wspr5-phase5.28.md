<!-- SPDX-License-Identifier: MIT -->

# Phase 5.28 representative build on wspr5

The exact twice-reproduced Phase 5.28 archive at source commit `9c408ec` and
SHA-256 `cd7e9d60f603101634d6f81e82edda311b724678c9ce9329ff98609911bcc3d6`
passed every sidecar checksum and compiled against the running stock
`6.18.34+rpt-rpi-2712` headers. The module SHA-256 is
`41ba511cc0821cf46fc856d40da53c90e578b8b7d8a734c35e0476984244d459`;
version and vermagic match.

The build documented `/lib -> usr/lib` and the final header-build alias into
root-owned mode-0755 `/usr/src`. Nothing was registered, installed, loaded,
bound, or activated. Services and boot state were unchanged; no GPIO, clock,
DMA, Si5351, SDR, transmitter, antenna, or RF action occurred. This proves
representative build compatibility only.
