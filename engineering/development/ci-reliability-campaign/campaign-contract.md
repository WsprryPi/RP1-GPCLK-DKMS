<!-- SPDX-License-Identifier: MIT -->

# CI reliability campaign contract

This campaign prepares eleven bounded implementation phases for RP1-GPCLK-DKMS.
Reliability, safety, required coverage, and defect detection are acceptance gates.
Speed and maintenance reductions are optimization targets within those gates.
An aggregate improvement cannot compensate for losing a required obligation or
weakening detection of a specific required defect.

## Authority and scope

The current authoring task prepares, reviews, saves, commits, and pushes planning
documents only. It does not execute any implementation phase, test campaign,
candidate build, provisioning, package operation, or target operation.
A saved prompt is pending work, not an implementation-completion record.

Execute a phase only after the user explicitly selects it. Selection does not
authorize later phases, remote settings changes, hosted CI, publication, or
operations separately gated below. Reinspect source and authorization at entry.
Follow [AGENTS.md](../../../AGENTS.md), the
[module contract](../../contracts/rp1-gpclk-dkms-module-contract.md), and applicable
nested instructions. Preserve all user work and staging. Do not merge, amend,
rebase, force-push, create a PR, tag, publish, or retire another chat's work.

Audit and implement only RP1-GPCLK-DKMS. WsprryPi, WSPR-Transmitter, WsprryPico,
and the external qualification Harness remain separate owners. Record companion
dependencies without inspecting or changing sibling checkouts under this campaign.
Keep application policy, band/mode eligibility, and qualification outside the module.

## Execution boundaries

Hosted CI execution is not authorized for this campaign until the user explicitly
changes that instruction. This does not describe or change repository settings. Do not dispatch or rerun workflows, remove skip markers
to obtain validation, alter workflow triggers to suppress CI, or change repository
Actions settings. Every planning commit uses a supported CI-skip marker and a new
non-release feature branch; inspect existing run metadata after pushes without
launching a workflow. A skipped/pending check is not passing validation.

For later implementation, inspect every test before running it. Ordinary tests
must remain offline, unprivileged, network-free, hardware-free, and repeatable.
Run only checks within the selected phase's actual authorization. Provisioning,
network access for dependencies, real disposable-container dpkg/DKMS operations,
and environment installation require explicit effect-specific authorization.
Container package tests are real package operations, not host-only unit tests.

Do not perform host DKMS/module install/remove/load/unload/bind/unbind,
device-tree overlay operations, sudo mutations, boot/signing/udev/systemd/kernel
configuration changes, endpoint or GPIO/GPCLK/DMA operations, transmitter keying,
SDR capture, RF output, reboot, or shutdown. No phase grants those operations.
Do not run target collectors or clock-disabled target administration. Never
infer hardware, kernel-lifetime, timing, service, GPIO, or RF qualification from
host, header-build, or disposable-container results.

Keep generated output, measurements, and fault artifacts outside every checkout.
Use an identified disposable environment for any authorized package/compile work.
Keep results and prompt-review findings in the execution chat; do not commit run
logs, qualification campaigns, completion reports, or replacement archives.

## Reorientation at each phase entry

Inspect branch/worktree status, staging, remotes, current commit/tree, relevant
history, current contracts, owning implementation, tests, and recursive dispatch.
Record exact source/artifact/environment identities in chat. Preserve unexpected
work and avoid assuming that an earlier audit or phase still describes current code.
Use [testing guidance](../../testing.md) and [ROADMAP.md](../../../ROADMAP.md).
Do not copy historical counts into acceptance criteria without remeasurement.

## Evidence and acceptance

Preserve valid, malformed, adversarial, no-write, ownership, identity/revision,
cryptographic, persistence, cancellation, cleanup, and recovery obligations.
Retain independent golden vectors, real crypto checks, aborting hardware stubs,
the exact predecessor, consumed schemas/metadata, and final-output validation.
GPIO4 and GPIO20, C and C++, different platforms/headers/profiles, and independent
format/trust boundaries are distinct contexts. Never remove one to meet a quota.

For each behavioral change, define correct behavior and deliberate defects first.
Use source/fixture evidence to establish the old oracle's actual sensitivity.
If it has none, state that; do not invent prior efficacy. Define an independent
replacement oracle and demonstrate preserved or improved detection before retiring
the old path. Schedule/load variation must preserve correct behavior and reliable
failure detection. Repeated green runs or larger timeouts do not prove repair.

Readiness requires observed state. Preserve real product timing. Watchdogs are
finite failure guards with phase-specific diagnostics, not readiness evidence.
Trace partial I/O, EOF, exits, descendants, cancellation, and cleanup ownership.
Preserve the primary error and report secondary cleanup errors separately.
An unknown cleanup state blocks acceptance.

Run a separate adversarial assessment after implementation and again after each
repair. Reinject every failed assertion into affected work and repeat the affected
checks. Do not declare a phase complete while a required gate is pending or failed.
Do not broaden operation authority just to close a gate.

## Accounting

Freeze reproducible complete denominators before evaluating savings. Separate
orchestration, mixed fixtures/assertions, scenario data, production tooling,
generated/vendor assets, and documentation. Identify unallocated roles and holds.
Charge every replacement, helper, regression, companion edit, relocated
implementation, new dependency, and newly activated coverage.

Evaluate code, active physical files, process/suite/compiler/linker invocations,
jobs/contexts, and comparable elapsed time separately. Cases and required contexts
measure coverage, not reductions. Unused-test retirement receives zero baseline
or numerator credit. Unreferenced fixtures remain HOLD until unused status is
established. Do not claim an entire file envelope as removable machinery.

Separate measured facts, mathematical bounds, engineering estimates, and unknowns.
A local-unit reduction does not establish an overall 50 percent result.
Report successful first attempts, failed/cancelled work, retries/reruns, queue
delay, execution envelope, and aggregate overlapping job spans separately.
Do not call aggregate spans billed cost. Use comparable source, toolchain,
coverage, and cold/warm conditions; do not invent percentiles or precise budgets.
Required assurance is a minimum; defective checks and inadequate enforcement may
be improved, but weakened frequency/gating is not an efficiency saving.

## Phase handoff and lifecycle

Stop at the selected phase boundary. Report changes, exact checks/results,
skipped/pending contexts, sensitivity evidence, risks, remaining gates, source
identities, licensing/documentation impact, and Git state in chat.
Commit/push implementation only when separately authorized; honor no-CI markers.
Never report skipped hosted CI as passed.

An accepted prerequisite means its required assurance gates passed, or the user
accepted a documented no-change/HOLD disposition that preserves the existing
assurance. An optional optimization may be rejected without blocking later
measurement of unchanged behavior. A failed required reliability gate cannot be
waived as a successful optimization disposition.

The active index distinguishes prompt readiness from implementation status.
After later phase completion, consolidate durable technical content, repair links,
and retire completed prompts in accordance with AGENTS.md. Do not archive them
or retain completed prompts solely because an old checklist links to them.
