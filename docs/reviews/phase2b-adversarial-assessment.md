<!-- SPDX-License-Identifier: MIT -->

# Phase 2B adversarial assessment

Date: 2026-08-14
Scope: portable state, validation, ownership, and lifecycle core only
Result: pass for the offline evidence examined after four correction cycles

## Method

The assessment separately attempted to falsify the Phase 2B execution prompt,
Decision 0003, the module contract's ownership and cancellation rules, V1
validation, finite work, first-writer terminal publication, stale-event
rejection, cleanup latching, and the inert hardware boundary. It included
source review, complete state comparisons on rejected operations, strict host
compilation, repeated deterministic execution, ASan/UBSan, Clang static
analysis, forbidden-interface scanning, and targeted generation-guard and
terminal-guard mutations.

## Reinjected findings and resolutions

1. Owner close after STOP entered `DRAINING` preserved the pending stop and
   could leave the closed owner attached. The prompt and decision now require
   close to win the pending nonterminal reason, bounded drain to finish as
   `OWNER_CLOSED`, and ownership to be relinquished. A regression test proves
   subsequent acquisition succeeds.
2. Removing the centralized terminal-publication guard initially survived the
   suite because public entry points duplicated the guard. A host-only direct
   publication probe now tests the central invariant. Both the generation and
   terminal guard mutations are killed.
3. Accepted work retained only a finite unit count rather than the bounded
   plan. The core now copies validated tones and events or symbols into fixed
   capacity storage, marks one owned plan, and records exactly one logical plan
   release on terminal cleanup, including cleanup-fault paths.
4. RELEASE could reset `DEAD / PROVIDER_REMOVED` to `IDLE`. It now relinquishes
   a matching owner while preserving the permanent dead state and reason;
   reacquisition remains rejected. The recovery transition stays deferred.

The review also expanded malformed-input, limit-boundary, and portable
failure-reason matrices so the tests match the implemented acceptance surface.

## Final assertions

- One nonzero owner holds one globally unique nonzero lease; generations are
  nonzero and strictly increasing within a lease. Zero, wrap, wrong-owner,
  wrong-lease, and stale-generation operations fail without state mutation.
- Both submission forms validate the frozen V1 fields and checked bounds before
  generation commit. Accepted work is copied into bounded internal storage.
- Normal work is finite. STOP and owner close prevent successors and allow at
  most one modeled residual unit. This is a policy proof, not a DMA claim.
- Exactly one terminal state/reason publication succeeds per accepted
  generation. Later or stale terminal candidates cannot alter the snapshot.
- Terminal cleanup logically releases the accepted plan once. Cleanup failure
  publishes `CLEANUP_FAILED`, latches the core, and blocks release/reacquisition
  from clearing the latch.
- The core remains route-neutral and accepts only GPIO4/GPIO20 identities. The
  module skeleton still registers nothing and contains no hardware/resource
  acquisition interface.

## Evidence and limitations

`make check` passes SPDX, UAPI identity, manifest structural checks, inert
source scanning, documentation links, ShellCheck, the host ABI test, 16
lifecycle test groups twice, ASan/UBSan execution, positive and negative UAPI
copy identity, and whitespace checks. Clang static analysis completed without
a diagnostic. Targeted generation and terminal guard mutations were both
killed by the suite.

The full JSON Schema validator is unavailable, so the existing native
structural manifest checks remain the evidence. No representative Linux kernel
headers are present or required for this portable slice, so no module build was
performed. No kernel concurrency, file/device lifetime, real DMA drain, clock
or pinctrl cleanup, target binding, GPIO behavior, timing, transmission, or RF
behavior is established.

No uncorrected objective Phase 2B finding remains in the evidence examined.
