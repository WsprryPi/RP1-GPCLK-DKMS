<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 qualification-only successor repair prompt

## Objective

Repair the frozen qualification-tooling limitation that rejected the eighth
`qualificationArchive` release input, and provide deterministic construction
of an unpublished qualification-only successor without regenerating or
changing the frozen DKMS product archive.

## Verified starting point

- The frozen product archive SHA-256 is
  `ae6df3a66a9a26a6fb8474e5896c9053b9f69580d8c45383a5556fc397ebb549`.
- The frozen qualification archive cannot express an eighth pre-root input;
  its validator supports seven roles through schema 5.
- Historical schema-1 through schema-5 controls remain durable evidence and
  must continue to validate without modification.
- The candidate has not been published, so a qualification-only successor is
  permitted by `release/artifact-scoped-invalidation-policy-v1.json`.

## Required implementation

1. Extend the pre-root envelope and validator additively with schema 6.
   Schema 6 inherits the schema-5 lifecycle, package-path, predecessor, and
   snapshot requirements and requires exactly eight release-input roles:
   the existing seven plus `qualificationArchive`. The qualification archive
   name must be derived from the candidate release. Schema 2 through 5 must
   still require exactly their historical seven-role graph.
2. Validate all eight schema-6 files as regular, non-symlinked, hash-bound
   inputs in one administrator release directory. `SHA256SUMS` must cover
   exactly the other seven files, including both archives, with no duplicate,
   missing, extra, stale, or renamed entry.
3. Add deterministic offline tests for schema-6 acceptance and for missing,
   duplicate, stale, wrong-name, wrong-directory, and unchecksummed
   qualification archives. Retain historical schema-2 execution tests.
4. Provide a qualification-successor generator that consumes an independently
   verified frozen release unit, copies product artifacts byte-for-byte,
   generates only the qualification archive from the exact current source
   commit, and renews metadata, provenance, and checksums. It must fail closed
   for a dirty source, unsafe output, mismatched frozen product identity,
   malformed frozen release unit, or any product artifact byte change.
5. Independently validate two generated successors for byte equality,
   qualification inventory and metadata, product identity retention, renewed
   qualification source identity, and complete checksum/provenance binding.

## Constraints and non-goals

Do not alter historical evidence or generated controls. Do not change release
gate status, generate a Phase 5.53 control set, stage target inputs, connect to
a target, request or consume authorization, install or administer DKMS,
modules, overlays, services, or boot state, access GPIO/I2C, enable a clock,
submit DMA, use SDR or Si5351 hardware, connect an antenna, transmit, or
produce RF. This slice repairs and proves offline successor construction only.

## Validation and exit criteria

Run focused positive and adversarial tests, packaging and schema validation,
documentation links, whitespace checks, and one complete offline regression
suite. Compare the copied product archive, UAPI/DTBO sidecars, compatibility
manifest, and retained product identities byte-for-byte with the frozen unit.
Reinject every actionable failure and repeat affected checks. Exit only with a
clean scoped diff, no product archive regeneration, and no claim beyond an
offline-valid qualification successor mechanism.
