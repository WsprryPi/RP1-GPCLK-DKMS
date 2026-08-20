<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 complete staging-builder repair prompt

## Objective

Replace the overstated split-staging rehearsal with one shared, offline
transport builder that reconstructs every staged path from its declared owner.
The same builder output, after a future authorization, must be the only archive
eligible for target transfer.

## Required repair

1. Classify every envelope input as a release-directory artifact, a
   repository control-set file, or a product-archive member. Reject unowned or
   multiply owned paths.
2. Extract the complete product archive using regular-file and directory
   members only. Reject traversal, links, special files, duplicates, or an
   unexpected archive root.
3. Materialize all 64 declared inputs, all 54 product members, and the
   separately sealed envelope. Hash every declared input after construction.
4. Emit a normalized ustar containing exactly the 118-file union and a source
   map recording the owner and source of every file.
5. Make the exact split-staging test call this builder. With no frozen release
   directory it must report SKIP, never PASS. With the exact product and
   qualification archives it must extract the complete ustar, verify all
   member bytes, and invoke the archived pre-root entry point from that tree.
6. Exercise the repair against the retained Phase 5.53 release directory,
   then run the complete offline suite and a separate adversarial review.

## Constraints

Do not regenerate the control set, modify either release archive, contact a
target, transfer files, install anything, perform the pre-root transition, or
begin a lifecycle attempt. Preserve the retired target authorization and stop
after the offline repair, review, commit, and push.

## Exit criteria

The exact integration test must prove that all 118 files were materialized by
the shared builder, that the source map has no unowned path, and that the
archived entry point succeeds against the complete extracted transport. A
deterministic hash, closure-set calculation, or structural envelope validation
alone is insufficient.
