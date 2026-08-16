<!-- SPDX-License-Identifier: MIT -->

# Gate C representative build: wspr5 / 0.0.0-phase5.23

The authorized disposable build of frozen source commit
`61ec2032542ac3aea2f51feac904d5450cc17655` and archive SHA-256
`04b6f7aee8f19c3f0da9b0d8f6a53f8f68dcaaae464b5cf99b847b587415aa8c`
passed on `wspr5` against the installed stock
`6.18.34+rpt-rpi-2712` headers.

The module SHA-256 is
`44fba1121952e4874fcf5814cce721cc3a66d7e199ea1e0cce711c0887f489a3`.
Its reported version is `0.0.0-phase5.23` and its vermagic is
`6.18.34+rpt-rpi-2712 SMP preempt mod_unload modversions aarch64`. The busy
injector and UAPI probe compiled with their expected hashes but were not
executed. All three compiler diagnostic files are empty.

The immutable target evidence is
`/home/pi/gate-c-evidence/phase5.23-61ec2032542a`; its relative checksum
manifest SHA-256 is
`bed0238f9f46d0e2a64bd70250d47f7fbc407f326ab1d2c106ed6e56764dc5eb`.
The retrieved evidence passed every relative checksum. The disposable build
directory was removed and the final read-only runtime check found neither the
module nor its device endpoint.

This establishes only `Compatible-unqualified` build compatibility for the
exact candidate, host, stock kernel, installed headers, configuration,
`Module.symvers`, compiler, and architecture. It is route-neutral and does not
satisfy a Gate D lifecycle row. No DKMS registration, installation, signing,
loading, binding, overlay, service, boot, reboot, GPIO, clock, DMA,
transmission, Si5351, SDR, antenna, or RF activity occurred.
