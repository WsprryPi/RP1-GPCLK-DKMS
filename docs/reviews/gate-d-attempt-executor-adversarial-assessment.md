<!-- SPDX-License-Identifier: MIT -->

# Gate D attempt executor adversarial assessment

## Outcome

The offline slice now deterministically generates and validates 38 distinct
attempt documents and executes every document against a stateful fake system.
The documents bind candidate, predecessor, policy, route, plan, boot, and tool
identities; use unique evidence and journal paths; prescribe a closed operation
sequence; and reject unknown operations, unresolved variables, wildcards,
unsafe paths, service-state drift, total-deadline reset, and post-seal mutation.

This does **not** restore Gate D execution readiness. The command arrays invoke
`gate-d-outer step`, but the target-facing `step` command is not implemented.
Only generator, validator, and stateful fake-execution modes exist. Treating the
closed operation names as target-executable commands would repeat the semantic
plan error found by the pre-execution review.

No Raspberry Pi was contacted or changed. No installation, service, DKMS,
module, overlay, boot, reboot, GPIO, clock, DMA, transmitter, SDR, or RF action
occurred.

## Evidence established

- `release/gate-d-attempts-v1/index.json` binds exactly 38 unique checked-in
  documents and the generator/executor-oracle hash.
- Offline tests run all 38 attempt recipes against isolated fresh fake state
  and verify command order, output-disabled state, service restoration, final
  package state, evidence sealing, and unique evidence paths.
- Fifteen interruption attempts and four busy-state attempts are represented
  separately, and each row has a closed ordered recipe.
- The generator is byte-deterministic across independent output directories.

## Blocking findings

1. There is no privileged target dispatcher for the `step` subcommand named in
   every attempt document.
2. The fake backend models state transitions but does not yet prove real
   command construction, subprocess status capture, journal persistence,
   recovery after process death, or filesystem immutability.
3. Interruption checkpoints and stale/corrupt injectors are distinct by attempt
   identity, but their fake transitions are still generic rather than
   checkpoint-specific filesystem and DKMS state machines.
4. The checked-in schema is descriptive; the manual validator is authoritative
   and the execution-instance validator does not yet bind the attempt index.

All ten required-executable rows therefore remain `blocked-input-required`,
with `target-step-dispatcher-absent`. `--require-ready` must continue to fail.

## Next correction slice

Implement a fail-closed target `step` dispatcher whose operation handlers
compose the existing lifecycle and boot tools using literal argument arrays and
no shell; add persistent transaction journals and new-journal recovery; model
every interruption checkpoint and injector independently; validate the checked
attempt index from the execution instance; and adversarially test command
construction, partial failures, timeouts, evidence immutability, and recovery.
Only after those findings close may the ten rows become ready or any target
execution resume.

## Supersession update

Decision 0012 subsequently adopted a hybrid permanent-executor architecture.
Consequently `0.0.0-phase5.13` is historical and superseded before Gate D
execution. The attempt bundle described above remains development evidence for
the failed Phase 5.13 design; it is not the qualification bundle for a future
candidate.
