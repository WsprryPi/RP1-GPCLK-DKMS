<!-- SPDX-License-Identifier: MIT -->

# Phase 5.10 representative-system matrix execution prompt

## Authority and exit condition

Execute only the bounded offline Phase 5.10 portion of
`phase5-packaging-operator-enablement-execution-prompt.md`. Repository changes,
matrix design, and deterministic validation are authorized. This slice does
not authorize access to a Pi, package or DKMS mutation, signing or key changes,
module or overlay administration, boot changes, reboot, GPIO, clock, DMA,
transmission, RF, tagging, release publication, or consuming-repository work.

Phase 5.10 closes when the representative classes are frozen before target
testing in a machine-readable contract; every row names the selection rule,
preconditions, failure injection, exact expected state and reason, live gate,
transaction result, cleanup result, retained-prior-version result, required
diagnostics, allowed changes, final state, and residue audit; invalid or
incomplete rows fail validation; the complete offline suite passes twice; and
a separate adversarial assessment has no finding. Phase 5.10 does not execute
or close the representative target lifecycle gate.

## Matrix contract

`release/representative-system-matrix-v1.json` is the authoritative predeclared
matrix. Its row identifiers and meanings are stable evidence keys. A target
attempt must bind one row to one exact sealed candidate, evidence directory,
system identity, authorization, deadline, and baseline before mutation. One
attempt cannot satisfy another row, signing policy, kernel, route, or system.

The required rows are:

1. current supported Raspberry Pi OS kernel;
2. prior supported kernel used for downgrade;
3. newer unknown kernel and compatibility demotion;
4. module signing not enforced;
5. signing enforced with an enrolled local key;
6. deliberately failed build;
7. deliberately rejected signature;
8. missing headers;
9. conflicting overlay or resource;
10. interrupted upgrade;
11. stale compatibility manifest;
12. corrupted source archive or DTBO;
13. complete removal while inactive;
14. attempted removal while open or active; and
15. reinstall after complete removal.

Every row is output-disabled and deny-by-default. `Qualified` and live
eligibility are forbidden matrix outcomes. A successful build or lifecycle can
produce at most `Compatible-unqualified`; missing prerequisites are
`Unavailable`; known conflicts, signature rejection, corrupted identity,
stale policy, or unsafe removal are `Rejected`. An interrupted transaction is
inactive and recovery-required until its exact recovery and residue audits
pass. Cleanup ambiguity or an unexplained delta fails the row and latches the
applicable rejection state.

The prior complete version is retained only where a predecessor exists and the
transaction contract requires it. Rows without a predecessor say
`not-applicable`; they may not use an empty or inferred value. A rejected
operation must make no prohibited change. Removal tests preserve shared and
administrator-owned keys, configuration, and unrelated files.

## Evidence and execution rules

Before each future target attempt, copy the row unchanged into a new evidence
record and add the exact model/revision, kernel and headers, architecture,
compiler, firmware/DT, signing enforcement and trust identity, source/archive,
UAPI, DTBO and manifest hashes, baseline, commands, authorization, UTC and
monotonic bounds, and expected final hashes. Preserve failed attempts.

After execution record bounded stdout/stderr, exit status, scoped kernel-log
delta, diagnostics state/reason, transaction checkpoint, cleanup proof,
predecessor proof, final state, every allowed delta, every unexplained delta,
and residue results. A row passes only when all declared expectations are met;
`unknown`, missing evidence, extra residue, or an unclassified diagnostic is a
failure. Never generalize a passing row to another identity.

## Offline implementation and validation

Install the matrix contract as a package-owned release artifact. Add a
deterministic validator that rejects missing, extra, duplicate, or reordered
rows; missing required fields; forbidden live or `Qualified` outcomes;
inconsistent state/reason/result combinations; ambiguous cleanup; and absent
diagnostic or residue assertions. Exercise every negative rule without running
system commands.

Run SPDX, whitespace, documentation links, release validation, and the complete
offline suite twice. Then independently attempt to falsify representative
coverage, row independence, expected-state precision, predecessor retention,
diagnostic sufficiency, residue completeness, fail-closed behavior, and the
offline/target authorization boundary. Reinject every objective finding into
this prompt, the matrix, tests, or governing contracts and repeat affected
checks until none remain.

### Reinjected findings

1. A matrix can look complete while leaving success rows unable to detect an
   unexpected cleanup latch. Require every row's diagnostics to include the
   cleanup latch and require the residue audit to classify unexplained deltas.
2. Corruption is not one interchangeable condition. Require the corrupted-
   artifact row to test the source archive and each route-specific DTBO as
   separate attempts under the same stable row contract.
3. Reinstall-after-removal can conceal retained state. Require a proved empty
   package-owned baseline before reinstall and a second complete-removal audit
   after the reinstall attempt.
4. The governing prompt requires a predeclared deadline and evidence identity
   for each row, but the first matrix represented them only as execution
   instructions. Add both as mandatory per-row fields and reject semantically
   incorrect compatibility-state assignments, not merely invalid vocabulary.

All findings were reinjected and affected checks repeated. The final
adversarial pass found no remaining objective issue within this offline slice.

## Completion report

Report changed files, exact checks and skips, target/system/hardware/RF and
publication actions not performed, licensing/UAPI impact, remaining target
execution, Git state, and the next separately authorized gate. Do not report
the packaging gate or Phase 5 complete.
