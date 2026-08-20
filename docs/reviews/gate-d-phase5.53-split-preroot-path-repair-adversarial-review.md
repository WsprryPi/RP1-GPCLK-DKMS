<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 split pre-root path repair adversarial review

## Outcome

Pass for offline repair only. The repaired controls are not authorized for
target staging or execution.

## Assertions challenged

1. **Every path-bearing pre-root consumer was reconstructed.** The envelope's
   staged executor and pre-root module now resolve to their exact
   `control-set/scripts/` inputs. The administrator remains under the extracted
   54-file product archive. All four primary identities, including the
   qualification identity, are hash-equal members of `inputFiles`.
2. **The new topology is executable rather than merely deterministic.** The
   offline rehearsal reconstructs the 118-path split staging closure and runs
   the exact frozen `gate_d_outer.py pre-root-bootstrap` entry point, which
   loads and validates the exact frozen pre-root module successfully.
3. **Historical validation was not broken.** A proposed universal input-binding
   rule invalidated older envelopes and was rejected. Phase 5.53 enforces the
   stronger closure in its generator and exact rehearsal while the complete
   historical offline suite remains green.
4. **Schema 6 compares live predecessor state.** The independent snapshot
   comparator now selects `predecessorPackagePaths` for schemas 5 and 6 and
   treats an absent representative-build recovery identity as unclaimed rather
   than mismatched. Exact Phase 5.53 live comparison passes.
5. **Old authority cannot leak forward.** The prior envelope and authorization
   phrase are explicitly superseded. The repaired execution instance has
   `approved=false`, `targetExecutionApproved=false`, and
   `executionReady=false`; the historical attestation marks its old control set
   retired.
6. **Artifact ownership remains unchanged.** The product and qualification
   archives remain byte-identical at SHA-256
   `ae6df3a66a9a26a6fb8474e5896c9053b9f69580d8c45383a5556fc397ebb549`
   and `d931912d6ccc381b10a2a13d7f3a9122b0f748490ec8eefe0f86a28cb352c8d0`.

## Safety and claim ceiling

No target contact, staging, administrator invocation, pre-root transition,
lifecycle attempt, kernel or service mutation, GPIO/clock/DMA activity,
transmission, or RF work occurred. Passing this review establishes only an
offline-valid repaired control set awaiting a new explicit authorization.
