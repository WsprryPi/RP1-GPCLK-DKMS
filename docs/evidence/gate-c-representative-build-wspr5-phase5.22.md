<!-- SPDX-License-Identifier: MIT -->

# Gate C representative build: wspr5 / 0.0.0-phase5.22

The authorized disposable build of frozen source commit
`f7ddea06a68dedceb57aeec0ddedb67598a797e1` and archive SHA-256
`2601cadb4f2abe25b72c7ed3237c00307bbcc11a8ed671331fef677089f93be9`
passed on `wspr5` against the installed stock
`6.18.34+rpt-rpi-2712` headers.

The module SHA-256 is
`c4b9a04f3914a738fd3854354d42eb64f5b8c498ec7b7092a1cb68fe73c1c809`.
Its reported version is `0.0.0-phase5.22` and its vermagic is
`6.18.34+rpt-rpi-2712 SMP preempt mod_unload modversions aarch64`. The busy
injector and UAPI probe compiled with their expected hashes but were not
executed. All three compiler diagnostic files are empty.

The first evidence-sealing command stopped after the successful build because
non-interactive SSH did not place `/sbin/modinfo` on `PATH`. The build was not
repeated. Metadata inspection resumed with absolute `/sbin/modinfo`, and the
interruption and bounded resume are recorded in the sealed evidence.

The immutable target evidence is
`/home/pi/gate-c-evidence/phase5.22-f7ddea06a68d`; its relative checksum
manifest SHA-256 is
`abe852382d01a321df5f74b36979a00b29b6e8863e3f68457a3f22ae00d3197a`.
The retrieved evidence passed every relative checksum. The disposable build
directory was removed and the final read-only runtime check found neither the
module nor its device endpoint.

This establishes only `Compatible-unqualified` build compatibility for the
exact candidate, host, stock kernel, installed headers, configuration,
`Module.symvers`, compiler, and architecture. It is route-neutral and does not
satisfy a Gate D lifecycle row. No DKMS registration, installation, signing,
loading, binding, overlay, service, boot, reboot, GPIO, clock, DMA,
transmission, Si5351, SDR, antenna, or RF activity occurred.
