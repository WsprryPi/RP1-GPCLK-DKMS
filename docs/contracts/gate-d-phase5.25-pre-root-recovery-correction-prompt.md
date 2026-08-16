<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.25 pre-root staging and recovery correction prompt

## Objective

Create a distinct `0.0.0-phase5.25` successor that closes the two blocking
findings proved by the authorized Phase 5.24 pre-root attempt: the administrator
release-directory input graph was incomplete, and pre-root recovery could not
clean a failure that occurred before administrator transaction-state creation.

Perform this slice entirely offline. Preserve the Phase 5.24 evidence and its
target residue as historical facts. Stop before contacting either Raspberry Pi,
changing or cleaning the target, performing a representative build, staging
new target inputs, installing or loading anything, changing services or boot
state, rebooting, accessing GPIO or clocks, submitting DMA, using the Si5351 or
SDRplay, transmitting, performing RF activity, tagging, publishing, or changing
consuming repositories.

## Verified starting evidence

- Phase 5.24 passed deterministic offline construction, representative build,
  and authenticated pre-root validation.
- Its target transition failed before DKMS or package mutation because
  `/home/pi/gate-d-inputs/phase5.24-2a6ddeb8e0f7/release-metadata.json` was
  absent.
- Its sealed `--resume` path then failed because administrator recovery
  rejected the correctly absent administrator transaction state.
- The operational target baseline remained unchanged. Only the immutable
  Phase 5.24 inputs, partial qualification-root marker, and pre-root recovery
  journal remain.

## Required implementation

1. Supersede Phase 5.24 with a distinct Phase 5.25 development candidate;
   never modify or relabel the frozen Phase 5.24 archive.
2. Define a closed administrator release-directory input set containing the
   exact source archive, GPIO4 and GPIO20 DTBOs, compatibility manifest,
   provenance, release metadata, and checksum manifest required by
   `rp1-gpclk-admin.py`.
3. Bind every required sidecar by exact path and SHA-256 in the pre-root
   envelope and its schema. Reject missing, extra-required, swapped, stale,
   symlinked, substituted, or mode/ownership-invalid inputs before mutation.
4. Validate `SHA256SUMS` transitively: its membership and hashes must agree with
   the closed staged release set, release metadata, candidate archive, DTBOs,
   compatibility manifest, and provenance.
5. Make the pre-root journal record whether administrator invocation began and
   whether administrator transaction state exists. Recovery must be
   phase-aware, fail-closed, and repeatable:
   - before administrator invocation, skip administrator recovery;
   - after invocation but before administrator state exists, verify the empty
     runtime baseline and skip administrator recovery;
   - when exact administrator state exists, invoke only the sealed recovery;
   - reject foreign, symlinked, substituted, ambiguous, or unsafe state;
   - always clean only authenticated pre-root-owned files and directories;
   - permit repeated recovery to report a clean result without broad deletion.
6. Bind a reviewed Phase 5.24 residue-recovery document describing the exact
   marker, journal, absent administrator state, expected baseline, allowed
   cleanup paths, and refusal conditions. Keep it offline and unexecuted in
   this slice.
7. Ensure the permanent executor, bootstrap plan, target plan, installation
   inventory, schemas, release metadata, and complete transitive Python import
   graph use the Phase 5.25 identities consistently.

## Deterministic and adversarial tests

Test the exact installed/staged filesystem layout outside a checkout. Cover:

- the complete valid sidecar graph and `SHA256SUMS` membership;
- each sidecar missing, swapped, stale, substituted, symlinked, duplicated, or
  placed at the wrong path;
- interruption before root creation and after every pre-root checkpoint;
- install failure before administrator invocation, after invocation with no
  administrator state, and with exact administrator state;
- missing, foreign, stale, symlinked, partial, and already-clean journals;
- missing, substituted, symlinked, or foreign root markers and children;
- cleanup failure, recovery interruption, and repeated recovery;
- preservation of unrelated files, services, boot bytes, and historical
  evidence; and
- output-disabled invariants throughout every success and failure path.

Perform a separate adversarial assessment. Reinject every actionable finding
and repeat affected checks until no blocking software finding remains. Run the
complete offline suite twice. Build the exact clean source twice and freeze
Phase 5.25 identities only if the archives and all generated artifacts are
byte-identical and validate successfully.

## Exit criteria

Report implemented behavior, files changed, exact checks and results, skipped
target work, licensing/documentation impact, remaining Phase 5.24 residue, Git
state, and the next gate. Stop before representative build or Pi access. A
separately reviewed authorization is required to run the Phase 5.24 residue
recovery document; a later fresh authorization is required for Phase 5.25
representative build and target execution.
