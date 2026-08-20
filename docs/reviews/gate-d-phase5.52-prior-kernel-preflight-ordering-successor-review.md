<!-- SPDX-License-Identifier: MIT -->

# Phase 5.52 prior-kernel preflight ordering successor review

Status: PASS for the bounded offline successor implementation. The permanent
executor now distinguishes the initial normal-kernel preflight from the
post-reboot prior-kernel verification without weakening either identity.

The defect was an ordering contradiction in the frozen Phase 5.51 downgrade
attempts: top-level `kernelRelease` identifies the prior kernel used for DKMS
and route work, but `capture-preflight` runs before the sealed boot selector.
Requiring top-level `kernelRelease` at that first step made the authenticated
normal-kernel starting state unreachable.

`initial_preflight_kernel()` now returns top-level `kernelRelease` for every
ordinary row. Only `prior-supported-kernel-downgrade` requires the explicit
`inputs.boot.normalKernel` initially, while also requiring the sealed
`inputs.boot.priorKernel` to equal top-level `kernelRelease` and requiring the
normal and prior identities to differ. Missing, malformed, or inconsistent
identities fail closed. The selected initial identity is used for both the
running-kernel comparison and module-signing configuration lookup.

The existing post-reboot `verify-prior-kernel` and `verify-normal-kernel`
operations are unchanged. No command recipe, reboot behavior, recovery rule,
route, UAPI, DKMS action, output policy, or evidence-sealing behavior changed.

Regression coverage binds the exact failed Phase 5.51 attempt, preserves the
ordinary-row behavior, accepts only the normal kernel at initial downgrade
preflight, rejects the prior kernel at that point, and rejects absent or
inconsistent boot identities.

Adversarial assessment found and corrected one robustness gap during the
slice: a non-object `inputs` value initially raised an incidental attribute
error. It now receives an explicit fail-closed `ValueError`. No actionable
finding remains in the bounded implementation.

No target was accessed. No DKMS, module, overlay, service, boot, reboot, GPIO,
clock, DMA, Si5351, SDR, antenna, transmission, or RF operation occurred. This
commit is not a Phase 5.52 source freeze or target control set. Representative
build evidence, complete identity regeneration, fresh authorization, staging,
and target execution remain separate gates.
