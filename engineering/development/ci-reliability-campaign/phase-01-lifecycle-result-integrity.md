<!-- SPDX-License-Identifier: MIT -->

# Phase 01 Require complete attributable lifecycle results

## Selection and prerequisites

This is an execution prompt for selected unfinished work, not a completion record.
Authoring or committing it does not execute the phase.
Prerequisites: None; begin with current-source orientation.
Apply the accepted no-change/HOLD rule in the
[campaign contract](campaign-contract.md) for optional optimizations.

## Required orientation

Read the complete [campaign contract](campaign-contract.md),
[repository instructions](../../../AGENTS.md), and
[module contract](../../contracts/rp1-gpclk-dkms-module-contract.md).
Reinspect the current branch/worktree, staged/unstaged/untracked state, exact
source identity, relevant history, and owning contracts before acting.
Do not assume the authoring revision or previous audit is still current.
Current code owners to inspect recursively:

- `tools/run-package-lifecycle.py`
- `tests/package_lifecycle_linux.py`
- `tests/check_package_lifecycle.py`

Inspect actual callers, imported/lazy dispatch, production consumers within this
repository, and directly used fixtures. Preserve all existing user work.
Do not inspect or modify sibling repositories.

## Objective and bounded work

1. Define a closed, bounded scenario-result envelope shared by the container producer and host consumer. Inspect the existing result.json and environment.json before choosing additions; bind the requested scenario, exact source, candidate/predecessor digests, and image/run identity without inventing unavailable provenance.

2. Require a nonempty requested scenario set and exactly one terminal result for each requested scenario. Support an explicitly requested single scenario without pretending it is full lifecycle acceptance.

3. Make host aggregation reject missing, malformed, duplicate-key, truncated, oversized, stale, duplicate, contradictory, wrong-scenario, and wrong-source results, even when the container exits zero. Distinguish valid partial diagnostics from acceptance evidence.

4. Cross-check exit status, result status, completed work, and required safety declarations. Do not require every declared future matrix case to execute here; phase 07 owns the complete obligation map.

5. Ensure setup/dispatch failures produce attributable failure when possible; inability to write results must itself fail. Preserve all scenario behavior, real crypto, restricted capabilities/mounts, and output privacy.

6. Update the existing exit-only mocked driver regression to produce realistic results and prove result completeness, preserving its permission assertions.

7. Use strict schema/version/type checks, including Boolean-versus-integer distinctions. Generate a fresh run identity at the host and propagate it to each producer so matching source/artifact bytes alone cannot admit stale results.

## Verification and adversarial loop

Before editing, map each changed behavior to its current oracle and execution
context. Define correct behavior and deliberate defects, plus the smallest
meaningful regressions. Do not replace a real integration boundary with mocks.
When old efficacy is absent, identify the gap instead of inventing old sensitivity.

Use these phase-specific challenges in addition to the campaign-wide gates:

- A fake container exits zero and writes no result, an empty steps list, or a result copied from another scenario/source.
- The requested set is empty or contains duplicate scenario identities; one scenario is omitted or reported twice.
- Exit zero accompanies FAIL, nonzero accompanies PASS, or a result claims unsupported hardware/RF qualification.
- A result is a symlink/special file, contains duplicate JSON keys, exceeds its bound, or changes during the acceptance read.

Inspect every proposed command before running it. Begin with deterministic,
offline, unprivileged, hardware-free checks using attributable temporary output.
Use real subprocess/format boundaries where the obligation requires them.
Real container package/DKMS work, provisioning, and dependency installation need
separate effect-specific authorization. Do not run target or hardware operations.
Do not trigger hosted CI under the standing no-CI instruction.

Perform a separate adversarial assessment after the first implementation.
For every failed assertion, repair the affected work, reinject the deliberate
defect or relevant negative case, rerun affected checks, and assess again.
Test scheduling/load variation where relevant without retry-until-green.
Finite watchdogs cannot replace observed readiness or cleanup.
Keep primary failures and secondary cleanup errors distinguishable.

If a required context, authorization, dependency, or sensitivity experiment is
unavailable, report it as pending/failed with the exact next gate. Do not weaken
the test, replace it with a permissive stub, or mark this phase complete.

## Acceptance gate

Only a complete, coherent, attributable requested set can receive PASS; negative cases fail final aggregation. All existing scenarios and their independent evidence remain present.

All required coverage, safety, identity, failure propagation, and cleanup gates
take priority over speed. A local improvement cannot compensate for a lost
required defect or context. Do not proceed automatically to the next phase.

## Net budget and evidence

Charge the producer/consumer contract, bounded reader/parser, identity propagation, regression fixtures, documentation, and any helper. No reduction target applies to this reliability addition.

Freeze complete comparable before quantities and charge every replacement/helper,
regression, relocation, companion edit, new dependency, and added unique case.
Keep code, files, processes, compiler/linker invocations, contexts, and elapsed
time separate. Do not invent precise replacement allowances. A 50 percent
finding may be unsupported or not estimable. Preserve first-attempt failures,
rerun costs, queue delay, cold/warm conditions, and overlapping spans separately.
Save temporary measurement output outside every checkout; report results in chat.

## Handoff and Git boundary

Report changed files/behavior, exact checks and results, sensitivity evidence,
unavailable contexts, source/artifact/environment identities, net costs/savings,
risks, licensing/documentation impact, and the next gated step.
Explicitly state hardware/system/GPIO/transmission/RF effects and Git state.
Keep run logs, review findings, and completion reports out of the repository.

The present request authorizes commits/pushes of these planning documents only.
Later implementation commits/pushes require their own authorization and must
honor the no-CI instruction. Do not merge, rebase, force-push, tag, publish,
create a PR, change remote settings, or retire other work.
After later completion, consolidate durable content and retire this prompt
with repaired references under the repository's active-prompt lifecycle rule.
