<!-- SPDX-License-Identifier: MIT -->

# RP1 stock-kernel DKMS phased plan

Date established: 2026-08-13
Imported into this project: 2026-08-14
Original context: `WsprryPi/WsprryPi` feasibility research
Current authority: execution sequence subordinate to the
[module engineering contract](rp1-gpclk-dkms-module-contract.md)

This plan was preserved from the pre-repository WsprryPi research. Its project
boundary is updated here: kernel-module work occurs in
`WsprryPi/RP1-GPCLK-DKMS`; application integration and product qualification
remain in their owning WsprryPi repositories.

## Durable decision

Reject a custom-maintained Raspberry Pi kernel as the product architecture.
Pursue a stock-kernel-compatible, out-of-tree RP1 provider module distributed
as source and built locally through DKMS. Treat DKMS build success as build
compatibility only, never as hardware, timing, cleanup, RF, or coexistence
qualification.

The stock-kernel design cannot reproduce the custom provider-side GPCLK lease
completely. Common-clock exclusive-rate protection does not grant sole
ownership of clock enable state, and direct DMA writes to the RP1 GPCLK0
fractional divider bypass the stock clock driver's internal register lock.
Support must be explicit opt-in, fail closed on unknown or incompatible
combinations, and place documented dedicated-host and cohabitation
responsibility on the operator.

## Phase 1 - Contract and feasibility design

Status: complete when the project foundation and both corollary contracts have
passed review. No module behavior is implemented by this phase.

- Preserve the existing bounded userspace/provider UAPI concepts where
  feasible.
- Define compatibility states: `Qualified`, `Experimental`,
  `Compatible-unqualified`, `Unavailable`, and `Rejected`.
- Keep names, APIs, structures, diagnostics, and configuration route-neutral.
- Model allowlisted routes rather than accepting arbitrary GPIO numbers.
- Reserve GPIO4 and GPIO20 as eventual explicit routes without implementing
  GPIO20 yet.
- Define rollback, uninstall, signing, kernel-update, and fail-closed behavior.
- Establish repository ownership, licensing, UAPI authority, artifact identity,
  and release ordering.

Exit gate: no custom-kernel dependency remains; interfaces do not embed GPIO4
in a way that forces later migration; repository and licensing boundaries are
explicit; and adversarial review finds no unresolved architectural blocker.

## Phase 2 - GPIO4 clock-disabled prototype

Status: complete for the exact `wspr5` Raspberry Pi 5 / stock
`6.18.34+rpt-rpi-2712` identity recorded in the Phase 2E evidence. This is not
a general compatibility or live-output qualification.

- Build an out-of-tree module against explicitly identified representative
  kernel headers and prepare it for DKMS integration.
- Use DMAengine for DMA-channel allocation, pinctrl for GPIO4 routing, and
  supported common-clock APIs for preparation, rate configuration, and
  balanced enable/disable.
- Derive and validate the GPCLK0 fractional-divider DMA destination from the
  authoritative RP1 device-tree clock-provider resource. A fixed absolute
  address is not the primary contract.
- Keep live output disabled.
- Prove source-level UAPI validation, ownership, lifetime, cancellation, stale
  callback, and partial-acquisition cleanup offline.
- Under separately authorized clock-disabled target administration, prove bind,
  unbind, process-death cleanup, unload constraints, conflict behavior,
  signing, and failed-kernel-update behavior.

Exit gate: every GPIO4 clock-disabled safety and lifecycle test passes on the
exact target. Compilation alone does not satisfy the gate.

## Phase 3 - GPIO20 injection before interface freeze

Status: complete for the exact `wspr5` Raspberry Pi 5 / stock
`6.18.34+rpt-rpi-2712` clock-disabled identity recorded in the Phase 3B
evidence. This does not authorize or qualify live output.

This is the deliberate point to add GPIO20: after the central GPIO4
stock-kernel feasibility result is known, but before freezing the UAPI, overlay
format, compatibility manifest, installer configuration, persisted selector,
or operator documentation.

