<!-- SPDX-License-Identifier: MIT -->

# Phase 02 Retain process and container ownership through cleanup

## Selection and prerequisites

This is an execution prompt for selected unfinished work, not a completion record.
Authoring or committing it does not execute the phase.
Prerequisites: Phase 01 accepted.
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

1. Trace launch, output draining, child exit, timeout, signals, cancellation, container identification, and cleanup ownership before changing control flow.

2. Handle Docker --rm explicitly: verified absence of this run's container is success; permission/daemon/query errors and unknown state are not proof of absence. Do not treat every nonzero docker rm as failure or ignore every one.

3. Validate the cidfile as bounded run-owned data. Never remove a container merely because an untrusted/stale file names it; retain an attributable launch label or equivalent ownership proof.

4. Preserve the initiating failure and record cleanup failures separately. Cleanup failure after otherwise successful work must block acceptance. Never convert cancellation into PASS.

5. Place package_lock child release, bounded output collection, and reaping under exception-safe ownership. Release the fixture hold on every path, including failed synchronization, already-exited children, and interrupted communicate.

6. Use finite escalation only for owned processes/containers. Do not infer that killing userspace proves kernel or host effects stopped; preserve all existing container restrictions.

## Verification and adversarial loop

Before editing, map each changed behavior to its current oracle and execution
context. Define correct behavior and deliberate defects, plus the smallest
meaningful regressions. Do not replace a real integration boundary with mocks.
When old efficacy is absent, identify the gap instead of inventing old sensitivity.

Use these phase-specific challenges in addition to the campaign-wide gates:

- Auto-removed container is already absent versus Docker is unavailable or refuses inspection/removal.
- A stale or substituted cidfile names an unrelated container; launch fails before the cidfile exists.
- Primary scenario failure is followed by cleanup failure, or successful scenario work is followed by cleanup failure.
- Cancellation occurs before launch, during lock synchronization, during output draining, and during cleanup; a descendant retains a pipe.

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

Owned resources reach verified terminal/absent states or produce explicit unresolved cleanup failure; unrelated resources remain untouched and the primary diagnostic survives.

All required coverage, safety, identity, failure propagation, and cleanup gates
take priority over speed. A local improvement cannot compensate for a lost
required defect or context. Do not proceed automatically to the next phase.

## Net budget and evidence

Charge ownership verification, signal/cancellation handling, bounded output/reaping, regression helpers, and diagnostics. Do not book shorter watchdog failures as faster validation.

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
