<!-- SPDX-License-Identifier: MIT -->

# Gate C representative build: wspr5 / 0.0.0-phase5.24

The authorized disposable build of frozen source commit
`2a6ddeb8e0f7d31a26bbe4ebdc4bc0458a41c8c5` and archive SHA-256
`0da181f1ccfa9fb9edbd34456cec95730be8922283d1c5b207af376491413d8a`
passed on `wspr5` against the installed stock
`6.18.34+rpt-rpi-2712` headers.

The module SHA-256 is
`0f3a2de824d689a7cde95d43ead1006b5e1ca40506fb33baadea3c605b0a826d`.
Its reported version is `0.0.0-phase5.24` and its vermagic is
`6.18.34+rpt-rpi-2712 SMP preempt mod_unload modversions aarch64`. The busy
injector and UAPI probe compiled with their expected hashes but were not
executed. All compiler diagnostic files are empty.

The immutable target evidence is
`/home/pi/gate-c-evidence/phase5.24-2a6ddeb8e0f7`; its relative checksum
manifest SHA-256 is
`92ab327e22d3d18042d9e4be255a7e56e62fbec6228abe3db0ade5001d02de53`.
The retrieved evidence passed every relative checksum. The disposable build
directory was removed and the final read-only runtime check found neither the
module nor its device endpoint.

This establishes only `Compatible-unqualified` build compatibility for the
exact candidate, host, stock kernel, installed headers, configuration,
`Module.symvers`, compiler, and architecture. It is route-neutral and does not
satisfy a Gate D lifecycle row. No DKMS registration, installation, signing,
loading, binding, overlay, service, boot, reboot, GPIO, clock, DMA,
transmission, Si5351, SDR, antenna, or RF activity occurred.
