<!-- SPDX-License-Identifier: MIT -->

# Phase 3B adversarial assessment

Date: 2026-08-14
Scope: exact two-route clock-disabled execution, evidence, cleanup, and freeze
Result: pass after eleven reinjected findings; no unresolved Phase 3B blocker

## Method and findings

The assessment attempted to falsify route-neutral identity, GPIO20 independence,
compiled overlay and runtime DT identity, cross-route exclusion, pin/DMA
conflict unwind, descriptor/process lifetime, repeated administration, update
failure recovery, diagnostic completeness, evidence portability, and final
absence. Findings were added to the Phase 3B prompt before correction, and the
affected work was never accepted without a complete rerun.

Findings 1-5 corrected a GPIO4-specific compatibility identifier, preserved
historical Phase 2E validators, added GPIO20-specific negative fixtures,
resolved runner static-analysis defects, and restored exact whitespace.
Attempts 1-3 then exposed AppleDouble source contamination, incorrect handling
of an expected production-overlay conflict, and a diagnostic classifier keyed
to filenames rather than runtime node identities. Each attempt was preserved,
corrected, and rerun from a safe baseline.

The first complete target pass was independently checksummed but adversarial
review rejected its lifecycle coverage: open/unbind was GPIO20-only and did
not explicitly prove new-open failure or post-unbind unload blocking. Findings
9-10 added the full sequence for both routes, strengthened terminal absence to
include the installed artifact and bound-device set, and made source identity
portable. The entire matrix—not only those rows—then passed again.

The staged-diff gate then found extra EOF blank lines in six new source files.
Because removing them changed tested bytes, finding 11 rejected attempt 5 as
the final reproducibility record and required one last complete run from the
whitespace-clean snapshot.

## Independent evidence assessment

The final target and local outer archive hashes match. Every inner manifest
entry verifies after relocation. The ledger contains distinct GPIO4 and GPIO20
UAPI/DT identity passes, expected cross-route failures, process-death status
137 for both routes, six cycles in each route order, both strengthened
open-descriptor sequences, known-good recovery, the exact 22-line classified
dmesg delta, and the terminal zero/absent assertions.

The review found no claim that exceeds the evidence. Build and clock-disabled
administration retain a `Compatible-unqualified` ceiling. No GPIO4 result is
used as GPIO20 evidence, and no Phase 4 timing, active-output, transmission, or
RF claim is made. Phase 4 remains separately authorized.