- Verify GPIO20's authoritative RP1 pinmux, GPCLK routing, electrical
  capability, and device-tree representation.
- Add GPIO20 as a second allowlisted pinctrl-backed route using proven backend
  machinery.
- Reject unsupported and arbitrary GPIO selections.
- Confirm that selecting one route leaves the other safe and unclaimed.
- Keep GPIO20 compatibility and qualification distinct from GPIO4.

Exit gate: both routes pass independent clock-disabled selection, conflict,
cleanup, cancellation, mismatch, and safe-state tests, including repeated
administrative route changes.

## Phase 4 - Timing and controlled live-output qualification

This phase requires separately authorized target GPIO and RF operation.

Phase 4A has implemented and clock-disabled-tested the gated stock-kernel live
path on the exact recorded `wspr5` identity. That result is prerequisite
engineering evidence only: it does not qualify a route, timing, mode, GPIO
output, or RF. Controlled output begins only in a separately reviewed Phase 4B
slice.

- Measure scheduled common-clock enable/disable latency and jitter.
- Validate DMA divider sequencing and neighboring-register integrity.
- Exercise initially enabled clocks and competing cooperative consumers; reject
  unsafe startup.
- Perform bounded live qualification independently for GPIO4 and GPIO20.
- Record exact Pi model, kernel, device tree, overlay, route, drive, frequency,
  mode, module artifact, UAPI, and evidence identity.
- Qualify each supported transmission mode separately.

Exit gate: every advertised route and mode has independent timing, cleanup,
recovery, and RF evidence. Do not generalize across routes or kernels.

## Phase 5 - Packaging and operator enablement

- Distribute source, Kbuild files, `dkms.conf`, tightly scoped overlays,
  compatibility metadata, diagnostics, signing guidance, rollback, removal,
  provenance, and operator warnings.
- Consume tagged, checksummed releases through an explicit WsprryPi
  compatibility manifest; never consume a moving branch.
- Default new and rebuilt installations to no live output unless the exact
  combination is qualified or an administrator explicitly enrolls in
  `Experimental` operation.
- Make the device node restrictive and require explicit administrator
  acceptance of dedicated-host and software-cohabitation responsibilities.
- On kernel updates, rebuild through DKMS but demote unknown combinations to
  `Compatible-unqualified` or `Unavailable`.
- Never fall back to `/dev/mem`, a custom kernel, or another physical backend.

Exit gate: installation, update, downgrade, removal, signing, and failure
recovery pass on representative target systems without weakening compatibility
or qualification boundaries.

## Hardware-control boundary

| Phase | No RP1 Pi access | RP1 administration with output disabled |
| --- | --- | --- |
| 1 - Contract and feasibility | Complete | Complete |
| 2 - GPIO4 clock-disabled prototype | Partial implementation only | Complete for the exact recorded `wspr5` identity |
| 3 - GPIO20 before interface freeze | Implementation complete | Complete for the exact recorded `wspr5` identity |
| 4 - Controlled live qualification | Live path implemented offline | Phase 4A clock-disabled prerequisite complete; live qualification incomplete |
| 5 - Packaging and enablement | Partial implementation only | Mostly; representative lifecycle systems remain required |

Module binding and every target-Pi operation require explicit authorization,
even when output remains disabled. Clock-disabled administration is distinct
from live GPIO and RF authorization.

## Persistent non-goals and cautions

- No WsprryPi-maintained custom kernel.
- No claim of complete exclusion against direct-MMIO software.
- No assumption that exclusive-rate APIs lease clock enable state.
- No qualification inherited from DKMS compilation.
- No GPIO20 support or qualification inferred from GPIO4 results.
- No arbitrary GPIO selector.
- No automatic physical-backend fallback.
- No live hardware or RF work without separately bounded authorization.

## Provenance

This document incorporates the pre-repository WsprryPi RP1 stock-kernel DKMS
phased plan established on 2026-08-13. This repository file is now the
portable, reviewable copy used by the module project; no developer-local path
is part of the project contract.
