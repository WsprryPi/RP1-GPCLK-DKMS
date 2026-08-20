<!-- SPDX-License-Identifier: MIT -->

# Phase 5.54 lifecycle attempt-1 authorization prompt

Perform one GPIO4 output-disabled lifecycle attempt on `wspr5`, bound to
installed-state evidence commit `c5f278cccb2398875198e1d7d2e7727aee757a7f`,
control source commit `9151cb35ce982cc127029d4de679530fd275f2a3`,
product package SHA-256
`f61286a6e63c2735413a0e86d13c5dc2d91f4581e8a20aab7291234b1991f90b`,
and qualification-control bundle SHA-256
`f9e03ffa9b5b1b142dff67288ff8924f1d2a21eaf4623c2596a10919c70a74ef`.

Begin with a final read-only recapture of the exact configured `-2` package,
running `6.18.34+rpt-rpi-2712` kernel, four stock DKMS installations, installed
UAPI and both overlay identities, empty package audit, unloaded module, absent
endpoint, zero active or boot-selected overlays, inactive conflicting services,
and the physical-safety assertions. Stop on any mismatch.

Only after a match, transfer the bundle without metadata, rehash it, require
its exact three-member inventory, extract it into one new user-owned directory,
run its validator and renderer, and compile its probe against the installed
UAPI. Execute the rendered GPIO4 sequence exactly once: load
`rp1_gpclk_dkms live_output=0`; prove the output gate is disabled; apply only
the `rp1-gpclk-gpio4` runtime overlay while capturing its returned identifier;
settle udev; prove the endpoint and disabled gate; run the bounded
query/acquire/release probe; remove only that captured overlay; prove endpoint
absence; unload the module; and prove module absence.

On any post-load failure, close the probe, remove only the captured attempt
overlay if present, unload the attempt-loaded module if present, and verify the
original inactive package baseline. Preserve failure evidence and stop. On
success, remove only the user-owned staged bundle, extracted controls, and
compiled probe, then seal the evidence and stop before GPIO20 or any other
matrix row.

This authorization must explicitly permit the named output-disabled module
load/unload, GPIO4 runtime overlay apply/remove and safe inactive pinctrl
binding, and UAPI query/acquire/release. It does not permit `live_output=1`,
clock enable or rate change, DMA submission, GPIO output, boot changes, reboot,
transmission, RF, GPIO20, package removal, or another lifecycle attempt.
