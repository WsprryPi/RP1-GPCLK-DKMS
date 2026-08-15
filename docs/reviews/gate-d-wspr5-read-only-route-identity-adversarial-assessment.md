<!-- SPDX-License-Identifier: MIT -->

# Gate D wspr5 read-only route-identity adversarial assessment

## Scope

This review attempts to falsify the read-only system identity, route-specific
compatibility decision, conflict interpretation, readiness promotion, and
authorization boundary. It does not treat discovery as installation, binding,
clock-disabled lifecycle evidence, dynamic-owner exclusion, or qualification.

## Findings reinjected

1. The live flattened device-tree blob was not readable without added
   privilege. No privilege was requested. Evidence instead records the
   installed base DTB hash plus a deterministic digest over all 2,720 readable
   live property files; both limitations and identities remain explicit.
2. A historical unowned `rp1-gpclk-provider.dtbo` exists. It is absent from the
   active boot configuration and live tree, so it is preserved as unrelated
   residue rather than misclassified as an active conflict or removed.
3. Absence of static route, GPCLK0, and DMA TICK0 references cannot prove that
   no dynamic consumer will appear later. Both route decisions therefore
   require immediate fail-closed preflight, remain `liveEligible: false`, and
   create no installation or binding authority.
4. The decisions initially called themselves positive release-manifest
   entries. They are separately hashed Gate D execution sidecars and do not
   rewrite the sealed release manifest. The field and documentation now say
   `positiveExecutionCompatibilityDecisionEstablished` to avoid that overclaim.
5. Only rows whose remaining blocker was the current route or non-enforcing
   signing identity became ready. Prior-kernel downgrade, deliberate build
   failure with retained predecessor, and interrupted upgrade remain blocked
   pending exact predecessor evidence.
6. The signature-enforcing, signature-rejection, missing-header, newer-kernel,
   and genuine-conflict rows remain deferred. Current non-enforcement and an
   inactive historical overlay file cannot substitute for those environments.

## Final disposition

The read-only evidence supports `Compatible-unqualified` execution decisions
for GPIO4 and GPIO20 with live output disabled. Seven required-executable rows
are ready, three are blocked, and five environmental rows are deferred.
`inputsReady`, `executionReady`, and complete environmental coverage remain
false. No target mutation is authorized.

## Version/kernel build follow-up

The later authorized three-build matrix closed the three predecessor-dependent
input blockers without changing the route or environmental conclusions. Its
separate adversarial assessment is
[`gate-c-version-kernel-build-matrix-adversarial-assessment.md`](gate-c-version-kernel-build-matrix-adversarial-assessment.md).
All ten required-executable inputs are now ready; execution still lacks fresh
target authority.
