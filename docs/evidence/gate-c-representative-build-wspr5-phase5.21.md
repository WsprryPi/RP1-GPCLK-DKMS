<!-- SPDX-License-Identifier: MIT -->

# Gate C representative build: wspr5 / 0.0.0-phase5.21

The explicitly authorized disposable build of frozen source commit
`d0046092dfa9ffa0c58171ddcb52b7819cc50fc6` and archive SHA-256
`fc5828d91446843d8ea78a09691c973d74082bea7655b6c0547a06d35fba1624`
passed on `wspr5` against the installed stock
`6.18.34+rpt-rpi-2712` headers.

The module SHA-256 is
`8f533495f1b4f9404d346237c2f41cb4c88f7552ee1a40472f4aa058fd028ade`.
Its reported version is `0.0.0-phase5.21` and its vermagic is
`6.18.34+rpt-rpi-2712 SMP preempt mod_unload modversions aarch64`. The busy
injector and UAPI probe compiled with their expected hashes but were not
executed. All three compiler diagnostic files are empty.

The immutable target evidence is
`/home/pi/gate-c-evidence/phase5.21-d0046092dfa9`; its relative checksum
manifest SHA-256 is
`1a9d86f973de58f3af47ee6877d1d5579786e2e8f46c74ed1931b17d9c939305`.
The retrieved evidence passed every relative checksum. The disposable build
directory was removed and the final read-only runtime check found neither the
module nor its device endpoint.

This establishes only `Compatible-unqualified` build compatibility for the
exact candidate, host, stock kernel, installed headers, configuration,
`Module.symvers`, compiler, and architecture. It is route-neutral and does not
satisfy a Gate D lifecycle row. No DKMS registration, installation, signing,
loading, binding, overlay, service, boot, reboot, GPIO, clock, DMA,
transmission, Si5351, SDR, antenna, or RF activity occurred.
