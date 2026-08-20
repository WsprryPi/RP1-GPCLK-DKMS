<!-- SPDX-License-Identifier: MIT -->

# Phase 5.34 representative build on wspr5

Exact clean freeze commit `3a3f970739934ead0f49629d0a9cda8113b33357`
produced two independently validated, byte-identical non-publishable release
units. Archive SHA-256 was
`a9895836700f284fc8e2e89c58a7b2cbd9257ea60543ebe1f59cddd2a2359ae6`;
GPIO4 and GPIO20 DTBO SHA-256 values remained
`c3e17a685694928468bb18c24f5bb4e25454745d6989e6c9d2c2acf447b908d6`
and `8eaa8afae7f88a665fc9bec6da1b013be049b2a32c909c729caeff9181bcf3aa`.

The exact unit was checksummed and extracted under
`/home/pi/gate-c-evidence/phase5.34-3a3f970` on wspr5. It compiled directly and
unprivileged against canonical stock headers
`/usr/src/linux-headers-6.18.34+rpt-rpi-2712`. The resulting AArch64 relocatable
module SHA-256 was
`2250172cd8430d05bb1aab147308128e69157df65bf0288532de210266cfc70d`.
`/usr/sbin/modinfo` reported version `0.0.0-phase5.34`, license
`Dual MIT/GPL`, and vermagic
`6.18.34+rpt-rpi-2712 SMP preempt mod_unload modversions aarch64`.

The target-built UAPI probe and busy injector were compiled but not executed;
their SHA-256 values were
`1ee335da403784a775efc049f49eb598e3541c625418b65015b322e29b0a1742`
and `c01d97301fcbad4266e6fd41c040f561da0c106affc28cf353455e4a071331dd`.
Headers were `root:root` mode `0755`; `.config` SHA-256 was
`2a83d4324e9b47d418b4efac18d3af43d15cc956b71c5a8eb074060bf8383801`
and `Module.symvers` SHA-256 was
`681e9fe5710e43c785b39c9e9f410a860cba6a6037e51af23a408cb5ccbe2426`.
The compiler was Debian GCC 14.2.0.

No DKMS operation, installation, module load or bind, overlay activation,
GPIO access, clock enablement, DMA, Si5351 operation, SDR or transmitter use,
antenna connection, reboot, transmission, or RF occurred. Initial and final
module, endpoint, and test-DKMS state were absent. This supports only
`Compatible-unqualified` build compatibility.
