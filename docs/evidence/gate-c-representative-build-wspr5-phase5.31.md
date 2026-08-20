<!-- SPDX-License-Identifier: MIT -->

# Phase 5.31 representative build on wspr5

The exact clean implementation commit
`c7e6fafdc434bdad78e12a6683239b8d87845cfa` produced two isolated,
byte-identical development release units. The source archive SHA-256 is
`ac0ce593e988886a24c22866409a20097a24105a94b846152bdc30ac4a060bed`.

Every staged release checksum passed. The archive was extracted below
`/home/pi/gate-c-evidence/phase5.31-c7e6faf` on `wspr5` and built against the
stock `6.18.34+rpt-rpi-2712` headers. The module SHA-256 is
`7e1e02a535c6b549327411c84e48580c31efb0e0b1662e7fd3b3bc58f31a44b9`.
`modinfo` reported version `0.0.0-phase5.31`, license `Dual MIT/GPL`, and
vermagic `6.18.34+rpt-rpi-2712 SMP preempt mod_unload modversions aarch64`;
`file` identified an AArch64 ELF relocatable module.

The canonical header path was
`/usr/src/linux-headers-6.18.34+rpt-rpi-2712`. Kernel configuration SHA-256 was
`d5ba966d17d456a6f29e53baf53464e1fd53f9f8e31481da18f2221f1da2593d`,
`Module.symvers` SHA-256 was
`681e9fe5710e43c785b39c9e9f410a860cba6a6037e51af23a408cb5ccbe2426`,
and the compiler was Debian GCC 14.2.0.

No DKMS add, build, or installation command was used. No module was loaded or
bound, no endpoint or overlay appeared, and no GPIO, clock, DMA, Si5351,
transmitter, SDR test, antenna, transmission, or RF operation occurred.
Services remained `wsprrypi=active`, `sdrplay=active`,
`sdrconnect-server=inactive`, and `SoapySDRServer=active`. This result supports
only `Compatible-unqualified` build compatibility.
