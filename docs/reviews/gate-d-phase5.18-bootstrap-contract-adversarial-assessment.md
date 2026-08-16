<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.18 bootstrap-contract adversarial assessment

Status: offline software review passed; candidate freeze pending

The review covers the closed bootstrap schema, target-plan and instance hash
bindings, literal dispatch, journals, retained-tool identities, empty inactive
baselines, cleanup ownership, interruption, and recovery. Target evidence is
out of scope.

## Findings closed

1. The first draft invoked the administrator at its not-yet-installed
   destination. The final plan binds a distinct staged bootstrap path, source
   hash, installed path, and installed hash; literal argv invokes the staged
   source through `/usr/bin/python3`.
2. Installation alone leaves the candidate registered and installed. A
   separate literal `cleanupArgv` and durable `cleanup-runtime` checkpoint now
   precede retained-tool and empty-runtime verification.
3. The target plan now has schema version 3 with an exact subordinate-plan
   path and digest. The execution instance has schema version 2 with the same
   independent binding.
4. The permanent outer executor has a closed `bootstrap` action and uses the
   same atomic journal and recovery-required semantics without accepting shell
   programs.
5. Stateful tests cover exact success, missing retained tools, changed and
   swapped identities, malformed argv, prohibited safety changes, unsafe
   cleanup paths, symlinked identity input, interrupted installation,
   recovery dispatch, cleanup failure, and retained residue.
6. The first schema-3 draft did not require the bootstrap executor in the
   target-plan tooling set and inherited an exact schema-2 conditional. Schema
   3 now binds that source and installed identity and validates the subordinate
   bootstrap document, not merely its digest.
7. The cleanup vector originally allowed unbound middle arguments. The plan
   now binds the predecessor, successor, kernel, and staging directory and
   accepts only the corresponding exact literal command.
8. Recovery originally invoked the installed administrator, which might not
   exist after an early interrupted install. Recovery now invokes the sealed
   staged administrator, and the empty-baseline checkpoint rejects every
   declared cleanup path that remains.
9. Bootstrap execution originally accepted a standalone valid plan. Mutating
   dispatch now requires the ready execution instance and verifies that the
   instance, target plan, subordinate plan path, and subordinate plan digest
   are identical.

The complete offline suite passed twice after the final corrections. No target
was contacted or changed.
