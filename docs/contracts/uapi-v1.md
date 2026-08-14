<!-- SPDX-License-Identifier: MIT -->

# RP1 GPCLK UAPI ABI v1 contract

## Authority and status

The byte-authoritative header is `include/uapi/linux/rp1_gpclk.h`. This
document defines its validation and state semantics. Phase 3 freezes ABI v1 at
the exact byte identity recorded in `uapi-identity.json`; see Decision 0006.
Phase 3 implements only
clock-disabled `QUERY`, `ACQUIRE`, and `RELEASE`. Submission, STOP, and state
progression remain unavailable and fail with `EOPNOTSUPP`; their layouts stay
public contracts for later implementation rather than implemented behavior.

## Common validation

Every request must have its exact V1 `size`, version 1, zero header flags, and
zero reserved fields. Unknown commands, flags, enum values, routes, modes,
capability bits, nonzero reserved bytes, or non-NUL-terminated identity strings
fail closed. Output structures are zero-initialized before fields are filled;
identity strings are NUL-terminated and zero-padded.

All counts and duration sums use checked arithmetic before allocation or copy.
User pointers are copied once into bounded kernel-owned storage; they are not
retained. A nonzero `lease_id` belongs to one open file. Generations are
nonzero, strictly increase within that lease, and are rejected when stale or
associated with another lease.

## Query and compatibility

`QUERY` is read/write because userspace supplies the common header and the
kernel returns the remaining fields. It reports an administratively bound
allowlisted route; it never selects a route. `capabilities` describes
implemented operations. `LIVE_ELIGIBLE` may be present only when the exact
compatibility identity permits live use; its absence overrides submission
availability for live output. Raw physical/DMA addresses and register offsets
are never returned.

`compatibility_state` and `compatibility_reason` use their separate enums.
`module_id`, `build_id`, and `compatibility_id` are stable, NUL-terminated,
zero-padded identifiers, not free-form diagnostics. The supported-drive mask
uses `DRIVE_SUPPORT_*` bits; submission `drive_ma` uses the literal 2, 4, 8,
or 12 mA values.

## Acquisition and work

`ACQUIRE` verifies `expected_route` and all `required_capabilities`. It returns
a new opaque lease ID only after exclusive ownership is established. The
future implementation must not return partial ownership.

Both submission commands point to a tone array. Each tone contains lower and
upper unsigned Q16 divider values and dither counts. Both counts must be
nonzero, their checked sum must not exceed `RP1_GPCLK_DITHER_PERIOD_MAX`, and
the upper divider must equal the lower divider plus one. Divider acceptance is
further restricted by the recognized provider/layout compatibility identity;
the UAPI does not authorize arbitrary register values.

`SUBMIT_WSPR` requires exactly four tones and 162 one-byte symbol indexes.
Every symbol is less than `tone_count`; each tone's checked count sum equals
`writes_per_symbol`; `fractional_bits` is 16; `tick_divider` is 511; and
`writes_per_symbol` is nonzero and no greater than 66,792. The expected frame
duration must be nonzero and no greater than the request-duration limit.

`SUBMIT_EVENTS` accepts QRSS, FSKCW, or DFCW, not WSPR. It requires 1-4 tones
and 1-512 fixed-size events. Each event has a nonzero duration within the event
limit, a zero reserved field, and only `OUTPUT_ENABLED` as a flag. A disabled
event ignores `tone_index`; an enabled event requires it below `tone_count`.
The checked duration sum must equal `total_duration_ns` and remain within the
request limit. `fractional_bits` is 16 and `tick_divider` is 511.

Submission succeeds only after the complete request validates and is copied.
It returns its generation without starting unbounded work.

## State, stop, and release

The observable progression is `IDLE` to `RUNNING`, optionally `DRAINING`, then
`COMPLETE` or `FAILED`. `DEAD` means the provider is removed or permanently
unavailable. Terminal states retain exactly one terminal reason. Nonterminal
states report `NONE`; normal completion reports `COMPLETE`; a completed stop
reports `STOPPED`; failures use the most specific stable failure reason.

`STOP` prevents a successor and initiates the separately validated bounded
drain. It is generation-specific and idempotent only for the same terminal
generation. `GET_STATE` never changes state. `RELEASE` requires the matching
lease, refuses active unsafe release, and cannot clear a cleanup-fault latch.
Owner close follows the same bounded cleanup path and publishes
`OWNER_CLOSED` where work was active.

## Additive evolution

V1 layouts, offsets, numeric assignments, flags, and meanings are immutable.
An extended structure receives a new command number and explicit suffix; it
does not enlarge an existing `_IOC_SIZE`. New capabilities, enum values, and
reasons are additive. Reserved values and fields remain unavailable until a
reviewed revision assigns them.

The stable administrative routes are GPIO4 value 1 and GPIO20 value 2. A
queried route reports the overlay-bound route; `ACQUIRE.expected_route` must
match it and cannot remux or change the administrative route.
