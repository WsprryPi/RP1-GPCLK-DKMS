<!-- SPDX-License-Identifier: MIT -->

# Phase 4 execution-prompt adversarial assessment

Date: 2026-08-14
Scope: Phase 4 specification and authorization boundary only
Result: prompt pass after four reinjected findings; Phase 4 execution blocked

## Assessment boundary

This assessment reviews
`docs/contracts/phase4-timing-controlled-live-output-execution-prompt.md`.
It does not assess a live-path implementation, target hardware, timing, GPIO,
DMA execution, transmission, or RF evidence. The current driver still exposes
only clock-disabled `QUERY`, `ACQUIRE`, and `RELEASE` behavior.

## Findings and reinjection

1. The first draft treated WSPR UTC alignment as if ABI v1 and the module owned
   scheduled start. ABI v1 has no UTC start field, while WsprryPi owns
   scheduling and its transmitter subproject owns UAPI translation. The prompt
   now requires exact cross-repository artifact identity and prevents a module
   result from claiming application or product qualification.
2. The user requested QRSS/TONE evidence, but ABI v1 has a QRSS enum and no
   separate TONE enum. The prompt now records a constant TONE as one enabled
   QRSS event with one tone and forbids inventing a new frozen mode value.
3. The first matrix grouped FSKCW and DFCW into one result cell. Although one
   bounded authorization may cover the requested FSKCW/DFCW class, their timing
   semantics and qualification results are distinct. The matrix now has
   separate FSKCW and DFCW rows for both routes.
4. Inspection after authorization found that the historical live executor
   depended on custom-kernel provider lease APIs and directly managed DMA-tick
   registers absent from the current module's DT resource contract. Those APIs
   cannot be imported into the stock-kernel design. The prompt now requires a
   reviewed DT-derived DMA-tick ownership/mapping contract, exported DMAengine
   use, supported common-clock enable/disable, exact readback, and proof that
   disabled event gaps do not violate atomic-context or clock-reference rules.
   Live capability must remain absent if that contract cannot be established.

## Blocking assessment

Execution cannot cross the target gates because the current task does not
identify and authorize the exact target administration, GPIO fixture/output
bounds, or conducted-RF chain and matrix rows required by Gates B, C, and D.
It also does not provide predeclared numeric acceptance thresholds, sample
counts, instrument/reference identities, calibration evidence, or emergency
disconnect procedure. Inventing those values after measurement would invalidate
the qualification.

No target connection, installation, module load/bind, overlay mutation, active
pinctrl selection, clock preparation or enablement, DMA submission, GPIO
output, transmission, SDR capture, or RF operation is authorized by the prompt
itself. Phase 4 therefore remains open and the compatibility ceiling remains
`Compatible-unqualified`.
