<!-- SPDX-License-Identifier: MIT -->

# Phase 5.32 representative build on wspr5

Exact clean commit `4e62b3a0b584396a9528be07592d92e0796555f2`
produced two independently validated, byte-identical development release
units. The archive SHA-256 is
`068a3c78011427f643c4880e9bb18d59c1d4bfdb812f82c76137ab64d2365bbe`;
GPIO4 DTBO SHA-256 is
`c3e17a685694928468bb18c24f5bb4e25454745d6989e6c9d2c2acf447b908d6`,
and GPIO20 DTBO SHA-256 is
`8eaa8afae7f88a665fc9bec6da1b013be049b2a32c909c729caeff9181bcf3aa`.

The exact archive was verified and extracted below
`/home/pi/gate-c-evidence/phase5.32-4e62b3a` on `wspr5`, then compiled directly
against canonical stock headers
`/usr/src/linux-headers-6.18.34+rpt-rpi-2712`. The module SHA-256 is
`13fd2a026810cdb790f8b7ad04bb15fe93fed48dc1366b159ef3872ada84e715`.
`modinfo` reported version `0.0.0-phase5.32`, license `Dual MIT/GPL`, and
vermagic `6.18.34+rpt-rpi-2712 SMP preempt mod_unload modversions aarch64`;
`file` identified an AArch64 ELF relocatable module.

The header owner and mode were `root:root` and `0755`. Kernel configuration
SHA-256 was
`2a83d4324e9b47d418b4efac18d3af43d15cc956b71c5a8eb074060bf8383801`,
`Module.symvers` SHA-256 was
`681e9fe5710e43c785b39c9e9f410a860cba6a6037e51af23a408cb5ccbe2426`,
and the compiler was Debian GCC 14.2.0. The configuration hash differs from
the earlier Phase 5.31 record and is recorded as observed target identity;
the installed header package is `1:6.18.34-1+rpt1`.

No DKMS add, build, or install command was used. No module was loaded or bound,
no endpoint or overlay appeared, and no GPIO, clock, DMA, Si5351, transmitter,
SDR test, antenna, transmission, reboot, or RF operation occurred. Services
remained `active`, `active`, `inactive`, `active`. This evidence supports only
`Compatible-unqualified` build compatibility.
