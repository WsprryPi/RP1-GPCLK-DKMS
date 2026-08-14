<!-- SPDX-License-Identifier: MIT -->

# Phase 2 evidence-intake execution prompt

## Role

Act as the engineering archivist and adversarial kernel-module architect for
`WsprryPi/RP1-GPCLK-DKMS`. Establish a self-contained, reviewable baseline for
offline Phase 2 work without implementing the module or initializing Git.

## Authorities

Read and follow, in order:

1. the repository `AGENTS.md`;
2. `docs/contracts/rp1-gpclk-dkms-module-contract.md`;
3. `docs/contracts/phased-plan.md`;
4. the immutable WsprryPi stock-kernel DKMS product contract; and
5. the exact historical WsprryPi RP1 artifacts identified during this work.

The module contract governs this repository. The WsprryPi product contract
governs application integration and product qualification. Stop if they
conflict; do not silently choose one.

## Authorized scope

Perform repository-local research and documentation only:

- inventory historical UAPI, kernel-provider, portable-core, overlay, tests,
  phase reports, and retained evidence;
- record exact source repository paths and Git object identities;
- inspect SPDX, copyright, derivation, and reuse constraints;
- distinguish reusable concepts from code that is reference-only, superseded,
  prohibited as a production dependency, or pending licensing review;
- establish the proposed UAPI conceptual baseline without freezing unresolved
  names, numbers, layouts, or ABI;
- record exact compatibility evidence and identify what remains target-derived;
- identify open decisions and recommend their optimal decision point; and
- create durable repository documents supporting the next offline slice.

Do not:

- initialize Git, create a branch, stage, commit, push, or publish;
- copy implementation source into this repository;
- implement Kbuild, DKMS, module, UAPI, overlay, installer, or test code;
- install, load, bind, unload, or otherwise operate a module;
- change the WsprryPi repository;
- access a Raspberry Pi or change system configuration; or
- perform GPIO, DMA, clock, transmission, SDR, or RF activity.

## Required source inspection

At minimum inspect:

- the userspace UAPI header;
- the historical provider's public and internal contract headers;
- provider implementation, portable core, KUnit, static-contract tests, and
  overlay;
- custom-kernel patches only as historical evidence;
- reports for stock-clock probing, DMA address translation, bounded
  cancellation, production lifecycle, provider UAPI, clock-disabled runtime,
  lease generation, keyed-mode planning, drive selection, and operator
  visibility;
- evidence summaries and checksums relevant to those claims; and
- Git history/object identity sufficient to make every reference reproducible.

Do not infer a conclusion from a filename or summary when the underlying source
or report is available.

## Required deliverables

Create or update:

1. `docs/evidence/historical-evidence-index.md`
   - exact artifact path and immutable WsprryPi Git identity;
   - claim supported;
   - evidence class and limitations;
   - disposition in the DKMS project.
2. `docs/development/provenance.md`
   - repository/commit provenance;
   - per-artifact licensing and copyright observations;
   - reuse classification and conditions;
   - explicit prohibition against relabeling GPL-only derivatives as MIT.
3. `docs/development/uapi-baseline.md`
   - compared historical definitions;
   - preserved concepts and semantics;
   - inconsistencies and migration risks;
   - proposed additive route/capability direction;
   - unresolved ABI decisions clearly marked as not frozen.
4. `docs/development/compatibility-identities.md`
   - identities demonstrated by historical evidence;
   - identities required for future builds and runtime checks;
   - unknowns that cannot be reconstructed safely;
   - rule that build success cannot exceed `Compatible-unqualified`.
5. `docs/development/historical-artifact-inventory.md`
   - every relevant source/report classed as `Reusable`, `Reference only`,
     `Superseded`, `Prohibited production dependency`, or
     `Licensing review required`;
   - rationale and next action.

Update the root README only if needed to make these repository documents
discoverable. Do not imply that module implementation has begun.

## Design-decision rule

Do not manufacture a permanent choice merely to finish the documents. If work
requires a decision that materially fixes public ABI, project/release identity,
licensing scope, supported kernel range, overlay model, device-node naming, or
cross-repository compatibility behavior:

1. finish all objective research that informs it;
2. document the unresolved decision and consequences;
3. present mutually exclusive choices, including compatibility and migration
   costs;
4. recommend one choice with reasons; and
5. stop for the project owner's decision before encoding it as settled.

Choices that can safely remain intentionally unfrozen until implementation
should be recorded and scheduled at the latest safe decision point rather than
blocking evidence intake.

## Adversarial assessment

Attempt to falsify:

- that every inherited technical claim has a reproducible source;
- that source provenance and licensing permit the proposed disposition;
- that the userspace and kernel headers actually agree;
- that old custom-provider assumptions apply to a stock-kernel consumer;
- that fixed addresses, private symbols, kprobes, or provider-private locks
  have accidentally become production dependencies;
- that GPIO4 assumptions have frozen GPIO20 out of the design;
- that historical target evidence has been mistaken for DKMS qualification;
- that compatibility identities are precise enough to reproduce; and
- that the new repository can begin offline work without undocumented reliance
  on chat or developer-local memory.

Inject every objective failure back into the deliverables and repeat the
affected checks. Do not resolve an actual owner decision by assumption.

## Exit gate

Pass only when:

- all five deliverables exist and link to repository or immutable remote
  artifacts rather than local machine paths;
- licenses and provenance are explicit;
- UAPI concepts are traceable but no unresolved ABI is falsely frozen;
- compatibility evidence and unknowns are separated;
- custom-kernel material is clearly historical rather than a product
  dependency;
- GPIO20 remains possible at the Phase 3 boundary;
- an adversarial pass reports no uncorrected objective failure;
- any material design decision is returned to the owner; and
- Git remains uninitialized and no hardware or external repository state was
  changed.
