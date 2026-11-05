<!-- SPDX-License-Identifier: MIT -->

# Phase 08 Strengthen production-sensitive assertions and resolve fixture holds

## Selection and prerequisites

This is an execution prompt for selected unfinished work, not a completion record.
Authoring or committing it does not execute the phase.
Prerequisites: Phase 07 accepted.
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

- `tests/check_route_uapi_contract.py`
- `tests/resource_policy.c`
- `tests/lifecycle_core.c`
- `tests/fixtures/runtime_controller_harness.c`
- `overlays/fixtures`
- `engineering/contracts/rp1-gpclk-dkms-module-contract.md`

Inspect actual callers, imported/lazy dispatch, production consumers within this
repository, and directly used fixtures. Preserve all existing user work.
Do not inspect or modify sibling repositories.

## Objective and bounded work

1. Classify each claimed behavioral check as actual implementation execution, independent model/vector, source-shape constraint, or self-contained demonstration.

2. Address the toy route ownership loop without pretending it previously caught a production defect. Link required ownership/refusal obligations to actual production-sensitive oracles.

3. Retain useful independent models and static safety boundaries; strengthen missing sensitivity rather than replacing all static checks or treating every model as redundant.

4. Use deliberate production defects to define future sensitivity evidence for ownership, no-write refusal, cleanup latches, stale generations, and lifetime boundaries without claiming host stubs prove kernel concurrency.

5. Resolve each of the eight overlay fixture holds individually from in-repository evidence and contracts. If an external owner cannot be established within scope, retain HOLD with precise missing evidence.

6. Do not delete fixtures, recovery resources, or provenance in this phase. Any later authorized retirement must follow the repository cleanup instructions; proven unused material receives zero reduction credit.

7. If an oracle exposes a module/kernel product defect, preserve the reproduction and propose a separately scoped repair. Do not fold kernel implementation changes into this harness/oracle phase.

## Verification and adversarial loop

Before editing, map each changed behavior to its current oracle and execution
context. Define correct behavior and deliberate defects, plus the smallest
meaningful regressions. Do not replace a real integration boundary with mocks.
When old efficacy is absent, identify the gap instead of inventing old sensitivity.

Use these phase-specific challenges in addition to the campaign-wide gates:

- A production ownership/refusal check is removed but the supposed behavioral test still passes.
- A golden expected value is replaced by a call to the implementation under test.
- A fixture is called unused solely because no named caller was found, despite generic discovery or possible target ownership.
- GPIO4 evidence is substituted for GPIO20, or a mocked lifetime model is presented as real kernel qualification.

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

Claims match actual oracle sensitivity; missing efficacy is explicit; every fixture has a retain/hold disposition without unqualified deletion.

All required coverage, safety, identity, failure propagation, and cleanup gates
take priority over speed. A local improvement cannot compensate for a lost
required defect or context. Do not proceed automatically to the next phase.

## Net budget and evidence

Charge every new oracle and activated case. Retiring demonstrations or unused fixtures cannot fund the orchestration target; do not erase protected independent evidence.

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
