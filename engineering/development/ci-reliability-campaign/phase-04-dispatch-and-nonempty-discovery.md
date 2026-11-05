<!-- SPDX-License-Identifier: MIT -->

# Phase 04 Prove required dispatch and nonempty execution

## Selection and prerequisites

This is an execution prompt for selected unfinished work, not a completion record.
Authoring or committing it does not execute the phase.
Prerequisites: Phases 01 through 03 accepted.
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

- `tests/check_test_inventory.py`
- `tests/run-offline-checks.sh`
- `Makefile`
- `.github/workflows/offline.yml`
- `.github/workflows/documentation.yml`
- `tests/test_documentation_config.py`
- `tests/test_documentation_images.py`

Inspect actual callers, imported/lazy dispatch, production consumers within this
repository, and directly used fixtures. Preserve all existing user work.
Do not inspect or modify sibling repositories.

## Objective and bounded work

1. Replace filename-substring registration with explicit ownership connected to actual dispatch and observed results. Do not introduce a second registry that can drift independently of the runner.

2. Require nonempty expected suites and nonempty discovery for unittest owners. Account for non-unittest programs with their own execution contract; do not force lexical assertion counts to become case counts.

3. Preserve standalone and subset entry points, the parameterized module validator, target-client classifications, both C planners, C/C++ compilation contexts, and Linux/Windows documentation contexts.

4. Keep separately invoked tests isolated where imports, global monkeypatches, or top-level execution require it. Do not bulk-import check_*.py to discover tests or merge processes merely to reduce launches.

5. Distinguish documented local optional tools/platform skips from required CI prerequisites. Missing required tools must fail; legitimate non-Linux cases remain explicitly classified.

6. Preserve every push/PR/tag context and Windows invalid-builder failure check. Do not change merge policy or add path filters, quarantine, scheduled-only, or nonblocking execution.

## Verification and adversarial loop

Before editing, map each changed behavior to its current oracle and execution
context. Define correct behavior and deliberate defects, plus the smallest
meaningful regressions. Do not replace a real integration boundary with mocks.
When old efficacy is absent, identify the gap instead of inventing old sensitivity.

Use these phase-specific challenges in addition to the campaign-wide gates:

- A filename remains only in a comment while its invocation is removed.
- Discovery returns zero, the expected registry is empty, or a test body is never dispatched.
- One planner/language/platform context is removed while a similarly named test remains.
- A required tool is unavailable; an unexpected skip or zero-exit empty suite is presented as full validation.

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

Every required owner has executable dispatch and attributable nonempty results; deliberate omissions fail. Independent entry points and platform distinctions remain usable.

All required coverage, safety, identity, failure propagation, and cleanup gates
take priority over speed. A local improvement cannot compensate for a lost
required defect or context. Do not proceed automatically to the next phase.

## Net budget and evidence

Charge registry/dispatch/result plumbing, all runner/Make/workflow companions, and regressions. New coverage is added responsibility, not a consolidation saving.

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
