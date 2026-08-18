<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 qualification-only successor freeze prompt

## Objective

Freeze one qualification-only successor for the final installed Phase 5.53
product without rebuilding, reinstalling, or changing that product.

## Fixed identities

- Product source: `4e7a64a0ca353d2fcab6e25891f5254746e2b91a`.
- Product archive SHA-256:
  `032a0ca214427ebb6115b933042e7135f03c2ed6ce4f5c399686b2cf61395a76`.
- Prior qualification archive SHA-256:
  `a60a23378f1ae07b0fb7566f73af82a13f0453196bfa1a8553c91a987dd0486e`.

## Required execution

1. Verify the branch, clean worktree, upstream, frozen release-unit checksums,
   product archive hash, and source identity.
2. Update the successor builder and validator to accept only the final product
   archive hash; reject the retired product identity.
3. Reconcile the active gate graph before freezing because it is a
   qualification-archive input. Keep the successor hash in repo-only external
   evidence rather than creating a self-referential archive identity.
4. Commit that exact qualification source closure.
5. Generate two qualification-only successor release units independently from
   the same clean commit and frozen release unit.
6. Prove complete release-directory byte identity, unchanged product artifacts,
   identical qualification archives, safe sorted inventory, deterministic
   metadata, complete checksums, and exact source bytes.
7. Run one complete offline regression suite from the clean qualification
   source commit.
8. Record repo-only evidence and an adversarial review without altering any
   qualification-archive input. Commit and push them separately.

## Safety and non-goals

Do not access `wspr5`; install, remove, load, bind, or unload a module; apply an
overlay; reboot; activate GPIO, clock, or DMA; transmit; or produce RF. Do not
regenerate or reinstall the product archive. Do not generate lifecycle controls
or execute the final `offline-checks-twice` gate in this slice.

## Adversarial review and exit

Reject any product-byte change, dirty-source successor, nondeterminism,
incomplete archive closure, stale product allowlist, path-bearing consumer not
derived from the successor closure, self-referential identity, or over-broad
claim. Exit only with two byte-identical independently validated successor
units, one passing full offline suite, durable external evidence, a clean pushed
branch, and `offline-checks-twice` as the single next gate.
