<!-- SPDX-License-Identifier: MIT -->

# RP1 GPCLK userspace interface

## Authority and identity

The canonical endpoint is `/dev/rp1-gpclk`. The byte-authoritative interface
is `include/uapi/linux/rp1_gpclk.h`; `uapi-identity.json` records its exact
SHA-256 digest. This repository has no released transmission interface and
therefore carries no legacy layouts, compatibility commands, version
negotiation, or fallback behavior. The module, consumers, diagnostics, tests,
and exact-header digest must change together whenever this interface changes.

The interface exposes bounded GPCLK operations only. It never exposes physical
addresses, DMA channels, register offsets, arbitrary divider programs, or
route-changing operations.

## Common validation

Every request supplies the exact structure `size`, a zero header `reserved`
field, zero header `flags`, and zero structure-specific reserved fields.
Unknown commands, flags, enum values, routes, modes, capability bits, nonzero
reserved bytes, malformed sizes, or non-NUL-terminated identity strings fail
closed. Output structures are zero-initialized before fields are filled.

Counts and duration sums use checked arithmetic before allocation or copy.
User pointers are copied once into bounded kernel-owned storage and are never
retained. A nonzero `lease_id` belongs to one open file. Generations are
nonzero, strictly increase within that lease, and are rejected when stale or
associated with another lease.

## Operations

| Command | Contract |
| --- | --- |
| `RP1_GPCLK_IOC_QUERY` | Reports the active route, compatibility state and reason, capability limits, duration limits, and exact module/build/compatibility identities. It never selects a route. |
| `RP1_GPCLK_IOC_ACQUIRE` | Acquires one exclusive lease for the exact route and required capabilities. Optional operation-scoped live authorization requires `RP1_GPCLK_ACQUIRE_F_AUTHORIZE_LIVE`, `RP1_GPCLK_CAP_LIVE_ELIGIBLE`, `RP1_GPCLK_CAP_OPERATION_LIVE_GATE`, and a nonzero 32-byte authorization digest. |
| `RP1_GPCLK_IOC_SUBMIT_WSPR` | Submits exactly four tones and 162 `WSPR` symbol indexes with bounded pacing and duration. |
| `RP1_GPCLK_IOC_SUBMIT_EVENTS` | Submits bounded `QRSS`, `FSKCW`, or `DFCW` events. |
| `RP1_GPCLK_IOC_SUBMIT_TONE` | Submits one continuous or finite tone. |
| `RP1_GPCLK_IOC_STOP` | Prevents a successor and starts generation-specific bounded drain and cleanup. |
| `RP1_GPCLK_IOC_GET_STATE` | Returns lease-scoped state without changing it. |
| `RP1_GPCLK_IOC_RELEASE` | Releases an idle lease when `generation` is zero, or stops, drains, and releases the named generation. |
| `RP1_GPCLK_IOC_GET_SNAPSHOT` | Returns one coherent passive, non-owning observation without disclosing owner or lease tokens. |

`QUERY.capabilities` describes implemented operations. The
`RP1_GPCLK_CAP_LIVE_ELIGIBLE` bit appears only when the recognized route
identity and current runtime checks permit a live attempt. Capability presence
does not itself authorize installation, loading, GPIO output, transmission, or
RF activity.

## Acquisition and live authorization

Clock-disabled ownership uses zero `authorization_flags`, a zero authorization
digest, and no live-gate capability requirement. It can inspect and serialize
the endpoint but cannot authorize output.

Operation-scoped live acquisition requires the exact active route, current
`Experimental` eligibility, both live-gate capabilities, the single authorize
flag, and a nonzero digest. The digest binds an application-reviewed request
and plan identity; the kernel does not interpret its contents or treat nonzero
bytes as operator authority. Endpoint permissions, application policy,
compatibility enrollment, physical topology, and operator authorization remain
separate requirements.

A successful authorized acquire binds output authorization to its owner and
lease. Submission verifies that binding. Release, owner close, copyout failure,
provider removal, and teardown revoke it. A later lease requires a fresh
authorization. The immutable module-load output gate is a separate current
development path and never bypasses route, resource, ownership, or cleanup
checks.

## Tone and event representation

Each tone contains adjacent unsigned Q16 divider values and two nonzero dither
counts. Their checked sum cannot exceed
`RP1_GPCLK_DITHER_PERIOD_MAX`; the upper divider equals the lower divider plus
one. Provider and resource validation further restrict divider acceptance.

`SUBMIT_WSPR` requires four tones, 162 one-byte symbols, 16 fractional bits,
tick divider 511, and a nonzero `writes_per_symbol` no greater than 66,792.
Every symbol is below `tone_count`; every tone count sum equals
`writes_per_symbol`; and the expected duration is within the request limit.

`SUBMIT_EVENTS` accepts 1–4 tones and 1–512 events for `QRSS`, `FSKCW`, or
`DFCW`. Each event has a bounded nonzero duration and only
`RP1_GPCLK_EVENT_F_OUTPUT_ENABLED` may be set. Enabled events name a valid tone;
disabled events ignore the tone index. The checked event-duration sum equals
`total_duration_ns` and stays within the request limit.

`SUBMIT_TONE` accepts one inline tone. `CONTINUOUS` requires
`duration_ns == 0` and runs until an explicit stop, release, owner close,
provider removal, or failure. Kernel-bounded DMA chunks bound cancellation and
do not create an operator-visible duration. `FINITE` requires 1,000,000 through
120,000,000,000 ns inclusive and completes automatically after cleanup.

## State, drain, cleanup, and release

The observable progression is `IDLE` to `RUNNING`, optionally `DRAINING`, then
`COMPLETE` or `FAILED`. `DEAD` means the provider is removed or permanently
unavailable. Terminal states retain one stable terminal reason. A cleanup
failure latches `FAILED` with `CLEANUP_FAILED` and prevents further use.

`STOP` is generation-specific. It prevents successors, drains only the current
kernel-bounded descriptor, disables pacing and output, restores safe pinctrl
and clock state, verifies cleanup, and then publishes the terminal state.
`GET_STATE` never changes state. `RELEASE` with a nonzero generation follows
the same stop-and-drain path before relinquishing the lease; a zero generation
releases only an idle or terminal lease. Owner close converges on the same
bounded cleanup rules.

## Passive snapshot

`GET_SNAPSHOT` does not acquire ownership, allocate or return a lease token,
advance a generation, submit work, change output state, or clear retained
terminal state. It returns one mutex-serialized observation of route and
identity, compatibility, output eligibility, owner/lease presence, generation,
operation state, terminal reason, current event, drain state, cleanup fault,
timing, and resource quiescence.

`current_event`, `elapsed_ns`, and `remaining_ns` are meaningful only when the
corresponding `RP1_GPCLK_SNAPSHOT_F_*_VALID` bit is present. GPIO safety, clock
quiescence, DMA quiescence, and related observations use `UNKNOWN`, `FALSE`,
and `TRUE`. `stable == TRUE` requires idle or terminal state, completed worker
and plan cleanup, no cleanup fault, and all three resource observations true.
A snapshot describes one instant and is not proof of future state.

`GPIO4` and `GPIO20` remain separate administrative routes. Querying or acquiring
one route never remuxes it, substitutes the other route, or transfers evidence
or eligibility between them.
