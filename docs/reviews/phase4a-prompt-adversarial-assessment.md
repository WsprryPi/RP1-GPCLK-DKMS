<!-- SPDX-License-Identifier: MIT -->

# Phase 4A implementation-prompt adversarial assessment

Date: 2026-08-14
Scope: stock-kernel live-path implementation prompt only
Result: pass after two reinjected findings

## Boundary

This assessment reviews
`docs/contracts/phase4a-stock-kernel-live-path-implementation-execution-prompt.md`.
It does not validate an implementation, build, target run, GPIO output, timing,
SDR capture, transmission, or RF. The current production driver remains the
clock-disabled Phase 3B implementation.

## Findings and corrections

1. The first draft required implemented submission code and a clock-disabled
   target regression but did not mandate a technically enforced output-inhibit
   control. Runner discipline alone could not prove that an accidental submit
   would remain inert. The prompt now requires an immutable-at-load,
   default-disabled enrollment gate, rejection before every hardware mutation,
   static runner checks, and tests that distinguish implemented capability from
   live eligibility.
2. The first draft required DT-derived DMA-tick resources while also treating
   the Phase 3 interface freeze as immutable, without forcing a decision about
   new overlay properties/resources. The prompt now requires an explicit
   compatibility assessment and, if necessary, a reviewed additive DT/overlay
   contract decision applied symmetrically to both routes and negative
   fixtures before implementation.

## Result

The corrected prompt has a hard stop before GPIO4 and does not allow Gate C to
leak into Phase 4A. It preserves the stock-kernel, exported-API, DT-derived,
route-neutral, frozen-UAPI, fail-closed, evidence-integrity, licensing, and
adversarial-reinjection requirements. No prompt-level objective blocker remains.
