<!-- SPDX-License-Identifier: MIT -->

# Gate D single-Pi matrix-policy adversarial assessment

## Scope

This review attempts to falsify the offline single-Pi execution policy, the
route-specific compatibility decision, readiness semantics, candidate
immutability, environmental deferral, and authorization boundary. It performs
no target, package, DKMS, module, overlay, service, boot, GPIO, clock, DMA,
transmission, SDR, or RF activity.

## Findings reinjected

1. Directly editing the packaged base matrix would change frozen candidate
   source inputs and invalidate Gate C. The fifteen original assertions remain
   unchanged; the classification is a separately hashed execution-policy
   sidecar bound by the concrete instance. Both new policy sidecars are
   explicitly excluded from candidate archive inputs and are tested as such.
2. Treating unavailable environmental identities as simulated rows would make
   policy fixtures look representative. Five rows are instead explicitly
   `deferred-environmental`; they remain unpassed and still block complete
   environmental coverage and publication.
3. Gate C alone did not capture the exact current firmware, base device tree,
   provider, resource, and conflict identity. Both route decisions therefore
   remain `Unavailable`, route-specific, output-disabled, and unauthorized for
   installation or binding. No historical Phase 4 runtime identity was copied.
4. The first validator revision checked only the route-decision hash. A
   hand-edited instance could have marked an install/load row ready while that
   exact decision remained unavailable. Semantic validation now requires a
   positive `Compatible-unqualified`, non-live decision for every route used by
   a ready installation lifecycle row.
5. Execution readiness initially conflated complete inputs with authority to
   mutate the target. The instance now records `inputsReady` separately from
   `executionReady`; fresh `targetExecutionApproved` authority is mandatory
   even after every required-executable input becomes ready.
6. Filesystem or offline fixtures cannot change environmental coverage. The
   validator rejects relabeling a policy-classified environmental row as ready
   or ordinarily blocked and verifies both sidecar hashes.

## Final disposition

No unresolved finding remains within this offline policy slice. The instance
is valid but intentionally reports two ready rows, eight blocked
required-executable rows, five deferred environmental rows,
`inputsReady: false`, `executionReady: false`, and
`environmentalCoverageComplete: false`. The next permissible step is a
separately authorized read-only identity refresh and predecessor-input review;
target mutation remains prohibited.
