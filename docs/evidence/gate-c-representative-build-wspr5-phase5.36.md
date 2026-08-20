<!-- SPDX-License-Identifier: MIT -->

# Phase 5.36 representative build on wspr5

Clean freeze commit `20f7a21ad8601f2e2fd4dec4640ea919acc22ce0`
produced two independently validated, byte-identical non-publishable release
units. Archive SHA-256 was
`a5d9fa6d83a4ea7405ede432be0bfcea201d850d21b3860fc40931f7e2fef271`;
GPIO4 and GPIO20 DTBO hashes remained
`c3e17a685694928468bb18c24f5bb4e25454745d6989e6c9d2c2acf447b908d6`
and `8eaa8afae7f88a665fc9bec6da1b013be049b2a32c909c729caeff9181bcf3aa`.

The exact unit was checksummed and built directly and unprivileged below
`/home/pi/gate-c-evidence/phase5.36-20f7a21` against canonical stock headers
`/usr/src/linux-headers-6.18.34+rpt-rpi-2712`. The resulting AArch64 relocatable
module SHA-256 was
`c11f89a63c4e2fbe09f6f0a401df348cbe5f4d713747f8c105a7731dc1007909`.
`modinfo` reported version `0.0.0-phase5.36`, `Dual MIT/GPL`, and vermagic
`6.18.34+rpt-rpi-2712 SMP preempt mod_unload modversions aarch64`.

UAPI, administrator, diagnostics, pre-root, outer-executor, UAPI-probe, and
busy-injector hashes were respectively
`1d411644352e61402bd4685a5692070d543ab2ee5b016d394294aa98970bd7fb`,
`450bb9bc502c4889a26aa342254409843230c63a869d3ee8095fc5a9310e8e4c`,
`573ee68e813a7a9cd530af2a3d0a6ee4de5c883e38f6d1a3e0b3b421ef3feab8`,
`4910e737830495b0fe6b8f41e3947b62968a2bcee32b0178288a37a3b525d7b8`,
`d81824ab0454ecb298714e07c08ff9d81255d216152631e5285e51e08ac1d43f`,
`1ee335da403784a775efc049f49eb598e3541c625418b65015b322e29b0a1742`,
and `c01d97301fcbad4266e6fd41c040f561da0c106affc28cf353455e4a071331dd`.
The helpers were compiled but not executed.

Headers were `root:root` mode `0755`; `.config` and `Module.symvers` hashes
remained `2a83d4324e9b47d418b4efac18d3af43d15cc956b71c5a8eb074060bf8383801`
and `681e9fe5710e43c785b39c9e9f410a860cba6a6037e51af23a408cb5ccbe2426`.
The compiler was Debian GCC 14.2.0.

No DKMS operation, installation, live-ledger move, module load/bind, overlay,
GPIO, clock, DMA, Si5351, SDR, transmitter, antenna, reboot, transmission, or
RF action occurred. Initial and final Phase 5.36 module, endpoint, and DKMS
states were absent. This supports only `Compatible-unqualified` build evidence.
