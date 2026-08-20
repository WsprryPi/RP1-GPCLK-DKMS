<!-- SPDX-License-Identifier: MIT -->

# Phase 4E combined-route GPIO4 adversarial assessment

Date: 2026-08-14
Status: passed; no unresolved objective finding

The assessment independently challenged whether the GPIO4 run used the exact
combined candidate qualified on GPIO20, whether GPIO20 could emit, every mode
decision, all 162 WSPR symbols, duration and relative spacing, cancellation,
divider readback, tick-window integrity, terminal uniqueness, cleanup, service
preservation, checksums, and archive relocation.

The unsigned module, UAPI, overlays, FDT, kernel, build identity, and
compatibility identity match the GPIO20 evidence exactly. GPIO20 was query-only.
All 14 GPIO4 requests have one terminal observation and one telemetry row,
cleanup zero, exact final-divider readback, and restored tick state. Raw IQ
supports each timing and tone decision. WSPR recovered all 162 symbols with
1.46426 Hz fitted spacing. The target ended absent and safe, and the relocated
archive verified.

No finding required reinjection or another burst. Absolute frequency and power
remain outside this receiver-relative result. Under the user's explicit
acceptance of relative calibration for now, the calibrated series is deferred
and does not invalidate the bounded Phase 4 timing/live-output matrix.
