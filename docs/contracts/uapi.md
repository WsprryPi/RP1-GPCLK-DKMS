<!-- SPDX-License-Identifier: MIT -->

# RP1 GPCLK userspace interface

## Authority and scope

The canonical endpoint is `/dev/rp1-gpclk`. It is owned by root with mode
`0600`; possession of an open descriptor is the production execution
authority. The kernel does not interpret product modes, application policy,
operator acknowledgements, or authorization digests. Non-root access requires
a separately reviewed change to the endpoint ownership boundary.

The byte-authoritative interface is `include/uapi/linux/rp1_gpclk.h` and
`uapi-identity.json` records its exact SHA-256 digest. The current interface is
unreleased and has no legacy layouts, negotiation, or fallback behavior. The
module, consumers, diagnostics, tests, and identity digest change together.

The interface exposes a bounded sequence of generic clock events. It never
exposes physical addresses, DMA channels, register offsets, arbitrary register
writes, route mutation, or an unbounded program.

## Common validation

Every request supplies the exact structure `size`, zero header flags and
reserved fields, and zero structure-specific reserved fields. Unknown commands,
flags, enum values, routes, capabilities, malformed sizes, nonzero reserved
bytes, or unterminated identity strings fail closed. Output structures are
zero-initialized before fields are populated.

Counts, pointer ranges, and duration sums use checked arithmetic. User arrays
are copied once into bounded kernel-owned plan storage and user pointers are
never retained. One open file may own one nonzero lease. Generations are
nonzero, strictly increase within a lease, and are rejected when stale or held
by another file.

## Operations

| Command | Contract |
| --- | --- |
| `RP1_GPCLK_IOC_QUERY` | Reports route, compatibility, generic capabilities and limits, DMA chunk duration, and exact identities. It never selects a route. |
| `RP1_GPCLK_IOC_ACQUIRE` | Acquires one exclusive lease for the exact route and required generic capabilities. |
| `RP1_GPCLK_IOC_SUBMIT_EVENTS` | Submits a finite generic event sequence under one lease and generation. |
| `RP1_GPCLK_IOC_STOP` | Rejects every successor and begins generation-specific bounded drain and cleanup. |
| `RP1_GPCLK_IOC_GET_STATE` | Returns lease-scoped state without changing it. |
| `RP1_GPCLK_IOC_RELEASE` | Releases an idle lease, or stops, drains, and releases the named generation. |
| `RP1_GPCLK_IOC_GET_SNAPSHOT` | Returns one coherent passive, non-owning observation without exposing owner or lease tokens. |

An acquired lease has generation zero until its first successful submission.
`RELEASE` with generation zero releases only that never-submitted idle lease; it
cannot release a lease that has retained or active generation state. After a
submission, callers name the exact returned generation.

Capabilities describe implemented mechanics: event submission, stop/drain,
stable state, route and compatibility identity, cleanup-fault latching,
load-time output inhibition, passive snapshot, and bounded DMA chunks. They are
not product-mode permissions or qualification claims.

## Output inhibition

`output_inhibit` is an immutable load-time administrative switch. Its default
is `0`, the production model in which the root-only endpoint can execute valid
requests. `output_inhibit=1` is reserved for clock-disabled development and
lifecycle tests: query, acquire, snapshot, stop, release, bind, unbind, and
cleanup remain testable, while every submission is rejected before output
setup. The switch cannot be changed after load and cannot bypass route,
resource, ownership, duration, cancellation, or cleanup checks.

## Tone and event representation

Each tone contains adjacent unsigned Q16 divider values and two nonzero dither
counts. Their checked sum cannot exceed `RP1_GPCLK_DITHER_PERIOD_MAX`; the upper
divider equals the lower divider plus one. Provider and resource validation
further restrict divider acceptance.

`SUBMIT_EVENTS` accepts 1 through 64 tones and 1 through 512 events. Every
event has a nonzero duration. `RP1_GPCLK_EVENT_F_OUTPUT_ENABLED` is the only
event flag. Enabled events name a valid tone; disabled events ignore the tone
index and create a quiescent gap. The checked event-duration sum must equal
`total_duration_ns` and cannot exceed signed 64-bit nanoseconds. The interface
contains no WSPR, QRSS, FSKCW, DFCW, carrier, band, or scheduling semantics;
userspace translates those policies into generic finite events.

The logical request is not materialized as one duration-sized DMA program.
Execution advances through fixed coherent storage holding at most one
one-second DMA chunk. Divider-write remainders and per-tone dither accumulators
carry across chunk boundaries so chunking does not change aggregate timing or
dither distribution. Disabled gaps reset the duration-conversion remainder.
Consequently a 20-minute event remains one lease and generation while coherent
memory stays constant with respect to duration.

## Cancellation, state, and cleanup

The observable progression is `IDLE` to `RUNNING`, optionally `DRAINING`, then
`COMPLETE` or `FAILED`. `DEAD` means the provider was removed or is permanently
unavailable. Terminal states retain one stable terminal reason. A cleanup
failure latches `FAILED` with `CLEANUP_FAILED` and prevents further use.

`STOP` is generation-specific. It prevents a successor immediately, lets at
most the current fixed chunk drain, disables pacing and output, restores safe
pinctrl and clock state, verifies cleanup, and publishes terminal state.
Cancellation latency is therefore bounded by the one-second chunk plus bounded
cleanup and scheduling allowance, independent of the logical request duration.
Cancellation and the worker's final check-and-issue boundary are serialized. A
chunk committed before `STOP` obtains that boundary is the one permitted drain;
after `STOP` returns, no later chunk can be issued.
The post-event divider readback uses the same cancellation commit boundary and
explicitly starts its separately configured DMA descriptor. Cancellation that
commits first suppresses readback issue and proceeds directly to cleanup.
Release, owner close, unbind, provider removal, and module teardown converge on
the same no-successor and bounded-drain rules. A DMA deadline remains failure
even if cancellation was also requested.

## Passive snapshot

`GET_SNAPSHOT` does not acquire ownership, allocate a lease, advance a
generation, submit work, change output state, or clear retained terminal state.
It reports route and identities, compatibility, output inhibition, operational
resource readiness, owner/lease presence, operation and terminal state, timing,
drain state, cleanup fault, and resource quiescence.

Timing values are meaningful only with their corresponding snapshot-valid bit.
Observations use `UNKNOWN`, `FALSE`, and `TRUE`. `stable == TRUE` requires idle
or terminal state, completed worker and plan cleanup, no cleanup fault, and safe
GPIO plus quiescent clock and DMA observations. A snapshot describes one instant
and is not proof of future state.

`GPIO4` and `GPIO20` remain separate administrative routes. Querying or
acquiring one route never remuxes it, substitutes another route, or transfers
evidence between routes.
