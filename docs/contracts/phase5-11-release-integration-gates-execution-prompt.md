<!-- SPDX-License-Identifier: MIT -->

# Phase 5.11 release and integration gates execution prompt

## Authority, mission, and exit condition

Execute only the bounded offline Phase 5.11 portion of
`phase5-packaging-operator-enablement-execution-prompt.md`. Repository changes,
release-gate design, deterministic validation, and documentation are
authorized. This slice does not authorize target access or mutation, package
or DKMS administration, signing or key changes, module or overlay
administration, boot changes, reboot, GPIO, clock, DMA, transmission, RF,
tagging, release publication, public-artifact download, issue changes, or
changes to `WSPR-Transmitter` or `WsprryPi`.

Phase 5.11 closes when candidate and published-release identities are
unambiguous; the module-publication and dependent-integration gates are frozen
in a machine-readable ordered contract; invalid, skipped, circular, or
over-broad claims fail deterministic validation; the complete offline suite
passes twice; and a separate adversarial assessment has no finding. Phase 5.11
does not close any gate whose required external evidence is absent.

## Candidate and published-release boundary

A **candidate** is one exact reviewed source commit plus a deterministic sealed
archive and its SHA-256 digest. It may be copied to a controlled test location
and used for representative builds or target lifecycle qualification under the
applicable authorization. An expected tag name, a local tag, a reproducible
archive, or a `publishable` metadata bit does not make it a consumable product
release. Consumers must not pin or release against a candidate.

A **published module release** is the same exact candidate only after every
module-publication prerequisite has passed, the reviewed tag and artifacts
have been published under Gate F authority, every public artifact has been
downloaded into a fresh location, and its outer and inner identities have been
verified. Publication remains unconfirmed if the post-download verification is
missing or fails. A changed byte requires a new candidate and version; a
published artifact is never replaced under the same tag.

## Machine-readable gate contract

`release/release-integration-gates-v1.json` is authoritative for ordering,
prerequisites, evidence, claim ceilings, and repository ownership. Gates are
strictly ordered:

1. freeze one candidate by exact commit, archive name, archive SHA-256, UAPI
   identity, overlay hashes, compatibility-manifest hash, and expected tag;
2. pass the full offline suite twice against the exact candidate;
3. pass every row of the representative lifecycle matrix with independent,
   sealed evidence;
4. close independent adversarial review;
5. reproduce the release archive and generated overlays independently and
   compare bytes;
6. prove the tag matches every internal version and release identity;
7. verify checksums after downloading every published artifact into a new
   location;
8. populate the real compatibility manifest with exact identities, evidence,
   states, reasons, and truthful live eligibility;
9. verify install, rollback, recovery, and complete-removal instructions from
   the candidate artifacts;
10. document known limitations and audit every claim against evidence; and
11. confirm module publication only after all preceding gates pass.

No `module-published` result may be inferred from a local tag, GitHub-generated
source archive, draft release, upload success, checksum file alone, or a
candidate tested by a consuming repository. Gate evidence is immutable and
names the exact candidate. A source or generated-artifact change invalidates
every affected downstream gate.

## Module publication gate

The module publication gate requires all of the following with no waiver by a
green subset:

- all offline checks passing twice;
- the complete representative lifecycle matrix passing;
- independent adversarial review closed;
- release archive and DTBOs independently reproduced byte-for-byte;
- the published tag matching module metadata, DKMS version, archive root and
  name, release metadata, notes, and compatibility identity;
- checksums verified after a fresh public download, including every inner
  checksum and provenance relationship;
- a real, populated compatibility manifest whose claims do not exceed its
  exact build, lifecycle, cleanup, route, mode, and calibrated evidence;
- install, rollback, recovery, and complete-removal instructions verified from
  the candidate artifact, including residue checks;
- known limitations and explicit exclusions documented; and
- no compatibility, qualification, security, coexistence, timing, RF, route,
  kernel, or application claim broader than the evidence.

If any item is missing, failed, stale, or indeterminate, the identity remains a
candidate and is not consumable. Record the exact blocker; do not substitute a
plan, old evidence, or another candidate.

## Dependent integration and release ordering

Only after the module release is published and independently verified may the
following separately authorized work begin:

1. `WSPR-Transmitter` consumes the published canonical UAPI and exact module
   release, never a moving branch or local candidate.
2. Cross-repository byte checks and semantic ABI checks pass for the header,
   ioctls, structures, offsets, enums, flags, routes, capabilities, states,
   reasons, limits, and fail-closed behavior.
3. `WsprryPi` pins the exact module tag, downloaded archive checksum, UAPI
   identity, and compatibility-manifest identity plus the reviewed adapter
   identity.
4. Application integration qualification runs under its own authorization and
   exact identities; adapter tests or module qualification do not substitute
   for product scheduling, mode, cleanup, or RF evidence.
5. Dependent releases are reviewed and published in order: module, adapter,
   then application.

Each repository retains separate branches, worktrees, commits, reviews, tags,
releases, and qualification claims. Failure in a consumer cannot select
`/dev/mem`, a custom kernel, or another physical backend.

## Offline implementation and validation

Install the machine-readable gate contract as a package-owned release
artifact. Add a deterministic validator that rejects reordered, missing,
duplicate, or extra gates; incomplete evidence requirements; publication
before public-download verification; integration before confirmed module
publication; candidate-as-release wording; absent byte and semantic UAPI
checks; missing exact pins or compatibility manifest; dependent release order
violations; and claims without a declared evidence ceiling.

The validator must report current repository facts truthfully: the
`0.0.0-phase5.2` identity is a non-published candidate, representative target
lifecycle results are absent, post-download verification is absent, the
current historical compatibility entries remain `Unavailable` and non-live,
and all dependent integration/release gates remain blocked. This status is a
gate snapshot, not release evidence.

Run SPDX, whitespace, documentation links, release validation, and the complete
offline suite twice. Then independently attempt to falsify candidate/release
separation, prerequisite completeness, evidence freshness, download
verification, manifest truthfulness, integration ordering, exact pinning,
cross-repository UAPI equivalence, claim ceilings, and authorization scope.
Reinject every objective finding into this prompt, the machine-readable
contract, tests, or governing contract and repeat affected checks until none
remain.

### Reinjected findings

1. A checksum verified only before upload does not prove the public artifact.
   Require a fresh download location, outer digest verification, extraction to
   another path, and verification of every inner checksum and provenance link.
2. A tag can match the visible release string while pointing at different
   bytes. Bind the tag to the exact candidate commit and require all internal
   version, archive, UAPI, overlay, manifest, and note identities to agree.
3. A populated manifest can still overclaim. Require every non-default state,
   route, mode, and live flag to cite exact evidence and enforce the applicable
   compatibility-state ceiling.
4. "Module published" can be ambiguous after an upload failure or draft
   release. Require both publication completion and successful post-download
   verification before consumers may proceed.
5. Cross-repository checks can pass while a consumer pins a different archive.
   Require canonical UAPI byte and semantic checks plus the exact downloaded
   module tag, archive digest, manifest digest, and adapter identity.

All findings were reinjected. The final adversarial pass must find no remaining
objective issue within this offline slice before it closes.

## Completion report

Report changed files, exact checks and skips, current gate status and blockers,
all target/system/hardware/RF/publication/consumer actions not performed,
licensing/UAPI/schema/documentation impact, final Git state, and the next
separately authorized gate. Do not report the module published, a consumer
integrated, a dependent release ready, or Phase 5 complete without the exact
external evidence required above.
