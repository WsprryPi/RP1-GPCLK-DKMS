<!-- SPDX-License-Identifier: MIT -->

# Phase 5.54 GPIO20 lifecycle attempt-2 authorization prompt

Perform one GPIO20 output-disabled lifecycle attempt on `wspr5`, bound to
installed-state evidence commit `c5f278cccb2398875198e1d7d2e7727aee757a7f`,
successful GPIO4 evidence commit
`4018b0ef2334fac759be49a5af1f6d3bd67676d6`, control source commit
`b231f912d42ab5ac59c2f7ac2552643ff3ac8230`, product package SHA-256
`f61286a6e63c2735413a0e86d13c5dc2d91f4581e8a20aab7291234b1991f90b`,
and GPIO20 control-bundle SHA-256
`69f4b9c360b781dbbaaaaa1e886ce5709d1377ccbb44d7f962de4fdde945d5d9`.

Begin with a final read-only recapture of the configured `-2` package, running
stock kernel, four DKMS installations, exact installed UAPI, exact GPIO20
canonical and inactive boot overlay, clean package audit, unloaded module,
absent endpoint, zero active or boot-selected overlays, inactive conflicting
services, and freshly confirmed physical safety for GPIO20. Stop on mismatch.

Only after a match, transfer the bundle without metadata, verify its digest and
exact three regular-file members, extract into one new user-owned directory,
run its validator and renderer, and compile the probe against the installed
UAPI. Execute the rendered sequence exactly once: load with `live_output=0`;
verify `N`; apply only `rp1-gpclk-gpio20`; derive its identifier from the
before/after active-overlay list; settle udev; verify endpoint and disabled
gate; run the GPIO20 query/acquire/release probe; remove only the captured
overlay; verify endpoint absence; unload; and verify module absence.

On failure after load, remove only the attempt GPIO20 overlay if present,
unload only the attempt-loaded module if present, verify the original inactive
baseline, preserve evidence, and stop. On success, remove only the user-owned
staged bundle and extracted controls, seal evidence read-only, and stop before
package removal/reinstallation or any other matrix row.

Authorization must explicitly permit this named output-disabled module
load/unload, GPIO20 runtime-overlay apply/remove and safe inactive pinctrl
binding, and UAPI query/acquire/release. It does not permit `live_output=1`,
clock enable or rate change, DMA submission, GPIO output, boot changes, reboot,
transmission, RF, GPIO4 activity, package removal, or another lifecycle attempt.
