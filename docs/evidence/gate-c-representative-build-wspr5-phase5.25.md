<!-- SPDX-License-Identifier: MIT -->

# Gate C representative build: wspr5 / 0.0.0-phase5.25

The authorized disposable build of frozen source commit
`d9f8fd8b17f1c2ee9324704c6b6630dfccfb5e4e` and archive SHA-256
`e615750897009b79d0ead1e3bbf4133e0c4d5c157cc259d513a76ad65bd993e4`
passed on `wspr5` against the installed stock
`6.18.34+rpt-rpi-2712` headers.

The module SHA-256 is
`556129fcd35cf0f64f8e5cd22dd2af932c83ecc1ff43fe3b940a81c667667398`.
Its reported version is `0.0.0-phase5.25` and its vermagic is
`6.18.34+rpt-rpi-2712 SMP preempt mod_unload modversions aarch64`. The busy
injector and UAPI probe compiled with their recorded hashes but were not
executed. All compiler diagnostic files are empty.

The immutable target evidence is
`/home/pi/gate-c-evidence/phase5.25-d9f8fd8b17f1`; its relative checksum
manifest SHA-256 is
`79168bfa7978b5e2e69097a5bbe5397627b193185ddb85c86ce56899f37f6857`.
Every checksum passed both on-target and after retrieval. The disposable archive
staging, build directory, and build driver were removed. The final runtime
check found no module, endpoint, overlay, or test DKMS registration.

This establishes only `Compatible-unqualified` build compatibility for the
exact candidate, host, stock kernel, installed headers, configuration,
`Module.symvers`, compiler, and architecture. It is route-neutral and does not
satisfy a Gate D lifecycle row. No DKMS registration, installation, signing,
loading, binding, overlay, service, boot, reboot, GPIO, clock, DMA,
transmission, Si5351, SDRplay, antenna, or RF activity occurred.
