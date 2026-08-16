<!-- SPDX-License-Identifier: MIT -->

# Gate C representative build: wspr5 / 0.0.0-phase5.26

The authorized disposable build of frozen source commit
`9f009240eecd55940d53d6f13cb9567aa76cd4ce` and archive SHA-256
`f43422342fc03c402eb0602949cc317aea239defc6544534ea98bc40d2c505bc`
passed on `wspr5` against installed stock `6.18.34+rpt-rpi-2712` headers.

The AArch64 module SHA-256 is
`6be0a2602db6442ad88b34879416fce25dc38dcaaa6b1634a2081ea5a80f600f`.
It reports version `0.0.0-phase5.26`, license `Dual MIT/GPL`, and vermagic
`6.18.34+rpt-rpi-2712 SMP preempt mod_unload modversions aarch64`. The busy
injector SHA-256 is
`c01d97301fcbad4266e6fd41c040f561da0c106affc28cf353455e4a071331dd`;
the UAPI probe SHA-256 is
`1ee335da403784a775efc049f49eb598e3541c625418b65015b322e29b0a1742`.
Both helpers compiled but were not executed. The diagnostics count is zero.

The exact representative inputs were Pi revision `c04170`, architecture
`aarch64`, header package `linux-headers-6.18.34+rpt-rpi-2712`
`1:6.18.34-1+rpt1`, compiler `cc (Debian 14.2.0-19) 14.2.0`, build-tree
`.config` SHA-256
`2a83d4324e9b47d418b4efac18d3af43d15cc956b71c5a8eb074060bf8383801`,
and `Module.symvers` SHA-256
`681e9fe5710e43c785b39c9e9f410a860cba6a6037e51af23a408cb5ccbe2426`.
The separately recorded boot-config SHA-256 is
`d5ba966d17d456a6f29e53baf53464e1fd53f9f8e31481da18f2221f1da2593d`.

The immutable target evidence is
`/home/pi/gate-c-evidence/phase5.26-9f009240eecd`; its relative checksum
manifest SHA-256 is
`1efeff299da529bf4b0801d6cd46ae967b20acfe3e2ae048a7c8883359b47216`.
Every checksum passed on-target and after retrieval. Evidence ran from
`2026-08-16T14:18:28Z` through `2026-08-16T14:18:32Z`. The disposable archive
staging, build tree, and driver were removed. Final checks found no loaded
module, endpoint, bound driver, overlay, or test DKMS registration.

This establishes only exact, route-neutral `Compatible-unqualified` build
compatibility with `liveEligible: false`; it does not satisfy a Gate D
lifecycle row. No DKMS registration, installation, signing, module load,
binding, overlay, service, boot, reboot, GPIO, clock, DMA, helper execution,
Si5351, SDRplay, antenna, transmission, or RF activity occurred.
