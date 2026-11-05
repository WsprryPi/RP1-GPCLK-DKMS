<!-- SPDX-License-Identifier: MIT -->

# Phase 09 Measure and reduce repeated module metadata queries

## Selection and prerequisites

This is an execution prompt for selected unfinished work, not a completion record.
Authoring or committing it does not execute the phase.
Prerequisites: Phases 01 through 08 accepted.
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

- `tests/package_lifecycle_linux.py`
- `tests/check_package_lifecycle.py`
- `scripts/package_signatures.py`
- `scripts/package_preflight.py`

Inspect actual callers, imported/lazy dispatch, production consumers within this
repository, and directly used fixtures. Preserve all existing user work.
Do not inspect or modify sibling repositories.

## Objective and bounded work

1. Measure the current snapshot query path in the same isolated environment before changing it. Count explicit queries separately from decompression, signature verification, compilation, and total scenario work.

2. Pilot one validated modinfo invocation per module instead of separate field invocations; preserve version, signer, key, signature algorithm/hash, interlock, dependency, alias, and vermagic meaning.

3. Define parsing for repeated/multiline fields, valid absent optional fields, missing mandatory fields, nonzero exits, malformed/oversized output, compression formats, and module drift.

4. Preserve real cryptographic verification and every before/after snapshot; fewer observations or weaker field checks are not efficiency savings.

5. Compare actual snapshot identities and scenario outcomes against the old path, then retire only equivalent query orchestration after sensitivity gates pass.

6. Report local launch reductions separately from whole-job elapsed savings. Do not promise that the historical nine-to-one query opportunity produces an overall 50 percent gain.

## Verification and adversarial loop

Before editing, map each changed behavior to its current oracle and execution
context. Define correct behavior and deliberate defects, plus the smallest
meaningful regressions. Do not replace a real integration boundary with mocks.
When old efficacy is absent, identify the gap instead of inventing old sensitivity.

Use these phase-specific challenges in addition to the campaign-wide gates:

- modinfo returns plausible stdout with nonzero status, missing required identity, duplicate contradictory fields, or truncated output.
- An unsigned module legitimately lacks optional signing fields; parser must not reject it by confusing absence with corruption.
- A compressed or substituted module changes between identity checks; crypto verification is silently replaced by metadata.
- A faster result comes from dropping snapshot frequency, header contexts, or signature operations.

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

Equivalent or stronger identity/failure detection with measured local process savings; global runtime benefit remains explicitly measured or unknown.

All required coverage, safety, identity, failure propagation, and cleanup gates
take priority over speed. A local improvement cannot compensate for a lost
required defect or context. Do not proceed automatically to the next phase.

## Net budget and evidence

Charge parser/helpers, differential and fault regressions, instrumentation, and all companion changes. No runtime saving is booked from launch counts alone.

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
