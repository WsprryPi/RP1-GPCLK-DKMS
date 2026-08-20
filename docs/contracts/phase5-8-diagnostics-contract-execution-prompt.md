<!-- SPDX-License-Identifier: MIT -->

# Phase 5.8 diagnostics contract execution prompt

## Authority and exit condition

Execute only the bounded read-only diagnostics portion of Phase 5A through
Phase 5C in `phase5-packaging-operator-enablement-execution-prompt.md`.
Repository changes and deterministic offline tests are authorized. Target
access, package or DKMS mutation, module load/unload/bind/unbind, overlay or
boot changes, enrollment, repair, reboot, GPIO, clock, DMA, transmission, RF,
tagging, publication, and consuming-repository changes are not authorized.

Phase 5.8 closes when the diagnostic contract and tool report every requested
identity and state when readable, express denied inspection as indeterminate,
remain bounded and secret-safe, cannot change system state, pass the complete
offline suite twice, and a separate adversarial assessment has no finding.

## Governing inputs and operator categories

Follow `AGENTS.md`, the module contract, the full Phase 5 prompt, UAPI v1,
release layout, installation model, overlay contract, permissions/enrollment
policy, compatibility/update policy, and signing policy. Emit exactly one
summary category:

- `healthy-and-qualified` for an exact `Qualified` identity;
- `healthy-but-experimental` for an exact `Experimental` identity;
- `build-compatible-but-live-disabled` for `Compatible-unqualified`;
- `unavailable` for absent prerequisites or no exact manifest identity;
- `rejected` for a known unsafe result, cleanup latch, malformed critical
  identity, or interrupted operation requiring recovery; or
- `indeterminate-because-inspection-lacked-privileges` when a required read or
  query was denied.

Never collapse unavailable, rejected, and privilege-indeterminate. A clean
report never proves absence of competing or direct-MMIO software.

## Required report

Report package-manager and DKMS status; running and installed kernels; header
availability; bounded build logs and transaction/last-result state; installed
module path, version, SHA-256, vermagic, signer, signature identifiers, loaded
state, immutable gate, and taint; endpoint presence, binding, ownership,
permissions, and type; bounded UAPI `QUERY`, capabilities, route,
compatibility state/reason/ID; release and manifest hashes, manifest ID, and
exact selected entry; enrollment record/status; cleanup-fault state; selected
route, installed DTBO hash, persistent marker, and runtime route; relevant
model, revision, base-DT, clock, DMA, and pinctrl identities; current-boot
project-only kernel diagnostics; and transaction-recorded residue.

Every read and command has a declared timeout/count/byte bound. Do not expose
raw physical addresses as a product interface. Do not collect private keys,
passphrases, tokens, unrelated logs, unrestricted dmesg/journal output, or
unbounded directory trees. Report unknown, absent, malformed, command-failed,
timed-out, and permission-denied states explicitly.

## Read-only implementation rules

The production command may open the endpoint read-only solely for `QUERY`.
Its subprocess allowlist is informational: `dpkg-query`, `dkms status`,
`modinfo`, and narrowly filtered current-boot `journalctl`. It must not invoke
an administrative project command or any mutating package, DKMS, module,
overlay, boot, enrollment, GPIO, clock, DMA, repair, reboot, transmitter, or RF
operation. Synthetic-root and injected-runner support exists only to prove the
collector offline; tests must reject any unexpected command before execution.

Compatibility selection requires one exact manifest entry matching both UAPI
compatibility ID and route. No match or multiple matches is unavailable.
Experimental classification reports enrollment separately; it never invents
enrollment or eligibility. An incomplete transaction is rejected and residue
is limited to journal-recorded package-owned paths. Diagnostics never repair
or remove residue.

## Validation and adversarial reinjection

Test all six categories, exact/no/duplicate manifest selection, missing and
malformed files, permission denial, endpoint metadata, UAPI parsing, unknown
capability bits, bounded command/file/log output, last transaction result,
residue bounds, secret exclusion, and the subprocess allowlist. Prove the
fixture suite dispatches no system or hardware operation. Run SPDX,
whitespace, documentation links, release validation, and the complete offline
suite twice.

Separately attempt to falsify read-only purity, ioctl layout, privilege
classification, compatibility selection, enrollment/latch reporting, bounds,
residue ownership, secret exclusion, and clean-report wording. Feed every
objective finding back into this prompt, implementation, and tests, invalidate
affected results, and repeat until no finding remains.

### Reinjected findings

1. The first synthetic-root adapter returned the UAPI fixture inside a generic
   file-result wrapper, unlike the real ioctl result. Normalize it at the
   boundary and regression-test classification through the complete collector.
2. UAPI v1 reports the cleanup latch through the stable compatibility reason,
   not a separate QUERY field. Derive the diagnostic boolean only from
   `cleanup-latched`; do not claim a successful read of a nonexistent field.
3. Presence of a platform-driver directory proves registration, not binding.
   Enumerate bounded driver-bound device entries and report binding only when
   one exists.
4. The first classifier could trust a positive UAPI state when no exact local
   manifest entry was selected. Require the unique selected entry and UAPI
   state to agree; absence is unavailable and disagreement is rejected.

All findings were reinjected and the affected tests repeated. The final
adversarial pass found no remaining objective issue within the offline scope.

## Completion report

Report files and behavior changed, exact checks, skipped environment checks,
system/hardware/RF and publication actions not performed, licensing/UAPI
impact, remaining target validation, Git state, and the next gated step. Do not
call all of Phase 5 complete.
