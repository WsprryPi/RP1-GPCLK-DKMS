<!-- SPDX-License-Identifier: MIT -->

# Phase 5.23 Gate D offline control-set construction prompt

## Objective

Construct and adversarially review the exact Phase 5.23 Gate D pre-root
bootstrap envelope, output-disabled route-compatibility decision, root-bound
target plan, deterministic 38-attempt bundle, and representative-system
execution instance. Perform the work entirely offline and stop before any
Raspberry Pi access or target mutation.

## Frozen inputs

- Candidate release: `0.0.0-phase5.23`.
- Source commit: `61ec2032542ac3aea2f51feac904d5450cc17655`.
- Source archive SHA-256:
  `04b6f7aee8f19c3f0da9b0d8f6a53f8f68dcaaae464b5cf99b847b587415aa8c`.
- Representative-build manifest:
  `release/gate-c-representative-build-manifest-phase5.23-v1.json`.
- Representative system and recovery facts remain the previously recorded
  `wspr5-stock` and `wspr5-rescue` identities. Treat every target fact as
  stale until immediate preflight revalidates it.
- Governing execution policy:
  `release/gate-d-matrix-policy-v2.json`.
- Predecessor: frozen `0.0.0-phase5.2` archive and identities already recorded
  by the prior Gate D plans.

## Required construction

1. Create a Phase 5.23 qualification-install identity and schema-3 bootstrap
   plan for the exact frozen candidate, predecessor, current stock kernel,
   installed administrator, complete retained Python import graph, helpers,
   cleanup operation, recovery operation, empty output-disabled baselines, and
   bounded journal.
2. Create a pre-root envelope that authenticates the frozen archive, staged
   executor, pre-root module, administrator, qualification identity, every
   root-bound control document, installed tool identity, proposed UID-bound
   mode-0700 root marker, transaction journal, cleanup paths, and exact
   install, cleanup, and recovery vectors. The transition must be one-shot and
   replay-resistant.
3. Create a route-specific compatibility decision for GPIO4 and GPIO20 using
   only the exact Phase 5.23 representative build and previously captured
   read-only system identities. Both routes remain
   `Compatible-unqualified`, output-disabled, and `liveEligible: false`.
4. Create a schema-5 root-bound target plan that binds the qualification root,
   bootstrap plan, complete installed Python import graph, permanent command
   entry points, target-built helper identities, predecessor/successor
   artifacts, recorded services and boot recovery identities, ten executable
   rows, all 38 attempts, and all output-disabled invariants.
5. Generate all 38 attempt documents deterministically from the exact plan and
   instance. Bind every document and both executor identities in a schema-2
   root-bound attempt index. Include all 15 interruption checkpoints and four
   busy-state attempts.
6. Create a schema-4 root-bound execution instance. Mark the ten
   `required-executable` rows ready and retain the five genuinely unavailable
   environmental rows as deferred. Set `inputsReady` truthfully. Do not claim
   target execution authorization: `targetExecutionApproved` and
   `executionReady` remain false until a fresh explicit Phase 5.23
   authorization is recorded.

## Safety and scope boundary

- Do not contact `wspr4`, `wspr5`, or `wspr5-rescue`.
- Do not install packages, register or build DKMS, install, sign, load, bind,
  unbind, unload, or remove modules, administer overlays, change services or
  boot configuration, reboot, access GPIO or clocks, submit DMA, transmit,
  use the Si5351 or SDRplay, connect an antenna, or perform RF activity.
- Do not change the frozen archive, source commit, module, UAPI, overlays,
  schemas, or permanent target executor.
- Do not tag, publish, open a pull request, or change a consuming repository.
- Generated qualification documents are test-owned control inputs, not release
  qualification or representative hardware evidence.

## Validation and adversarial review

- Validate every JSON document against its published schema where applicable.
- Recompute every referenced SHA-256 and reject missing, extra, reordered,
  swapped, stale, substituted, symlinked, traversal, or unhashed inputs.
- Reconstruct the 38-attempt bundle independently and require byte identity.
- Exercise every attempt with the stateful offline fake and require cleanup,
  service restoration, sealed evidence, and `liveOutput: false`.
- Verify the pre-root envelope binds every root transition file and complete
  installed tool graph, has no destination collisions, and cannot authorize
  normal dispatch before root creation or pre-root replay afterward.
- Verify all ten executable rows are ready, all five environmental rows remain
  deferred, `inputsReady` is true, and readiness fails only because fresh
  target authorization is absent.
- Run the complete offline suite twice. Perform a separate adversarial review,
  reinject each actionable finding, and repeat affected checks until no
  blocking finding remains.

## Exit criteria

The slice passes only when the complete control set is deterministic,
internally hash-closed, schema-valid, adversarially clean, and offline tests
pass twice. Commit and push only the attributable reviewed changes on the
current branch. Report exact files, checks, Git identities, non-activity
boundaries, unresolved environmental qualification, and the next gated step:
fresh explicit authorization for the exact sealed Phase 5.23 target execution.
