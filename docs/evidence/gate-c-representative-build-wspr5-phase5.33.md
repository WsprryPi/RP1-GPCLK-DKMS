<!-- SPDX-License-Identifier: MIT -->

# Phase 5.33 representative build on wspr5

Exact clean commit `4208941af537f21e3a20160d2d3d7fabe50f7cd3`
produced two independently validated, byte-identical development release
units. The archive SHA-256 is
`e5f5a047b17c08e5b33aaedfd88385b560324649c236c3518df4a660371a6867`;
GPIO4 DTBO SHA-256 is
`c3e17a685694928468bb18c24f5bb4e25454745d6989e6c9d2c2acf447b908d6`,
and GPIO20 DTBO SHA-256 is
`8eaa8afae7f88a665fc9bec6da1b013be049b2a32c909c729caeff9181bcf3aa`.

The exact release unit was checksummed and extracted below
`/home/pi/gate-c-evidence/phase5.33-4208941` on `wspr5`, then compiled directly
against canonical stock headers
`/usr/src/linux-headers-6.18.34+rpt-rpi-2712`. The module SHA-256 is
`e58b4b74b661eb2cfb50c4f960e9519dcfc9092769cf0c1947c9974906c24428`.
`modinfo` reported version `0.0.0-phase5.33`, license `Dual MIT/GPL`, and
vermagic `6.18.34+rpt-rpi-2712 SMP preempt mod_unload modversions aarch64`;
`file` identified an AArch64 relocatable ELF module.

The target-built UAPI probe and busy injector were compiled but not executed.
Their SHA-256 identities are
`1ee335da403784a775efc049f49eb598e3541c625418b65015b322e29b0a1742`
and `c01d97301fcbad4266e6fd41c040f561da0c106affc28cf353455e4a071331dd`.
These exact identities can be used by the later Phase 5.33 transition graph.

The header owner and mode were `root:root` and `0755`. Kernel configuration
SHA-256 was
`2a83d4324e9b47d418b4efac18d3af43d15cc956b71c5a8eb074060bf8383801`,
`Module.symvers` SHA-256 was
`681e9fe5710e43c785b39c9e9f410a860cba6a6037e51af23a408cb5ccbe2426`,
and the compiler was Debian GCC 14.2.0.

No DKMS command was used. No file was installed, no module was loaded or bound,
no endpoint or overlay appeared, and no GPIO, clock, DMA, Si5351, transmitter,
SDR test, antenna, transmission, reboot, or RF operation occurred. Final
service states were `active`, `inactive`, `inactive`, `active`; the Phase 5.33
install paths remained absent. This evidence supports only
`Compatible-unqualified` build compatibility.
