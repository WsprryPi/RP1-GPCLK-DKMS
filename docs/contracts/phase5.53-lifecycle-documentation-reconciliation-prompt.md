<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 lifecycle and documentation reconciliation prompt

## Objective

Reconcile the active release roadmap to the final product candidate actually
installed inactive on `wspr5`. Preserve valid component-scoped evidence, retire
obsolete blockers and controls, and identify one linear path to the remaining
representative lifecycle gate.

## Exact context

- Product source: `4e7a64a0ca353d2fcab6e25891f5254746e2b91a`.
- Product archive SHA-256:
  `032a0ca214427ebb6115b933042e7135f03c2ed6ce4f5c399686b2cf61395a76`.
- Last frozen qualification archive SHA-256:
  `a60a23378f1ae07b0fb7566f73af82a13f0453196bfa1a8553c91a987dd0486e`.
- Target-install attestation commit: `da4d464e1bfa53d964147e5682e9901ffccc3f64`.
- Successor ledger SHA-256:
  `d4fe02f8d66ac298f2076b37be297097f392095904cc3809717713cd01a14f8d`.
- GPIO4 and GPIO20 DTBO SHA-256 identities remain respectively `c3e17a...`
  and `8eaa8a...` as recorded in the candidate and install attestations.

## Required work

1. Update only the active machine-readable release gate graph and repo-only
   reconciliation documentation. Do not change the product archive closure.
2. Record the inactive product installation as partial lifecycle evidence, not
   as completion of the representative lifecycle matrix.
3. Remove the resolved split pre-root input incompatibility from current
   blockers. Keep the affected old Gate D controls immutable and historical.
4. Require all new path-bearing controls to be reconstructed from the final
   product and successor qualification closures; do not patch old controls.
5. Apply the artifact-scoped invalidation policy: retain the final product
   archive, ordinary-install, representative-build, UAPI, module, and DTBO
   evidence; require a qualification-only successor, one final split-candidate
   offline-checks-twice gate, then new exact-identity lifecycle controls.
6. Correct any offline regression whose result improperly depends on ambient
   worktree dirtiness.

## Non-goals and safety boundary

Do not access or mutate `wspr5`; install, remove, load, bind, or unload a module;
apply an overlay; reboot; activate GPIO, clock, or DMA; transmit; or produce RF.
Do not regenerate the product archive. Do not rewrite historical evidence.

## Validation and adversarial review

Validate JSON syntax and the release-gate contract, run the qualification
successor regression in both the current ambient state and the full offline
suite, inspect the complete diff, and challenge every retained or invalidated
claim against `release/artifact-scoped-invalidation-policy-v1.json`. Reinject
and correct every actionable finding before exit.

## Exit criteria

The active roadmap names the installed final candidate, obsolete blockers are
gone, incomplete gates remain blocked, the installed state is not overstated,
the product closure is untouched, and the next work is a qualification-only
successor followed by the final split-candidate offline gate—not another
product build or installation.
