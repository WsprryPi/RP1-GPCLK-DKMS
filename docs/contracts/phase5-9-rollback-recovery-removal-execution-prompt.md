<!-- SPDX-License-Identifier: MIT -->

# Phase 5.9 rollback, recovery, and complete-removal execution prompt

## Authority and exit condition

Execute only the bounded offline Phase 5.9 portion of
`phase5-packaging-operator-enablement-execution-prompt.md`. Repository changes
and deterministic synthetic-state tests are authorized. Target access, package
or DKMS mutation, module load/unload/bind/unbind, overlay or boot changes,
initramfs changes, signing-key changes, reboot, GPIO, clock, DMA, transmission,
RF, tagging, publication, and consuming-repository changes are not authorized.

Phase 5.9 closes when rollback, recovery, and complete removal have distinct
machine-readable contracts; unknown ownership or cleanup state fails closed;
the administration tool can produce non-mutating, exact plans and evaluate
post-operation evidence; simulated interruption and ownership tests cover the
full contract; the complete offline suite passes twice; and a separate
adversarial assessment has no finding.

## Definitions

- **Rollback** restores the immediately preceding known-complete module release
  and package-owned configuration after a failed successor. It may remove only
  successor-owned bytes and may restore only predecessor bytes recorded before
  the attempt. It refuses later administrator or third-party changes.
- **Recovery** resolves one incomplete or inconsistent lifecycle transaction.
  It classifies the durable checkpoint and either resumes a proven safe next
  step or converges to a documented inactive state. It never guesses ownership,
  treats a reboot or reinstall as proof, or clears a cleanup latch without a
  complete postcondition audit.
- **Complete removal** removes all and only state owned exclusively by this
  package release. Shared or administrator-owned configuration, keys, trust,
  services, and unrelated bytes are preserved and reported.

Uninstalling one DKMS row, deleting a source directory, or removing an overlay
is not complete removal. Repeated complete removal is accepted only after the
same absence and preservation audit.

## Durable transaction and ownership rules

Every mutating lifecycle operation must durably record its operation ID,
release and kernel identities, starting complete state, checkpoint, expected
next step, package-owned paths and hashes, predecessor rollback bytes and
hashes, commands attempted, result, and whether recovery is required. The
journal is written before mutation. Unknown fields, missing checkpoints,
unresolved symlinks, path traversal, broad targets, mismatched hashes, or
unclassified files stop the operation.

Rollback requires a failed inactive successor, an exact predecessor snapshot,
unchanged rollback targets, and a known cleanup state. Recovery requires an
inactive interrupted journal and a recognized checkpoint. Neither operation
may enable live output, activate an overlay, reboot, weaken signing or
compatibility policy, overwrite changed administrator state, or select a
fallback backend.

Complete removal first disables eligibility and proves: no open endpoint or
owner, no active generation/callback/DMA, cleanup not latched, selected pin
safe, and clock prepare/enable counts and parent restored to the recorded
baseline. A loaded module or bound device must be handled only by a separately
authorized, proven synchronous cleanup path; this offline slice plans no
forced teardown. Open, active, busy, unsafe, unknown, or unproven state rejects
removal.

Only exact inventory entries marked package-owned may be removed. Hash-guarded
files and exact symlinks must still match. Directories are removed only if
empty. Persistent overlay markers must be exact package markers; unmarked or
modified boot configuration is preserved and blocks automatic removal. Private
signing material may be removed only when an explicit ownership record proves
it was created exclusively for this package and is not shared; otherwise it is
retained and reported.

## Complete-removal acceptance

The post-operation evidence must prove all of the following:

1. no loaded module, bound platform device, open endpoint, owner, active work,
   callback, or DMA;
2. selected pin safe and clock prepare/enable counts and parent restored to the
   exact recorded baseline;
3. no production runtime overlay or package-owned persistent boot marker;
4. no DKMS registration, build, or installed module version and no module file
   under any applicable kernel update directory;
5. no package-owned udev, systemd, manifest, configuration, diagnostic,
   source, tool, documentation, transaction, backup, or residue file;
6. module dependencies and initramfs updated where the platform and recorded
   installation require them;
7. no exclusively package-created private signing material remains, while
   administrator-owned and shared signing material is preserved; and
8. every recorded unrelated/configuration preservation sample remains
   byte-for-byte identical where practical, with any unverifiable item causing
   an indeterminate failure rather than success.

Acceptance is a conjunction: `false`, `unknown`, absent required evidence, or
an extra field fails. A clean audit does not prove absence of unrelated
direct-MMIO interference.

## Offline implementation and validation

Freeze the contract in release metadata. Implement pure planners/evaluators
used by the administrative surface; they must dispatch no command. Test valid
rollback, recovery at every durable checkpoint, complete removal, repeated
removal, every acceptance assertion independently false/unknown/missing,
changed rollback bytes, foreign files, shared/admin keys, exclusive keys,
modified boot entries, symlinks, broad paths, residue, dependency/initramfs
requirements, and open/busy/active/cleanup-latched states.

Run SPDX, whitespace, documentation links, release validation, and the complete
offline suite twice. Then separately attempt to falsify operation separation,
ownership, rollback freshness, checkpoint recognition, fail-closed cleanup,
key ownership, preservation evidence, postcondition completeness, repeated
removal safety, and non-mutating purity. Feed every objective finding back into
this prompt, implementation, tests, and documentation, and repeat until none
remain.

### Reinjected findings

1. The first implementation did not place the new contract and evaluator in the
   installed release inventory. Add both as exact package-owned artifacts and
   exercise their installation in the synthetic transaction suite.
2. Pure functions alone lacked an operator-reviewable surface. Provide
   read-only JSON commands for rollback planning, recovery planning, and the
   complete-removal audit; reject symlink snapshots and dispatch no commands.
3. Do not accept truthy substitutes for known safety evidence. Require exact
   booleans and reject every missing, extra, or indeterminate field.

All findings were reinjected and the affected tests repeated. The final
adversarial pass found no remaining objective issue within the offline scope.

## Completion report

Report files and behavior changed, exact checks and skips, all system/hardware/
RF and publication actions not performed, licensing/UAPI impact, remaining
target validation, Git state, and the next gated step. Do not call Phase 5 or
target lifecycle qualification complete.
