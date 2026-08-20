<!-- SPDX-License-Identifier: MIT -->

# Phase 4 receiver-relative qualification closeout

Date: 2026-08-14
Status: complete under the accepted receiver-relative calibration scope

One exact combined stock-kernel candidate now has independent GPIO4 and GPIO20
evidence for QRSS/TONE, FSKCW, DFCW, WSPR, cancellation, DMA sequencing,
divider readback, owned neighboring-window integrity, and restoration. Both
routes used 2 mA and the same conducted two-attenuator RSP1B fixture. Every
live request was finite, and both route runs ended with pins input, common-clock
counts zero, no overlay/module/endpoint/installed artifact, and services
unchanged.

The GPIO20 report and archive are
`docs/evidence/phase4d-combined-route-gpio20.md` and SHA-256
`4d458e77f8fc4208e8485ff53ede89b265c1a5910dbf49b45ad684804b524fab`.
The GPIO4 report and archive are
`docs/evidence/phase4e-combined-route-gpio4.md` and SHA-256
`bdba7ac3a37c6dfbc1ac006a73b3af3e41f0488b1ef0ad1f96bd7a864dce7e73`.
Separate adversarial assessments have no unresolved objective finding.

This closeout does not claim calibrated absolute carrier frequency, output
power, spectral-regulatory compliance, antenna radiation, another Raspberry
Pi/kernel/device-tree identity, higher drive, or application-level scheduling.
The user explicitly accepted receiver-relative calibration for this phase and
deferred an absolute calibrated series. That later series is an additive
qualification, not evidence already obtained here.
