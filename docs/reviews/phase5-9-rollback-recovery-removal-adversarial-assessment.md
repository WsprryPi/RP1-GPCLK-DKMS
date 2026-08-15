<!-- SPDX-License-Identifier: MIT -->

# Phase 5.9 rollback, recovery, and complete-removal adversarial assessment

## Scope

This assessment challenges the offline Phase 5.9 contract, pure policy tool,
release inventory, installation integration, operator guidance, and tests. It
does not claim target lifecycle qualification.

## Findings and reinjection

1. **Initial package inventory gap.** The first implementation defined the
   contract and evaluator but did not install them as release-owned artifacts.
   The release layout, installation model, installer fixture, and installation
   tests now include both artifacts.
2. **Initial operator-surface gap.** Pure functions alone did not provide a
   reviewable operator invocation. The policy now exposes three explicitly
   read-only JSON commands and rejects symlink snapshots.
3. **Potential truthiness bypass.** Python truthy values could otherwise stand
   in for known booleans. Every safety and acceptance field now requires exact
   `bool` type, and missing, extra, `null`, open, active, latched, changed, or
   unclassified evidence is rejected by tests.

## Final falsification pass

The final pass attempted to conflate rollback with recovery, accept a same-
version predecessor, resume an unknown checkpoint, clear a cleanup latch,
accept live or unknown output state, omit an acceptance assertion, preserve
exclusive package keys, delete shared keys, overlook module/build/overlay/
policy residue, or dispatch a mutating command from the policy tool. No
remaining objective finding was identified within the authorized offline
scope.

Representative-target rollback, interrupted-operation recovery, initramfs and
dependency regeneration, key-ownership removal, and full residue audits remain
separate Gate D validation and are not inferred from these tests.
