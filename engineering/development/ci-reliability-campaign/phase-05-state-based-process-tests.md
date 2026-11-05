<!-- SPDX-License-Identifier: MIT -->

# Phase 05 Replace brittle process timing with observed state

## Selection and prerequisites

This is an execution prompt for selected unfinished work, not a completion record.
Authoring or committing it does not execute the phase.
Prerequisites: Phase 04 accepted.
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

- `tests/check_runtime_inventory.py`
- `tests/check_runtime_controller.py`
- `scripts/runtime_inventory.py`
- `scripts/runtime_controller_admin.py`
- `scripts/runtime_route_client.py`
- `scripts/runtime_application.py`

Inspect actual callers, imported/lazy dispatch, production consumers within this
repository, and directly used fixtures. Preserve all existing user work.
Do not inspect or modify sibling repositories.

## Objective and bounded work

1. Review actual timeout, EOF, output-limit, lock, acknowledgement, and direct-child ownership contracts before choosing fixtures. Production files are inspection boundaries; change production behavior only for a demonstrated defect within this phase's reviewed scope.

2. Replace reliance on the 100 ms timeout and two-second elapsed assertion with explicit child-state evidence and generous finite guards. A child that never reached its intended state must not validate the timeout path.

3. Use deterministic controlled-clock/selector cases where useful, while retaining real subprocess integration for output, exit, and timeout boundaries. Do not replace all real runner behavior with mocks.

4. Exercise partial I/O, EOF before exit, early/already-exited children, output bounds, nonzero exits, cancellation, descendants retaining descriptors, and secondary cleanup failure.

5. Review per-operation socket timeout versus overall transaction budget and nested service acknowledgement budgets. Preserve real boot/token/PID/service/output readiness checks and product timing.

6. Do not create a shared process abstraction unless explicit contracts and failure sensitivity justify it. Unresolved production behavior remains a documented hold, not an inferred repair.

## Verification and adversarial loop

Before editing, map each changed behavior to its current oracle and execution
context. Define correct behavior and deliberate defects, plus the smallest
meaningful regressions. Do not replace a real integration boundary with mocks.
When old efficacy is absent, identify the gap instead of inventing old sensitivity.

Use these phase-specific challenges in addition to the campaign-wide gates:

- Child startup is delayed, child exits before readiness, or it publishes readiness and then blocks.
- EOF occurs before child exit, a descendant retains stdout, or output arrives in fragments.
- A fake runner reports timeout without starting the intended child; a clock jump or repeated read defeats the overall budget.
- Acknowledged process/PID changes before terminal service acceptance; cleanup failure hides the primary error.

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

Tests distinguish readiness, timeout, exit, and cleanup under scheduling variation and detect deliberate defects; real timing and acknowledgement contracts remain intact.

All required coverage, safety, identity, failure propagation, and cleanup gates
take priority over speed. A local improvement cannot compensate for a lost
required defect or context. Do not proceed automatically to the next phase.

## Net budget and evidence

Charge synchronization fixtures, deterministic clock adapters, real-child cases, and any justified production repair. Repeated passing runs alone do not establish repair.

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
