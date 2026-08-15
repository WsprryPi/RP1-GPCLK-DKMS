<!-- SPDX-License-Identifier: MIT -->

# Phase 5 exit-gate execution prompt

## Mission and exact exit statement

Execute the remaining work governed by
`phase5-packaging-operator-enablement-execution-prompt.md` and attempt to prove,
rather than merely restate, this exit claim:

> The exact tagged module release can be installed, built, signed, selected,
> diagnosed, upgraded, downgraded, rolled back, recovered, and completely
> removed on the named representative systems. Unknown or failed identities
> remain non-transmitting; no prohibited fallback occurs; existing
> qualification is neither broadened nor inherited; all release artifacts are
> reproducible, checksummed, and independently reviewed; and the module release
> is published before any dependent WsprryPi release.

Phase 5 closes only if every noun and verb in that statement is bound to an
exact immutable identity and accepted evidence. A policy, plan, mock, unit test,
header build, local archive, local tag, successful install, or earlier Phase 4
capture is not a substitute for a missing lifecycle, publication, integration,
or calibrated-claim gate.

## Authority and stop conditions

The current request authorizes repository inspection, this comprehensive prompt,
offline implementation and validation, adversarial review and reinjection, and
cohesive commit and push when warranted. It does not supply the exact Gate D,
E, F, or G inputs that the governing prompt requires. In particular, do not
infer:

- a target hostname, model/revision, administrator account, signing policy,
  enrolled-key identity, kernel row, route, permitted reboot, recovery channel,
  deadline, or permitted system mutations;
- calibrated instruments, routes, modes, output limits, conducted fixture, or
  RF authority;
- an approved release version/tag, publication destination, release credentials,
  or permission to change a GitHub release or issue; or
- authority to edit, commit, push, tag, or release `WSPR-Transmitter` or
  `WsprryPi`.

Stop a dependent gate as `blocked-input-required`, without weakening it, when
one of these exact inputs is absent. Read-only discovery may identify candidate
systems, but discovery never becomes mutation authority.

## Frozen starting identity

Before changing or executing anything, record the branch, commit, upstream,
ahead/behind state, worktree status, remotes, tags at `HEAD`, module version,
expected tag, UAPI ABI and header SHA-256, overlay source hashes, release-policy
hashes, and every declared blocker in
`release/release-integration-gates-v1.json`. Inspect all lifecycle scripts and
tests before running them.

If the worktree is dirty, divergent, or contains an unexplained generated
artifact, preserve it and stop before candidate freeze or publication. Never
build a publishable artifact from uncommitted bytes.

## Execution sequence

### 1. Contract-to-implementation audit

Machine-check every required lifecycle verb against an executable, tested
implementation. Distinguish read-only planning/evaluation from actual mutation.
At minimum, separately account for preflight, staging, archive verification,
DKMS register/build/install/uninstall/remove, signing and signer verification,
inactive route selection, output-disabled load/bind/query/release/unbind/unload,
status, upgrade, downgrade, rollback, interrupted-transaction recovery,
uninstall-one-version, unregister-all-test-versions, complete removal, repeated
removal, and residue audit.

An operation is not implemented merely because it appears in a JSON contract,
documentation, a shell usage string, a pure policy function, or a mocked command
list. Each mutating operation needs fixed validated targets, ownership records,
durable checkpoints, interruption behavior, stale/foreign-byte refusal,
idempotence semantics, bounded diagnostics, and deterministic offline failure
tests. Correct every offline implementation gap before target use.

### 2. Offline candidate gate

Run the full offline suite twice from fresh generated-output locations. Run SPDX,
license/provenance, whitespace, documentation-link, schema, UAPI, overlay,
shell/static, archive-content, secret-exclusion, checksum/tamper, and
reproducibility checks. Record unavailable dependencies as skips; do not convert
a structural fallback into full schema validation.

Generate only a development/non-publishable release unit until the source is a
clean committed candidate and the exact release tag has been approved. Rebuild
the archive and both DTBOs independently and require byte equality. Bind all
results to the exact source commit and tool identities.

### 3. Representative-system input freeze

Before any target mutation, create an execution instance of
`release/representative-system-matrix-v1.json` that names the actual host and
every identity and authorization required by Gate D. Each row needs its own
immutable evidence directory, deadline, baseline, allowed changes, recovery
method, route, signing policy, failure injection, expected result, and final
residue state. One host/kernel cannot satisfy rows requiring genuinely distinct
kernel or signing identities.

