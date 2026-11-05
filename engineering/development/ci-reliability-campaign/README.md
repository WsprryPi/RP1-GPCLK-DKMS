<!-- SPDX-License-Identifier: MIT -->

# CI reliability and efficiency campaign

This active plan selects eleven bounded phases for RP1-GPCLK-DKMS.
The eleven phases are selected for sequential execution under the current session authority.
Execution remains subject to the campaign safety boundaries and standing no-CI instruction.

Read the [campaign contract](campaign-contract.md) before selecting a phase.
Reliability, safety, required coverage, and defect detection take priority over
speed and maintenance reductions. There is no promised overall 50 percent saving.
Whole-harness orchestration allocation remains unresolved; establish complete
current accounting before claiming savings.

## Phase list

Status: ✅ done, ⏳ in progress, and ▧ not started. Dependencies follow the
campaign contract's accepted-prerequisite rule, including honest no-change/HOLD
dispositions for optional optimizations. A failed required reliability gate cannot
be accepted as a successful disposition.

| Phase | Batch | Saved prompt | Implementation |
| --- | --- | --- | --- |
| 01 | Trustworthy lifecycle execution | Require complete attributable lifecycle results | ✅ Done |
| 02 | Trustworthy lifecycle execution | [Retain process and container ownership through cleanup](phase-02-owned-cleanup-and-cancellation.md) | ⏳ In progress |
| 03 | Trustworthy lifecycle execution | [Bound provisioning and preserve actionable diagnostics](phase-03-finite-budgets-and-diagnostics.md) | ▧ Not started |
| 04 | Coverage and deterministic evidence | [Prove required dispatch and nonempty execution](phase-04-dispatch-and-nonempty-discovery.md) | ▧ Not started |
| 05 | Coverage and deterministic evidence | [Replace brittle process timing with observed state](phase-05-state-based-process-tests.md) | ▧ Not started |
| 06 | Coverage and deterministic evidence | [Keep runtime bundle fixtures outside the checkout](phase-06-isolated-runtime-bundle-fixtures.md) | ▧ Not started |
| 07 | Coverage and deterministic evidence | [Map lifecycle obligations to actual execution](phase-07-lifecycle-obligation-attribution.md) | ▧ Not started |
| 08 | Coverage and deterministic evidence | [Strengthen production-sensitive assertions and resolve fixture holds](phase-08-production-sensitive-oracles.md) | ▧ Not started |
| 09 | Measured efficiency | [Measure and reduce repeated module metadata queries](phase-09-batched-module-metadata.md) | ▧ Not started |
| 10 | Measured efficiency | [Batch authenticated Git blob reads without weakening validation](phase-10-authenticated-git-batching.md) | ▧ Not started |
| 11 | Measured efficiency | [Establish integrated assurance and honest reduction verdicts](phase-11-integrated-acceptance-and-feasibility.md) | ▧ Not started |

## Cohesive execution order

Phases 01 through 03 establish trustworthy lifecycle results, owned cleanup,
finite execution budgets, and useful diagnostics. They retain serial scenarios
and all existing isolation and qualification boundaries.

Phases 04 through 08 close missing-dispatch and empty-discovery paths, improve
process synchronization, isolate generated fixtures, connect lifecycle obligations
to execution, and make behavioral claims match actual defect sensitivity.
New unique coverage is an added responsibility and cost.

Phases 09 and 10 measure two narrow optimization candidates: repeated module
metadata queries and authenticated Git blob reading. Preserve every field,
observation, trust boundary, and independent expected value. Accept or hold each
candidate on evidence; local launch-count gains do not establish whole-CI gains.

Phase 11 reconciles integrated assurance, remaining gates, and separate
code/file/process/time verdicts. Concurrency is a later, separately authorized
pilot only after serial assurance passes. Hosted CI and remote policy changes
remain unauthorized under the standing no-CI instruction.

## Selection and completion

Execute the selected phases in order. Reorient to actual source and preserve
unexpected user work at every entry. Report, update, and reprint this list after
each accepted phase; unresolved required gates remain visible.

Keep execution and adversarial-review results in chat. Update active planning
status only from actual accepted evidence. After completion, consolidate durable
technical content, repair references, and retire completed prompts under
[repository instructions](../../../AGENTS.md); do not create a completion archive.
Published tags/assets, canonical interfaces, qualification metadata, and recovery
resources retain their independent ownership and evidence requirements.
