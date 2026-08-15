<!-- SPDX-License-Identifier: MIT -->

# Phase 4C GPIO20 adversarial assessment

Date: 2026-08-14
Status: passed; no unresolved objective finding in the bounded GPIO20 scope

## Assertions challenged

- The live parameter alone cannot enroll a route: exact Raspberry Pi model,
  kernel, module identity, and GPIO20 route are required.
- GPIO4 was probed under live enrollment and rejected without an endpoint or
  output; GPIO20 alone reported `LIVE_ELIGIBLE`.
- The exact candidate passed the offline suite twice, warnings-fatal running-
  header build, and complete Phase 4A clock-disabled matrix before output.
- Each of 13 final requests has one telemetry row, exact divider readback,
  four-window tick restoration, cleanup fault zero, safe pin, and restored
  common-clock observations.
- Raw IQ independently supports the ten QRSS durations, FSKCW tone order and
  spacing, DFCW marks and disabled gaps, and bounded STOP result.
- Whole-boot historical diagnostics are excluded from the run-local delta.
- The portable archive verifies after independent relocation and the current
  target is absent/safe.
- Claims do not expand mapped neighboring-register evidence into unsupported
  provider-register coverage, relative spacing into absolute frequency, or a
  shortened program into WSPR evidence.

## Finding and reinjection

The otherwise-passing first analysis printed the inherited label
`PHASE4B_ANALYSIS=PASS`. Raw IQ and all kernel evidence were preserved. The
GPIO20 analyzer label was corrected to `PHASE4C_ANALYSIS=PASS`, the immutable
captures were reanalyzed with unchanged calculations and limits, internal
checksums were regenerated, and the archive was resealed and relocated twice.
No hardware rerun was necessary because neither measurement input nor decision
logic changed.

## Disposition

The bounded GPIO20 receiver-relative timing, relative-mode, DMA, cancellation,
restoration, and mapped-neighbor integrity qualification passes. Absolute
carrier accuracy and WSPR remain `Unavailable`. Together with the separately
accepted GPIO4 evidence, both administrative GPIO routes now have independent
controlled-output evidence on this exact target identity.
