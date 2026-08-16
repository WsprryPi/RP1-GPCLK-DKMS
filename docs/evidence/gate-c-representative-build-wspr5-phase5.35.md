<!-- SPDX-License-Identifier: MIT -->

# Phase 5.35 representative build on wspr5

Exact clean freeze commit `23efb65ea749dc09eb0cbadc18074be83f4035a9`
produced two independently validated, byte-identical non-publishable release
units. Archive SHA-256 was
`247f954541abb25bce9a1b60841122eaf02985b9fcea37df7d32e12fe9bf6e4c`;
GPIO4 and GPIO20 DTBO SHA-256 values remained
`c3e17a685694928468bb18c24f5bb4e25454745d6989e6c9d2c2acf447b908d6`
and `8eaa8afae7f88a665fc9bec6da1b013be049b2a32c909c729caeff9181bcf3aa`.

The exact unit was checksummed and extracted under
`/home/pi/gate-c-evidence/phase5.35-23efb65` on wspr5. It compiled directly and
unprivileged against canonical stock headers
`/usr/src/linux-headers-6.18.34+rpt-rpi-2712`. The resulting AArch64 relocatable
module SHA-256 was
`937357896407e941d561e4cda1cbcfdcd0d4d986fed8ec2ac6d0be460c6fa46c`.
`/usr/sbin/modinfo` reported version `0.0.0-phase5.35`, license
`Dual MIT/GPL`, and vermagic
`6.18.34+rpt-rpi-2712 SMP preempt mod_unload modversions aarch64`.

The target-built UAPI probe and busy injector were compiled but not executed;
their SHA-256 values were
`1ee335da403784a775efc049f49eb598e3541c625418b65015b322e29b0a1742`
and `c01d97301fcbad4266e6fd41c040f561da0c106affc28cf353455e4a071331dd`.
The UAPI, administrator, diagnostics, pre-root module, and outer executor hashes
were respectively
`1d411644352e61402bd4685a5692070d543ab2ee5b016d394294aa98970bd7fb`,
`391f02708ee26592c9010a3aeb1cf2374e85f081a2411c57f997a6e72c43f44a`,
`95ce06a47a38950bb0f4daf457918bb752eacd91c95becbd6e6a48cee2c7ab77`,
`da9e2683680c4ca3800394142534414bbd32a1a93e8526aae6fa93223cad7d97`,
and `d81824ab0454ecb298714e07c08ff9d81255d216152631e5285e51e08ac1d43f`.

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
