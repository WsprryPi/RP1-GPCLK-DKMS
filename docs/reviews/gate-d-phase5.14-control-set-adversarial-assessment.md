<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.14 control-set adversarial assessment

## Outcome

The offline Phase 5.14 control set is internally coherent and fail-closed. It
contains a route-compatibility decision, exact predecessor/successor pair,
target plan, deterministic 38-attempt bundle, and representative-system
execution instance. The instance intentionally fails `--require-ready` and
does not authorize installation or lifecycle execution.

No Raspberry Pi was contacted. No package, service, DKMS, module, overlay,
boot, reboot, GPIO, clock, DMA, Si5351, transmitter, SDR, antenna, or RF action
occurred in this slice.

## Assertions closed

1. The successor is exactly `0.0.0-phase5.14`, source commit
   `7bbdfe1b5c83e1417e9dc5e0c4a7385136fd094a`, and archive SHA-256
   `d0c17f2842716052bb49b1a4fc079d3d48a5674bae8610eee2ab9d17ac548bea`.
2. The route decision binds the new representative-build manifest, evidence
   manifest, module, kernel configuration, `Module.symvers`, UAPI, and unchanged
   GPIO4/GPIO20 overlay source and DTBO identities. It permits only
   output-disabled planning and requires a fresh read-only identity check.
3. The target plan contains ten required-executable rows and exactly 38
   attempts. It admits no live-output, arbitrary route, shell program, forced
   removal, unreviewed boot operation, or RF action.
4. All 38 documents regenerate byte-for-byte. The index binds every document,
   the attempt generator, and the permanent executor. Fifteen distinct
   interruption documents bind the exact 15-checkpoint transition and separate
   recovery operation.
5. The instance preserves five genuinely unavailable environmental rows as
   deferred qualification gates. Simulation does not satisfy them.
6. Phase 5.13 authorization is not inherited. `targetExecutionApproved` and
   `executionReady` are false, all ten executable rows retain a blocker, and
   `--require-ready` fails before dispatch.

## Remaining blockers

- The Phase 5.14 archive and DTBOs have not been staged at the target-plan
  paths.
- The permanent tools have not been installed. In particular, the checked
  hashes for the busy injector and UAPI probe are source identities, not hashes
  of the target-built installed binaries. Those installed hashes must be
  captured and the plan resealed before execution preflight can pass.
- Firmware, base device tree, resource ownership, active overlays, boot-file
  hashes, running kernel, signing policy, and named service states require a
  new read-only refresh immediately before any mutation request.
- The ten executable rows require a separately reviewed Phase 5.14 mutation
  envelope and fresh explicit target-execution authorization.

These are honest pre-execution inputs, not software-test failures. None can be
closed by an offline fixture or by reusing Phase 5.13 authorization.

## Claim ceiling

The control set is suitable for review and later target-input sealing only.
Phase 5.14 remains `Compatible-unqualified`, `liveEligible: false`, untagged,
unpublished, and ineligible for consuming-repository integration.
