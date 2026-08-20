<!-- SPDX-License-Identifier: MIT -->

# Gate D hybrid permanent-executor adversarial assessment

## Outcome

The corrected hybrid implementation closes the offline software findings.
It composes the permanent outer executor with an exact 15-checkpoint
qualification transition and a separately identified recovery operation,
executes all 38 plans against a phase-granular filesystem fake, and integrates
the permanent tools into selected successor `0.0.0-phase5.14`.

This is an offline candidate-freeze input, not Gate D qualification. The new
successor has no representative Pi build or route decision, so Gate D readiness
remains false.

No Raspberry Pi was contacted or changed. No package, service, DKMS, module,
overlay, boot, reboot, GPIO, clock, DMA, transmitter, SDR, or RF action occurred.

## Assertions that passed

- The executor accepts a closed operation vocabulary and renders literal
  argument arrays without accepting a shell program from qualification data.
- A new attempt directory is required; journals are atomically written and
  fsynced; one wall/monotonic deadline spans reboot resumes.
- Success and failure evidence receive deterministic checksums and read-only
  modes. Recovery verifies the sealed source and writes a new journal under a
  new operation identity.
- Exact service-state transactions, compensation ordering, safe archive
  extraction, bounded output, stale single-identity changes, deterministic
  single-artifact corruption, and busy readiness have filesystem-backed fake
  coverage.
- Both planned stock-kernel reboots stop at durable `reboot-required` states
  and resume from the next exact step in offline execution.
- The attempt index binds both the generator and permanent executor and exactly
  38 action-resolved documents. The superseded instance binds that index but
  cannot become ready.

## Closed findings

1. Every interruption document now contains exact subordinate transition and
   recovery documents. The target dispatcher invokes `gate-d-lifecycle` with
   those files, distinct journals, the exact instance, and the selected one of
   15 checkpoints.
2. The Phase 5.14 release layout and installer own the permanent executor,
   attempt validator, boot/lifecycle/platform coordinators, busy injector, and
   their complete-removal ledger entries. Phase 5.13 remains superseded.
3. Target preflight now rejects a mismatched running kernel, malformed boot
   identity, signature enforcement, active Gate D route, foreign resource, or
   any changed/symlinked/missing installed permanent tool before mutation.
4. Dispatcher tests cover closed vocabulary, exact staging, already-absent
   removal, changed owned bytes, deadlines, rollback, and output-disabled
   platform behavior. Outer tests cover immutable failed journals, separate
   recovery identity, restoration compensation, and non-reusable evidence.
5. The filesystem fake records and asserts registered, built, installed,
   loaded, unloaded, uninstalled, and absent states across all 15 checkpoints.

## Remaining external gates

The selected successor still requires its exact offline source/archive/tool
identities to be frozen after a clean commit. Representative builds, route
confirmation, renewed target-plan inputs, and fresh authorization are later
gates and are not borrowed from Phase 5.13.

## Required next correction

Commit the reviewed Phase 5.14 source, build the development release twice from
that exact commit, and freeze the matching offline identities. Stop before any
Pi access or representative build.
