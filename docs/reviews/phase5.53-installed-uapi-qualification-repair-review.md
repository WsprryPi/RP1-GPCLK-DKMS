<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 installed-UAPI qualification repair review

Status: PASS at the repaired offline artifact ceiling.

The failed target preflight exposed that the qualification installer and its
fake-system test assumed `/usr/include/linux/rp1_gpclk.h`, while the actual
product installation owns the canonical UAPI under
`/usr/src/rp1-gpclk-dkms-0.0.0-phase5.53/include/uapi/linux/rp1_gpclk.h`.
The installer now requires and compiles against that exact product-owned path.
Absence or a symlink fails closed.

The regression no longer injects a global header. A literal product archive was
reconstructed at its actual installed `/usr/src` closure, then the literal
qualification archive completed fake-system installation and removal while the
product sentinel remained unchanged. This exercises the path-bearing consumer
from the new artifact closures rather than patching historical controls.

Two clean generations retained product archive `032a0ca2...` byte-identically
and produced repaired qualification archive `71b53f8f...` byte-identically;
both passed independent successor validation. The prior `6dd18ef1...` archive
and its two-pass result are historical. The repaired pair requires a new exact
two-pass offline gate before target installation can be authorized again.

No target contact occurred during the repair, and no target mutation, module or
overlay action, reboot, GPIO, clock, DMA, transmission, or RF occurred.
