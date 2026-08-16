<!-- SPDX-License-Identifier: MIT -->

# Phase 5.37 representative build on wspr5

Clean freeze commit `71932324ec977d30ec0fadd48ef2673c49a6e173`
produced two independently validated, byte-identical non-publishable release
units using commit timestamp `1786909276`. Archive SHA-256 was
`299e8abe61f7c4ee81d9431539dcbae3614d33be2dafca0cb94a83996a4146ef`;
GPIO4 and GPIO20 DTBO hashes remained
`c3e17a685694928468bb18c24f5bb4e25454745d6989e6c9d2c2acf447b908d6`
and `8eaa8afae7f88a665fc9bec6da1b013be049b2a32c909c729caeff9181bcf3aa`.

The exact unit was checksummed and compiled directly and unprivileged below
`/home/pi/gate-c-evidence/phase5.37-7193232` against canonical stock headers
`/usr/src/linux-headers-6.18.34+rpt-rpi-2712`. The AArch64 relocatable module
SHA-256 was
`d34c6369ff56c3aa281f023fe5b2f044c409a2117c2120e115bc536703a52add`.
`modinfo` reported version `0.0.0-phase5.37`, `Dual MIT/GPL`, and vermagic
`6.18.34+rpt-rpi-2712 SMP preempt mod_unload modversions aarch64`.

UAPI, administrator, diagnostics, pre-root, outer-executor, UAPI-probe, and
busy-injector hashes were respectively
`1d411644352e61402bd4685a5692070d543ab2ee5b016d394294aa98970bd7fb`,
`b99900c3c43c2eeeebdf89ec0f498014dcdc68769b2013749d4486890cfb831b`,
`3db0bac2b18694f44e2c1dfbc2ab9fe28c621040213d7e98783a08a61ac93681`,
`4910e737830495b0fe6b8f41e3947b62968a2bcee32b0178288a37a3b525d7b8`,
`d81824ab0454ecb298714e07c08ff9d81255d216152631e5285e51e08ac1d43f`,
`1ee335da403784a775efc049f49eb598e3541c625418b65015b322e29b0a1742`,
and `c01d97301fcbad4266e6fd41c040f561da0c106affc28cf353455e4a071331dd`.
The helpers were compiled but not executed.

Headers were `root:root` mode `0755`; `.config` and `Module.symvers` hashes
were `2a83d4324e9b47d418b4efac18d3af43d15cc956b71c5a8eb074060bf8383801`
and `681e9fe5710e43c785b39c9e9f410a860cba6a6037e51af23a408cb5ccbe2426`.
The compiler was Debian GCC 14.2.0. The initial `dkms` lookup used the
non-interactive SSH `PATH` and could not locate the command; the preflight and
final checks therefore used canonical `/usr/sbin/dkms`. Evidence collection
similarly resumed with `/usr/sbin/modinfo` after compilation. Neither event
changed system state or invalidated the completed build.

No DKMS operation, installation, live-ledger mutation, retained-tool
replacement, module load/bind, overlay, GPIO, clock, DMA, Si5351, SDR,
transmitter, antenna, reboot, transmission, or RF action occurred. Initial and
final Phase 5.37 module, endpoint, DKMS, and overlay states were absent. This
supports only `Compatible-unqualified` build evidence.
