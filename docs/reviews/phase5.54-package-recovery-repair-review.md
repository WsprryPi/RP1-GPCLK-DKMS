<!-- SPDX-License-Identifier: MIT -->

# Phase 5.54 package-recovery repair review

Result: **offline pass; target recovery remains unauthorized**.

The first adversarial upgrade deliberately denied `link(2)` and `linkat(2)`
beneath `/boot/firmware` and reproduced the target-class failure against a
package that directly owned the DTBO paths. The repaired package does not own
those boot paths. It owns canonical DTBOs under `/usr/lib`, and guarded
maintainer scripts copy or remove only recognized bytes. The same injected
failure then allowed the exact `-1` to `-2` upgrade and clean purge.

Real DKMS returned its standard exit 77 for `6.18.44-v8-16k+`; the captured
stock identity `6.18.34+rpt-rpi-2712` passed the scope selector and reached the
deliberately incomplete-header failure instead. A separate simulation proved
recovery from `install ok half-configured` at `-1` to configured `-2`.

Two builds from source commit `5587d438f1d75aa938e1f44444dec5e29ad32174`
were byte-identical. The final package SHA-256 is
`f61286a6e63c2735413a0e86d13c5dc2d91f4581e8a20aab7291234b1991f90b`.
The literal package inventory contains both canonical overlays and no
`/boot/firmware` member.

No target was contacted. No installation, module or overlay activity, boot
change, GPIO/clock/DMA activity, transmission, or RF occurred. The remaining
step is one separately authorized recovery of the already captured target
state, stopping before lifecycle attempt 1.
