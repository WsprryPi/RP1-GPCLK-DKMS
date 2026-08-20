<!-- SPDX-License-Identifier: MIT -->

# Gate C representative build: wspr5 / 0.0.0-phase5.14

## Outcome

The authorized disposable build passed on `wspr5`. Frozen source commit
`7bbdfe1b5c83e1417e9dc5e0c4a7385136fd094a` and archive SHA-256
`d0c17f2842716052bb49b1a4fc079d3d48a5674bae8610eee2ab9d17ac548bea`
built without compiler or modpost warnings or errors against stock kernel and
headers `6.18.34+rpt-rpi-2712`.

The resulting 57,448-byte AArch64 module has SHA-256
`b41deafac7c5b49cafa9f13bbc4dba01585d5e013137c7e7015fb284a1990449`,
version `0.0.0-phase5.14`, license `Dual MIT/GPL`, and vermagic
`6.18.34+rpt-rpi-2712 SMP preempt mod_unload modversions aarch64`.

This proves only route-neutral `Compatible-unqualified` build compatibility,
with `liveEligible: false`. It does not establish a GPIO4 or GPIO20 route
decision and does not satisfy a Gate D lifecycle row.

## Inputs and evidence

- System: Raspberry Pi 5 Model B Rev 1.0, revision `c04170`, AArch64.
- Compiler: GCC 14.2.0, Debian `14.2.0-19`.
- Header packages: `linux-headers-6.18.34+rpt-rpi-2712` and
  `linux-headers-rpi-2712`, both `1:6.18.34-1+rpt1`.
- Kernel configuration SHA-256: `2a83d4324e9b47d418b4efac18d3af43d15cc956b71c5a8eb074060bf8383801`.
- `Module.symvers` SHA-256: `681e9fe5710e43c785b39c9e9f410a860cba6a6037e51af23a408cb5ccbe2426`.
- UAPI SHA-256: `1d411644352e61402bd4685a5692070d543ab2ee5b016d394294aa98970bd7fb`.
- Evidence interval: `2026-08-15T22:42:53Z` through `2026-08-15T22:42:58Z`.
- Target evidence: `/home/pi/gate-c-evidence/phase5.14-7bbdfe1b5c83`.
- Evidence-manifest SHA-256: `8cb7a946676bf31a79419b8bf7c7550bf3ebb9a49b618f3bc94868ea3842e56b`.

The retrieved review copy passed every checksum. The target evidence directory
and files are read-only. The exact disposable build directory was removed.

## Adversarial assessment

The initial attempt stopped before compilation because an unescaped dpkg format
token conflicted with `set -u`. Inspection proved the partial directory held
only pre-build identity files; that exact partial evidence directory was
removed and the corrected attempt used a fresh directory. The successful log
records all expected compile, link, and MODPOST stages and no warning or error.

No DKMS registration, package installation, signing, module installation,
loading, binding, overlay, service, boot, reboot, GPIO, clock, DMA, Si5351,
transmission, SDR, antenna, or RF activity occurred.
