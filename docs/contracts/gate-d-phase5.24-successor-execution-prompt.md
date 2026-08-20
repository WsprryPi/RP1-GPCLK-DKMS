<!-- SPDX-License-Identifier: MIT -->

# Phase 5.24 target-plan schema correction and Gate D reconstruction prompt

## Objective

Create a distinct `0.0.0-phase5.24` successor that resolves the frozen Phase
5.23 target-plan schema contradiction, proves the exact real plan against both
the published JSON Schema and permanent validator, passes iterative offline
adversarial review, freezes reproducible offline identities, and reconstructs
the complete pre-root and root-bound Gate D control set. Stop before Raspberry
Pi access or representative build unless a separate exact authorization is
provided.

## Governing facts

- Preserve Phase 5.23 commit, archive, representative-build evidence, and
  historical status unchanged.
- Phase 5.23 is blocked before control-set freeze because its published schema
  declares `attemptEnvelope` as an object while its permanent validator and
  executor require an ordered list.
- The successor must remain stock-kernel, output-disabled, fail-closed, and
  route-neutral in implementation. GPIO4 and GPIO20 retain independent
  `liveEligible: false` planning decisions.
- No successful offline check can substitute for representative target
  evidence or fresh target-execution authorization.

## Implementation requirements

1. Change the published target-plan schema so `attemptEnvelope` accepts exactly
   the ordered, unique, nonempty string list consumed by the permanent
   validator. Preserve closed-object and conditional schema behavior.
2. Add a regression that validates an exact production-shaped schema-5 plan,
   not a reduced fixture, with both `check-jsonschema` or an equivalent local
   Draft 2020-12 validator and `gate_d_target_plan.validate()`.
3. Add adversarial cases for object/list substitution, missing operations,
   duplicate operations, reordered operations, extra properties, root
   substitution, stale hashes, and a schema-valid but permanent-validator-
   invalid plan.
4. Advance every release-owned version and installation identity to the
   distinct Phase 5.24 successor without rewriting historical evidence.
5. Update behavior, security, candidate-status, installation, packaging,
   release-layout, integration-gate, and operator documentation truthfully.
6. Run the complete offline suite twice and perform a separate adversarial
   assessment. Reinject every actionable finding and repeat affected checks.
7. Commit the reviewed implementation, build that exact clean commit twice,
   require byte-identical archives, and record all generated sidecar and
   permanent-tool identities. Commit and push the freeze separately if clean.
8. Do not claim or fabricate a representative build. If no exact Phase 5.24
   target-build authorization exists, stop with the candidate frozen offline.
9. After an authorized representative build exists, construct the Phase 5.24
   qualification identity, schema-3 bootstrap, one-shot pre-root envelope,
   GPIO4/GPIO20 route decision, schema-5 root-bound target plan, deterministic
   38-attempt bundle, and schema-4 execution instance. Until then, retain that
   construction as the next gated step rather than using Phase 5.23 evidence.

## Safety and non-goals

- Do not contact or mutate `wspr4`, `wspr5`, or `wspr5-rescue`.
- Do not install packages, register or build DKMS on a Pi, administer modules
  or overlays, change services or boot configuration, reboot, access GPIO or
  clocks, submit DMA, transmit, use Si5351 or SDRplay, connect an antenna, or
  perform RF activity.
- Do not tag, publish, create a pull request, or change a consuming repository.
- Do not modify Phase 5.23 frozen artifacts or promote its representative build
  to Phase 5.24.

## Exit criteria

The authorized offline slice passes only when the Phase 5.24 implementation is
adversarially clean, the full suite passes twice, the exact committed source
builds reproducibly twice, and frozen offline identities bind that commit.
Commit and push only reviewed attributable changes. Report the exact commits,
archive identity, checks, skipped target evidence, hardware non-activity,
remaining worktree state, and the next authorization required.
