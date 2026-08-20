<!-- SPDX-License-Identifier: MIT -->

# Phase 4A implementation adversarial assessment

Date: 2026-08-14
Result: pass for the clock-disabled Phase 4A exit gate
Compatibility ceiling: `Compatible-unqualified`

## Scope

This separate review attempted to falsify the stock-kernel live path,
immutable enrollment gate, DT authority, finite DMA sequencing,
generation/lifetime behavior, cleanup ordering, capability claims, route
neutrality, licensing, and accepted `wspr5` evidence. It did not assess live
timing, GPIO waveform quality, modes, SDR reception, or RF.

## Findings reinjected and resolved

1. Active pinctrl selection originally preceded descriptor preparation. The
   production state machine now activates only after a finite DMA descriptor
   is configured. Activation failure terminates the owned descriptor and uses
   the common cleanup path.
2. The fake-boundary cleanup model was disconnected from production. It now
   directly sequences production rate, prepare, activation, readback, tick
   stop, DMA termination, clock balance, safe pin, and restoration callbacks.
   Tests inject every start and cleanup failure, attempt all remaining cleanup,
   and preserve the first error.
3. Linux exposed recursive `errno.h` fixture shadowing hidden by macOS. The
   fixture now supplies only the required stable constants; both host suites
   pass.
4. The RP1 parent has `ranges`, not a `reg` resource. The driver now uses the
   exported `of_range_to_resource()` API and validates both named translated
   resources within that authoritative range. Both runtime routes passed.
5. DMA completion lacked an explicit generation comparison. The callback now
   rejects a descriptor generation that differs from the live generation;
   synchronous teardown precedes plan release.
6. `GET_STATE` returned zero timing fields. It now snapshots bounded monotonic
   elapsed and remaining values under the device lock.
7. The second forced-quiescence deadline lacked an explicit terminal action.
   It now emits a critical diagnostic and synchronously stops the sole worker
   before resource release if bounded drain and forced DMA termination fail.

## Residual limitations and verdict

The stock consumer cannot reproduce the provider-private lease; exclusive-rate
protection is not exclusive enable ownership, and hostile raw MMIO remains
outside complete exclusion. `__clk_is_enabled()` is an exported dependency for
this exact kernel and must be revalidated for every new identity. DTC emits
overlay-context address-cell warnings because it cannot see target RP1 bus
cells; runtime decoding and translated-resource checks passed for both routes.

No unresolved objective finding remains against the Phase 4A clock-disabled
exit gate. This does not authorize or qualify live output. GPIO4 and GPIO20;
QRSS/TONE, FSKCW/DFCW, and WSPR; timing/jitter; live cancellation, readback,
restoration, neighboring-register integrity; and conducted SDR evidence remain
separate Phase 4 live qualification work.
