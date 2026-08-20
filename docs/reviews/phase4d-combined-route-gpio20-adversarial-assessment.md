<!-- SPDX-License-Identifier: MIT -->

# Phase 4D combined-route GPIO20 adversarial assessment

Date: 2026-08-14
Status: passed for GPIO20; no unresolved objective finding in this slice

The assessment challenged exact-byte dual-route enrollment, GPIO4 output
exclusion, GPIO20 route identity, bounded duration, all mode distinctions,
WSPR vector provenance and all-symbol recovery, final-divider readback, owned
neighbor-window restoration, STOP drain, terminal uniqueness, run-local log
scope, final absence, service preservation, and archive relocation.

Two findings were reinjected. First, the initial WSPR phase-slope estimator
locked onto receiver phase discontinuities and falsely reported 10.93 Hz tone
spacing. The immutable capture was reanalyzed with a carrier-bounded,
per-symbol windowed spectral estimator. It recovered 1.4683 Hz spacing, zero
symbol errors against the pinned 162-symbol `AA0NT EM18 20` vector, and a
0.242 Hz maximum fit residual. No repeat output was needed because source IQ
and pass limits were unchanged.

Second, fail-closed analyzer termination prevented the harness from writing
its planned whole-run delta. All 14 per-request logs were already retained.
The delta was reconstructed from the pre-run baseline and current kernel log,
classified successfully with exactly 14 Phase 4D telemetry rows, and added to
the resealed checksum manifest and portable archive.

No unresolved finding remains for GPIO20. Claims remain limited to relative
frequency, the mapped module-owned tick windows, this exact target and
candidate, and the conducted fixture. Absolute frequency and power remain
unavailable. The subsequently completed exact-byte GPIO4 matrix and combined
disposition are recorded in the Phase 4E assessment and Phase 4 closeout.
