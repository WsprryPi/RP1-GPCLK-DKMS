<!-- SPDX-License-Identifier: MIT -->

# Phase 10 Batch authenticated Git blob reads without weakening validation

## Selection and prerequisites

This is an execution prompt for selected unfinished work, not a completion record.
Authoring or committing it does not execute the phase.
Prerequisites: Phase 09 accepted.
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

- `scripts/release_contract.py`
- `scripts/build-release-candidate`
- `scripts/validate-release-candidate`
- `scripts/build-lifecycle-predecessor`
- `tests/check_release_candidate.py`

Inspect actual callers, imported/lazy dispatch, production consumers within this
repository, and directly used fixtures. Preserve all existing user work.
Do not inspect or modify sibling repositories.

## Objective and bounded work

1. Measure current source enumeration against the exact selected tree and environment. Treat each builder, validator, and predecessor enumeration as a separate required trust context.

2. Pilot bounded git cat-file batch reading with strict object identity/type/length framing, complete reads, EOF/exit/deadline handling, and exact path/mode/byte reconstruction.

3. Preserve full-commit selection, no replacement objects, safe Git environment, unsafe path/mode rejection, source limits, private-key rejection, dirty/index-hidden checks, and independent expected values.

4. Keep builder metadata generation separate from independent validation. Retain fresh reproducibility builds, poisoned-cache/environment regressions, candidate/release distinctions, and validation of final copied output.

5. Do not reuse builder caches as the validator's source of truth or collapse replay tests merely because their outputs match. H2 replay consolidation remains HOLD unless separately justified.

6. Report per-enumeration launch savings, production-tool maintenance cost, regressions, and measured elapsed contribution separately. Rebuild only disposable candidates if separately authorized; never alter published tags or assets.

7. Identical blobs legitimately referenced by multiple paths remain valid. Reject unexpected duplicate responses or framing/count mismatches without rejecting legitimate repeated requested object IDs.

8. Exercise valid repeated blob IDs for different paths as a positive case alongside invalid extra/missing replies. Compare source maps against independent Git object expectations, not only two calls to the replacement parser.

## Verification and adversarial loop

Before editing, map each changed behavior to its current oracle and execution
context. Define correct behavior and deliberate defects, plus the smallest
meaningful regressions. Do not replace a real integration boundary with mocks.
When old efficacy is absent, identify the gap instead of inventing old sensitivity.

Use these phase-specific challenges in addition to the campaign-wide gates:

- Batch output supplies the wrong object, kind, size, delimiter, duplicate response, missing response, trailing bytes, or early exit.
- The source contains symlinks/unsafe modes/private keys or changes hidden by index flags.
- A warm cache or builder-generated manifest supplies both actual and expected bytes.
- Final candidate bytes drift after private-build validation, or candidate/release metadata is interchanged.

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

Exact source maps and independent rejection sensitivity are preserved with measured process savings; published releases and validation boundaries remain unchanged.

All required coverage, safety, identity, failure propagation, and cleanup gates
take priority over speed. A local improvement cannot compensate for a lost
required defect or context. Do not proceed automatically to the next phase.

## Net budget and evidence

Charge production parser/process code, hermetic Git fixtures, all regressions, and measurement overhead. Local batch savings cannot establish a whole-campaign target.

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
