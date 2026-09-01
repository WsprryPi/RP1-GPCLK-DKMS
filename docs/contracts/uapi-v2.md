<!-- SPDX-License-Identifier: MIT -->
# RP1 GPCLK UAPI ABI v2 contract

ABI v2 extends ABI v1, which remains supported unchanged. The
byte-authoritative current header is `include/uapi/linux/rp1_gpclk.h`, and the
canonical endpoint remains `/dev/rp1-gpclk`.

## Negotiation

New consumers issue `QUERY_V2` (ioctl number `0x27`) with an exact v2 header.
An old module rejects this unknown ioctl with `EOPNOTSUPP`. A new module retains
the original v1 QUERY result and v1 capability set. V2 QUERY reports ABI range
1 through 2 and separately advertises `TONE_CONTINUOUS` and `TONE_FINITE`.
Unknown header flags, reserved fields, capability requirements, operations,
sizes, or versions fail closed.

## TONE

`SUBMIT_TONE_V2` (ioctl `0x28`) accepts exactly one inline v1 tone descriptor.
The descriptor expresses frequency through adjacent Q16 divider values and a
bounded dither period; fractional bits are 16, the tick divider is 511, the
integer divider is 1 through 255, and only advertised drive strengths are
valid. The request route must equal the acquired route.

`CONTINUOUS` is operation 1 and requires `duration_ns == 0`. It has no hidden
deadline, retry, or repetition policy and remains RUNNING until a generation-
specific STOP, RELEASE_V2, owner close, provider removal, or failure. Kernel
execution uses bounded one-second DMA chunks solely to bound cancellation; a
chunk is not an operator-visible duration.

`FINITE` is operation 2 and requires a duration from 1,000,000 through
120,000,000,000 ns inclusive. The kernel owns that deadline and automatically
publishes COMPLETE/COMPLETE after cleanup. The one-second qualification form
uses exactly 1,000,000,000 ns. Zero and overflowed/out-of-range durations fail.

Both forms require a recognized route-specific compatibility identity and
LIVE_ELIGIBLE at ACQUIRE and submission. No compatibility or qualification
evidence transfers between source identities, routes, or targets.

STOP moves RUNNING to DRAINING, wakes the DMA wait, terminates callbacks and DMA,
stops the tick source, disables and unprepares the clock, selects the safe GPIO
state, restores the prior rate, verifies readback, and only then publishes a
stable terminal state. Cleanup failure latches FAILED/CLEANUP_FAILED.
`RELEASE_V2` (ioctl `0x29`) performs generation-specific stop, bounded drain,
then lease release. Historical v1 RELEASE remains terminal-only.

For continuous TONE, v1 `GET_STATE` reports RUNNING with elapsed and remaining
both zero as an explicit unbounded-duration sentinel. Finite TONE reports a
kernel-clamped elapsed value and nonnegative remaining duration.

WSPR remains dedicated `SUBMIT_WSPR`; QRSS, FSKCW, and DFCW remain finite
`SUBMIT_EVENTS` modes. No existing numeric identity or meaning is changed.
