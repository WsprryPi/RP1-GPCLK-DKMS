<!-- SPDX-License-Identifier: MIT -->

# Phase 5.30 representative build on wspr5

The exact clean implementation commit
`73f3f7df4d7df194a52d14cacf127d29a316545f` produced two isolated,
byte-identical development release units. Both validations passed. The source
archive SHA-256 is
`ffc6b2e08ef8ed28550980c64bdc5c48e7d917c39e927f192e62c0451b408fd9`.

That archive was extracted beneath
`/home/pi/gate-c-evidence/phase5.30-73f3f7d` on `wspr5` and built against the
stock `6.18.34+rpt-rpi-2712` headers. The module SHA-256 is
`2203aeea52b17c0f6ce233f55ddff1069c93e05294238f517078029c87d9e0a0`;
`modinfo` reported version `0.0.0-phase5.30` and vermagic
`6.18.34+rpt-rpi-2712 SMP preempt mod_unload modversions aarch64`. Both Gate D
helpers compiled but were not executed.

The target retained `/lib -> usr/lib`, the stock header `build` alias resolving
to root-owned mode-0755
`/usr/src/linux-headers-6.18.34+rpt-rpi-2712`, configuration SHA-256
`2a83d4324e9b47d418b4efac18d3af43d15cc956b71c5a8eb074060bf8383801`,
and `Module.symvers` SHA-256
`681e9fe5710e43c785b39c9e9f410a860cba6a6037e51af23a408cb5ccbe2426`.

No DKMS installation, module load, binding, endpoint, overlay, GPIO, clock,
DMA, Si5351, transmitter, SDR operation, antenna, or RF activity occurred.
Services remained `wsprrypi=active`, `sdrplay=active`,
`sdrconnect-server=inactive`, and `SoapySDRServer=active`. This result supports
only `Compatible-unqualified` build compatibility.
