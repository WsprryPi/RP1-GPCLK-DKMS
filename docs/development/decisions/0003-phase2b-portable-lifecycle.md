<!-- SPDX-License-Identifier: MIT -->

# Decision 0003: Phase 2B portable lifecycle core

- Status: Accepted
- Date: 2026-08-14
- Scope: Offline portable policy only

## Decisions

The core accepts an explicit nonzero owner identity which a later kernel
adapter will bind to an open file. One owner holds one opaque nonzero lease.
Lease values increase globally and generations increase within a lease. Zero
and the maximum 64-bit value are rejected so allocation cannot wrap or alias a
stale identity. A submission's generation field is zero on input and receives
the allocated value only after the complete, already-copied request validates.

The centralized state machine supports `IDLE`, `RUNNING`, `DRAINING`,
`COMPLETE`, `FAILED`, and `DEAD`. An accepted request moves to `RUNNING`.
Normal progress completes with `COMPLETE`; STOP or active owner close latches a
no-successor drain with at most one residual portable work unit. Successful
drain publishes `STOPPED` or `OWNER_CLOSED`. Failures publish the most specific
frozen reason. Provider removal publishes `DEAD / PROVIDER_REMOVED` unless an
earlier terminal result already won.

If owner close arrives while STOP is draining, close replaces the pending
nonterminal reason with `OWNER_CLOSED` and guarantees ownership relinquishment
after the bounded drain. This prevents a closed owner from blocking later
acquisition. It does not replace a terminal result that was already published.

Terminal publication is first-writer-wins and centralized. The state/reason
pair is committed together and is immutable. Counters prove exactly one
successful publication per accepted generation. A terminal-precommit fault is
converted deterministically to `FAILED / INTERNAL_ERROR`; a cleanup fault wins
before publication as `FAILED / CLEANUP_FAILED` and latches the core. An
already-published terminal outcome always outranks a later completion, stop,
failure, close, removal, or callback.

`GET_STATE` is observational. STOP is idempotent for the same draining or
stopped generation only. RELEASE refuses running or draining work and cannot
clear a cleanup latch. Explicit release of idle or terminal work is the reset
point for retained terminal evidence. Active owner close performs bounded
drain and relinquishes ownership at terminal publication; a cleanup latch then
prevents reacquisition. A new lease resets its generation counter, while the
globally increasing lease ID keeps old `(lease, generation)` pairs stale.

`DEAD / PROVIDER_REMOVED` is the exception to ordinary terminal reset. RELEASE
may relinquish its matching owner, but preserves the dead state and reason;
acquisition remains unavailable. Only later reviewed provider reinitialization
may define a recovery transition.

## Portable boundary

Inputs are bounded arrays already copied by a future dispatcher. The core does
not dereference UAPI user addresses. After validation it copies the accepted
tones and events or symbols into fixed-capacity core-owned arrays. Terminal
cleanup releases that logical plan exactly once; no dynamic allocation is
used. The core does not allocate kernel resources, register an endpoint, or
implement synchronization. Host-only named fault injection is
compiled under `RP1_GPCLK_HOST_TEST`; it is absent from the module build.

The portable single-threaded tests establish deterministic policy behavior,
not kernel concurrency, callback synchronization, open-file lifetime, real DMA
drain, clock restoration, pinctrl cleanup, or hardware safety. Those remain
separate gated work.
