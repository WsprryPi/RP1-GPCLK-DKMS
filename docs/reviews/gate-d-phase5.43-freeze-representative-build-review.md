<!-- SPDX-License-Identifier: MIT -->

# Phase 5.43 freeze and representative-build review

Status: accepted for offline control construction; lifecycle execution remains
unauthorized.

The schema-5-capable candidate is frozen at
`aa92b0550acd66671fe1988510cf93987cd61c0a`. Two independently validated
non-publishable release units generated with its commit timestamp are
byte-identical. Archive SHA-256 is
`a8a200d069ad433353a8812ef6a9a4c585b75a9f6af3d6501ac3672e90c997c3`.

The exact archive built directly and unprivileged on `wspr5` against stock
`6.18.34+rpt-rpi-2712` headers. Module SHA-256 is
`d7cfefc1cba02a92485f4cbdc8b1aa1109467a9a258f4f32773c2bd3ec18c0ae`.
The archived schema-5 pre-root module is
`c9eec608c36ac6023373481e76b07b24d0ae39f8c4fa658412cef88f299b3ad3`.
Initial and final inactive baselines agree.

No installation, lifecycle, DKMS administration, module operation, overlay,
GPIO, clock, DMA, Si5351, SDR, transmitter, antenna, transmission, or RF
operation occurred. This is build compatibility evidence only.
