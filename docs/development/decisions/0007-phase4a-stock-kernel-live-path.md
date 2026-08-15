<!-- SPDX-License-Identifier: MIT -->

# Decision 0007: Phase 4A stock-kernel live path

Status: accepted for implementation; target output remains inhibited
Date: 2026-08-14

## Context

ABI v1 already freezes finite WSPR and event submissions, STOP, state, routes,
and terminal reasons. Phase 3B implements only clock-disabled query, acquire,
and release. Historical experiments proved RP1 DMA TICK0 can pace DMAengine
transfers to and from GPCLK0 `DIV_FRAC`, but some historical provider code
depends on custom-kernel lease APIs and private provider state. Those
dependencies are rejected here.

## Decision

The production module remains a consumer of the stock `clk-rp1` provider. It
uses only exported common-clock, DMAengine, pinctrl, platform-resource,
device-tree, workqueue/timer, completion, and lifetime APIs.

Two named eight-byte platform resources, `tick-dma0` and `dma-tick0`, are added
symmetrically to both route overlays. Their RP1-relative identities are frozen
for this compatibility generation as TICKS DMA0 control/cycles and DMA TICK0
enable/control. The driver obtains and maps them only through named platform
resources, validates their sizes, parent containment, non-overlap, and expected
relative identity, and owns them through the single route endpoint. It never
accepts their addresses from userspace and never maps general RP1 or clock
provider registers.

The validated DT clock-provider resource remains authoritative for deriving
the CPU-physical `DIV_FRAC` target. DMAengine performs both memory-to-device
divider writes and device-to-memory exact readback through the selected TICK0
request. `clk_get_rate()` is diagnostic only and is not exact divider readback.

Common-clock ordering is:

1. reject an initially enabled clock or conflicting endpoint;
2. retain exclusive-rate protection acquired at probe;
3. capture the supported initial rate and parent identity;
4. set the reviewed initial tone rate while the selected pin is safe;
5. prepare the clock in sleepable context;
6. prepare finite DMA, cancellation, and cleanup before activation;
7. select active pinctrl, enable the clock, then start tick pacing;
8. gate enabled event intervals with balanced `clk_enable()`/`clk_disable()`
   only while the clock remains prepared; sleepable transitions occur in a
   serialized worker, never an hrtimer callback;
9. after completion or STOP, prevent successors and drain at most the current
   finite descriptor;
10. DMA-read the final divider, stop tick pacing, disable/unprepare the clock,
    select safe pinctrl, restore the initial rate through `clk_set_rate()`, and
    release only module-owned resources.

This cannot recreate the historical provider-private lease. Direct-MMIO or
uncoordinated kernel software remains outside complete exclusion; the module
fails closed on every conflict it can observe and never claims more.

All work is driven by one serialized generation-specific kernel thread. DMA
callbacks compare the descriptor generation and only complete the bounded wait;
they do not perform sleepable clock or pinctrl calls. Device removal deregisters
new access, marks the object dead, requests STOP, synchronously terminates DMA
after the bounded drain deadline if necessary, quiesces hardware, and retains
the object until all open-file references close.

An immutable-at-load `live_output` module parameter defaults false and is mode
`0444`. With it false, submission ioctls fail with compatibility rejection
before copying arrays, allocating a live plan, selecting pinctrl, preparing or
changing a clock, configuring/submitting DMA, or writing tick registers.
Phase 4A target testing loads only with the default false value. Submission,
STOP, and stable-state capabilities may be reported only after their complete
production implementations exist; `LIVE_ELIGIBLE` additionally requires the
parameter and an exact allowed compatibility identity. Phase 4A does not grant
that identity.

Phase 4B target execution corrected one Phase 2C assumption: RP1 DW AXI DMA
expects the validated CPU-physical peripheral address in the slave
configuration and performs its own RP1 bus translation. `dma_map_resource()`
returned an invalid all-ones destination on the exact target. The live path
therefore passes the DT-derived CPU-physical `DIV_FRAC` address directly to
DMAengine, with checked representability, and never pretranslates it. This
supersedes the mapping mechanism in Decision 0004 without changing the
DT-derived ownership or containment rules.

Phase 4C changes only the exact live enrollment identity from the completed
GPIO4 slice to the separately wired GPIO20 slice. GPIO4 must reject live probe
under the Phase 4C bytes; this is deliberate route isolation, not a regression
of the retained GPIO4 evidence at its accepted commit.

## Divider and finite-work constraints

All tones in one request must share the reviewed integer divider and differ
only in bounded fractional values. The stock clock is configured to the first
tone before DMA changes `DIV_FRAC`. Divider words contain only the logical
16-bit fraction in bits 31:16. Counts are nonzero and bounded by ABI v1.

WSPR contains exactly 162 finite symbol descriptors, each no longer than
66,792 writes. Event execution compiles finite per-event descriptors whose
checked aggregate allocation and duration remain under explicit kernel limits.
STOP prevents a successor and drains the already issued descriptor; it does not
terminate mid-descriptor unless later evidence proves that ordering safer.

Cleanup/readback/restoration failure publishes `CLEANUP_FAILED`, latches the
device rejected, inhibits new work, and is not cleared by close or a nominal
later request.

## Additive DT consequence

Decision 0006 froze route identities and overlay names, not the complete bytes
of an unreleased Phase 3 prototype. Adding identical named module-owned pacing
resources to both production overlays is an additive internal binding revision.
The compatible string remains v1 only if offline and target DT validation prove
old clock-disabled behavior and new fail-closed parsing unambiguous. Otherwise
implementation stops for a new compatible and coordinated contract update.

## Rejected alternatives

- maintained custom kernel or provider patch;
- `/dev/mem`, raw userspace MMIO, kprobes, private symbols, or provider-private
  state discovery;
- fixed absolute addresses in C source or userspace-supplied resources;
- `clk_get_rate()` as exact `DIV_FRAC` readback;
- sleepable pinctrl/common-clock operations from timer or DMA callback context;
- aborting a finite descriptor before a proven hardware-idle boundary;
- changing rate or restoring a stale snapshot after another consumer acts;
- enabling live output merely because the module builds; and
- automatic fallback to another physical transmitter backend.

## Validation consequence

Phase 4A must provide deterministic fake-boundary tests, representative kernel
builds, a separate adversarial assessment, and a complete clock-disabled
two-route `wspr5` regression with `live_output=false`. No GPIO output or mode/RF
qualification follows from this decision.
