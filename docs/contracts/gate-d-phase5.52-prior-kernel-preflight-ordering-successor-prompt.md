<!-- SPDX-License-Identifier: MIT -->

# Phase 5.52 prior-kernel preflight ordering successor prompt

Implement only the offline successor required by the sealed Phase 5.51
attempt-3 failure at commit
`b91e1b239fd48c1f5270c4be03873abf3ef1d5f6`. Bind the work to operation
`gd-prior-supported-kernel-downgrade-gpio4`, attempt-document SHA-256
`e4002b4b21f2fdbacfbdc4d7180b0b037bae6344e17ef3148edd5680af0f4fe7`,
sealed failed-journal SHA-256
`ca04e0da5cba4e02f49812064ef5ecc6224b657ad35fcc3897446cc564c6566e`,
and sealed failure-manifest SHA-256
`58366390b1c5bfdf425108857bd17685f1ad37b63168d0438dfd6db002973a66`.

Correct the permanent executor's initial preflight kernel selection. For the
`prior-supported-kernel-downgrade` matrix row only, `capture-preflight` must
require the sealed `inputs.boot.normalKernel`, because boot selection and the
first reboot occur later in the attempt. The existing
`verify-prior-kernel` step remains responsible for requiring
`inputs.boot.priorKernel` after that reboot. Every other matrix row must
continue to require its declared top-level `kernelRelease`.

Keep the rule explicit, closed, and fail-closed. Reject a missing, malformed,
or inconsistent normal-kernel identity rather than falling back to the running
kernel or guessing from the host. Use the selected preflight kernel for both
the running-kernel comparison and module-signing-policy evidence so those
checks cannot disagree.

Add deterministic regression coverage that proves:

1. a current-kernel row still selects its top-level `kernelRelease`;
2. the exact failed Phase 5.51 attempt selects its sealed normal kernel for
   initial preflight;
3. rooted target preflight accepts that normal kernel before the prior-kernel
   selection steps;
4. the same preflight rejects the prior kernel as an initial state; and
5. malformed or absent boot identities fail closed.

Update durable review documentation with the defect, correction, evidence,
and remaining gates. Perform a separate adversarial assessment and correct
every actionable finding before handoff. Run focused checks and the complete
offline suite with the exact Phase 5.51 archive supplied.

This slice does not regenerate or authorize a Phase 5.52 target control set.
Do not modify the frozen Phase 5.51 attempts or sealed target evidence. Do not
access a target, install or load DKMS, bind or unbind, apply an overlay, alter
services or boot state, reboot, access GPIO, enable clocks, submit DMA, operate
Si5351 or SDR equipment, connect an antenna, transmit, or produce RF. A new
source freeze, representative build, canonical recapture, regenerated control
set, authorization decision, staging transition, and target attempt are later
independent gates.