Do not execute a row whose system selection remains prose such as "a supported
system" or "where representative hardware is available." Missing required
systems or policies are unresolved Phase 5 blockers, not skipped passes.

### 4. Output-disabled lifecycle matrix

Execute every frozen row with live output immutable false. Record commands before
execution, UTC and monotonic intervals, deadlines, bounded stdout/stderr, exit
status, hashes, scoped kernel-log delta, checkpoints, cleanup, and baseline
comparison. Preserve failed attempts. Prove no active pinctrl selection, clock
prepare/enable delta, DMA submission, GPIO output, transmitter action, SDR use,
RF, or fallback.

After each row, recover or converge to its specified inactive state and audit
only package-owned residue. Never leave a candidate installed for convenience.
The complete matrix passes only when every required row has accepted exact
evidence and the named systems match their declared final states.

### 5. Release-candidate and publication gate

After the lifecycle matrix and its adversarial review pass, freeze one clean
committed candidate, approved version, expected tag, archive SHA-256, UAPI hash,
both overlay source/DTBO hashes, manifest hash, tool identities, and claim
ceiling. Populate compatibility only from accepted exact evidence. Existing
Phase 4 receiver-relative evidence never transfers to changed package bytes and
never creates calibrated `Qualified` status.

Under separate Gate F authority, create and push the reviewed tag, publish every
immutable artifact, download each public artifact to a fresh location, verify
outer and inner hashes and provenance, extract independently, and verify all
install inputs. Until fresh-download verification passes,
`modulePublicationConfirmed` remains false and no consumer may pin the release.

### 6. Ordered consuming-repository gates

Only after confirmed module publication, and under separate Gate G authority,
update `WSPR-Transmitter` to consume that exact release and pass byte-for-byte
and semantic UAPI checks. Only after that reviewed adapter identity exists may
`WsprryPi` pin the exact module and adapter identities and run its separately
authorized application qualification. Keep all commits, reviews, tags,
releases, issue state, evidence, and claims separate. Enforce module, then
adapter, then product publication order.

## Adversarial review and reinjection loop

After each substantive slice, independently try to falsify authorization,
operation completeness, path/ownership safety, interruption recovery, signing,
route isolation, output-disabled behavior, residue claims, reproducibility,
manifest truthfulness, qualification ceilings, public-download identity, UAPI
identity, and release ordering. Write every objective finding below, amend the
governing implementation or contract, invalidate affected evidence, and rerun
the affected checks. Ordinary green tests never waive a finding.

### Reinjected findings

1. At the starting identity, executable install and failed-install recovery do
   not demonstrate executable upgrade, downgrade, rollback, complete removal,
   repeated removal, or the 15-row representative lifecycle matrix. Pure policy
   evaluators and matrix-schema tests do not close those gates.
2. `release/release-integration-gates-v1.json` truthfully marks candidate freeze,
   representative lifecycle, publication/download verification, and consumer
   integration blocked. Do not publish or rewrite those statuses without exact
   evidence.
3. The current compatibility entries bind earlier Phase 4 identities and remain
   `Unavailable` and non-live for the Phase 5 package identity. Packaging cannot
   inherit or broaden them.
4. Structural schema validation when `jsonschema` is unavailable is a recorded
   environment limitation, not full JSON Schema validation.
5. A comprehensive request does not fill the exact Gate D/E/F/G identity and
   authorization fields. Stop those gates as `blocked-input-required` until
   their named inputs are supplied.
6. Operator-facing status text must distinguish the implemented guarded install
   transaction from the still-missing complete lifecycle surface; describing
   either the installer as absent or Phase 5 lifecycle as complete is false.

Repeat the assessment until no objective finding remains within the authorized
and executable slice. Phase 5 itself remains open if an external gate is
blocked, even when the offline slice has no remaining finding.

## Completion report

Report implemented, passed, failed, unavailable, blocked-input-required,
deferred, and unauthorized gates separately. Include exact identities and
hashes, commands and results, skips, target final states, compatibility and
claim ceilings, every system/GPIO/DMA/RF/publication/consumer action performed
and not performed, licensing and documentation impact, Git state, and the next
required authorization. Quote the exit statement only as proved or explicitly
state which clause remains unproved.
