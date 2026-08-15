<!-- SPDX-License-Identifier: MIT -->

# Phase 5 packaging and operator enablement execution prompt

## Mission and exit condition

Act as the packaging implementer, representative-target lifecycle operator,
release custodian, cross-repository integration coordinator, evidence
custodian, and adversarial reviewer for `WsprryPi/RP1-GPCLK-DKMS`. Convert the
exact Phase 4 module candidate into a reproducible, diagnosable, reversible,
fail-closed operator installation without broadening its compatibility or RF
qualification claims.

Phase 5 is complete only when all of the following are true:

1. the release unit and every installed path, owner, permission, version,
   checksum, and lifecycle transition are frozen and machine-checked;
2. deterministic offline, simulated-failure, representative-header, and
   representative-target lifecycle suites pass with no unresolved objective
   finding;
3. installation, signing, route selection, output-disabled verification,
   update, downgrade, rollback, interruption recovery, and complete removal
   restore every named representative system to the expected state;
4. unknown or failed identities remain non-live and no prohibited physical
   backend fallback occurs;
5. a tagged, checksummed, reproducible module release is published and its
   downloaded artifacts are independently verified;
6. `WSPR-Transmitter` consumes that exact release's canonical UAPI and
   `WsprryPi` consumes that exact release through compatibility metadata, with
   separate commits, reviews, tests, and release decisions; and
7. any `Qualified` claim is backed by the required calibrated evidence for the
   exact packaged identity. Receiver-relative evidence alone remains clearly
   identified and may support only the reviewed lesser release state.

Passing only an offline package build, DKMS build, signature check, install,
or clean removal does not close Phase 5. A partial lifecycle or integration
matrix remains open and must not be generalized.

This prompt is a specification, not authorization. Do not modify repositories,
mutate a target, publish an artifact, change issue state, or operate GPIO or RF
merely because this file exists. Stop at every gate unless the current user
request grants that exact bounded authority.

## Governing contracts and frozen inputs

Follow, in order:

1. `AGENTS.md`;
2. `docs/contracts/rp1-gpclk-dkms-module-contract.md`;
3. `docs/contracts/phased-plan.md`;
4. `docs/contracts/uapi-v1.md`;
5. `docs/development/decisions/0006-phase3-interface-freeze.md`;
6. `docs/development/decisions/0007-phase4a-stock-kernel-live-path.md`;
7. the exact Phase 4 closeout, route reports, adversarial assessments, and
   artifact hashes;
8. canonical `include/uapi/linux/rp1_gpclk.h`, `uapi-identity.json`, and
   `schema/rp1-gpclk-compatibility-manifest-v1.schema.json`; and
9. the exact reviewed subordinate Phase 5 slice prompt when executing only a
   bounded portion of this phase.

ABI v1 bytes and semantics, ioctl values, enum values, structure sizes and
offsets, capability meanings, route values, overlay names, DT properties,
compatible, module/device names, and compatibility vocabulary are frozen.
Correct implementation defects without silently changing a frozen interface.
If a change is necessary, stop for a reviewed additive ABI/schema decision,
assign a new immutable identity, and invalidate every affected build,
lifecycle, integration, and calibrated evidence row.

The Phase 4 closeout is receiver-relative evidence for one exact combined
candidate, two routes, 2 mA, and the recorded kernel/DT/fixture identity. It is
not calibrated absolute-frequency, power, spectral-compliance, radiated-RF,
another-kernel, higher-drive, or application-scheduling evidence. Packaging
must preserve that boundary.

## Repository ownership and release ordering

This repository owns module source, canonical UAPI, Kbuild/DKMS packaging,
route overlays, module compatibility metadata, signing and lifecycle tooling,
module diagnostics, module-specific evidence, and module releases.

`WsprryPi/WSPR-Transmitter` owns its userspace adapter, request translation,
canonical-UAPI consumption strategy, application-side lifecycle, and terminal-
reason handling. `WsprryPi/WsprryPi` owns physical-backend policy, persisted
route selection, installer orchestration, enrollment, operator workflow,
support diagnostics, scheduling, and product qualification.

Do not vendor application source here or copy this complete module source tree
into WsprryPi. Coordinate only through the tagged module artifact, canonical
UAPI, compatibility manifests, checksums, and explicit cross-repository tests.
Keep repositories' branches, dirty state, commits, reviews, tags, issues, and
qualification claims separate.

The release order is mandatory:

1. publish and independently verify `RP1-GPCLK-DKMS`;
2. integrate and, when separately authorized, release `WSPR-Transmitter`
   against that published module identity; and
3. integrate and, when separately authorized, release `WsprryPi` against the
   published module and exact adapter identities.

No dependent release may consume a moving default branch or an unpublished
local archive.

## Authorization gates

### Gate A: contract and research

Read-only inspection, contract drafting, gap analysis, matrix design, and
review are permitted only within the current task. Gate A authorizes no source
change, build whose implementation has not been inspected, target access,
external publication, or lifecycle action.

### Gate B: offline implementation

Obtain explicit authorization before changing source, packaging, scripts,
tests, schemas, manifests, or documentation. Offline work must remain
unprivileged, network-free, hardware-free, deterministic, and safe to repeat.
Mocks must not dispatch real `dkms`, `modprobe`, `dtoverlay`, boot-configuration,
key-enrollment, package-manager, GPIO, clock, DMA, transmitter, or RF actions.

### Gate C: disposable representative build qualification

Before compiling against representative headers or using a disposable DKMS
staging tree, record the exact source/archive, header packages, kernel releases,
configuration, compiler, architecture, symbol versions, and permitted output
paths. Do not register with system DKMS, install, sign, load, bind, or change a
target under this gate.

### Gate D: target lifecycle administration with output disabled

Before any target mutation, obtain bounded authorization naming:

- target host, model/revision, administrative account, and connection method;
- exact source commit, sealed archive digest, module version, UAPI digest,
  compatibility manifest, and permitted overlay artifacts;
- permitted package prerequisite, DKMS register/build/install/remove, signing,
  key-enrollment, module load/unload, bind/unbind, overlay, boot-configuration,
  update, downgrade, rollback, recovery, and removal actions;
- whether service changes, boot configuration, reboot, or initramfs updates are
  permitted, with recovery procedures and deadlines;
- the one route allowed in each row and the immutable output-disabled setting;
  and
- exclusions, including active pinctrl, clock enablement, DMA submission, GPIO
  output, transmitter keying, SDR operation, antenna connection, and RF.

Authorization for one host, kernel, route, signing policy, or lifecycle row
does not authorize another. No reboot is implicit. Stop before a reboot or
boot-time validation unless it is expressly named with a recoverable access
plan.

### Gate E: calibrated conducted qualification

Obtain a separate authorization for each route and mode family before
calibrated output. It must identify the exact frozen packaged candidate,
kernel/DT/overlay, route, header pin, drive, frequencies, modes, maximum
durations/repetitions/energized time, conducted non-radiating chain,
attenuation/load, calibrated instruments and references, calibration dates and
uncertainties, operator and observers, stop triggers, cleanup deadlines, and
explicit permission for the bounded GPIO/DMA/clock/RF actions.

GPIO4 and GPIO20 remain independent. QRSS/TONE, FSKCW, DFCW, and WSPR retain
separate result rows. No antenna or intentional radiation is authorized by
this prompt.

### Gate F: module publication

Tagging, pushing, publishing a release, uploading artifacts, or changing an
issue/release state requires explicit publication authorization after the
release-candidate and adversarial gates pass. Publication authority for this
repository does not authorize a WSPR-Transmitter or WsprryPi commit, tag, push,
release, or issue transition.

### Gate G: cross-repository implementation and release

Obtain separately bounded authority for each consuming repository. Inspect its
contracts, branch, worktree, remotes, submodules, and relevant history before
editing. Preserve dirty work and use the already published module artifact as
the immutable integration input.

## Persistent safety and compatibility invariants

- Target stock Raspberry Pi kernels; never introduce or restore a maintained
  custom-kernel dependency.
- Never replace stock `clk-rp1`, fall back to `/dev/mem`, use raw userspace
  MMIO/private symbols/fixed physical addresses, or select another physical
  transmitter backend after failure.
- Unknown hardware, kernel, DT, firmware, headers, configuration, symbols,
  signing, manifest, artifact, resource, route, capability, enrollment,
  cleanup, or recovery state fails closed.
- A DKMS or header build establishes at most `Compatible-unqualified` and
  cannot preserve or create live eligibility by itself.
- New and rebuilt installations default to live output disabled. Experimental
  operation requires explicit durable administrator enrollment tied to the
  exact relevant identities.
- A cleanup failure latches `Rejected` until the reviewed recovery contract
  proves remediation. Reinstall, reload, reboot, or a later nominal run does
  not silently clear it.
- GPIO4 and GPIO20 use separate one-route overlays and evidence. Never infer
  one route from the other or accept an arbitrary GPIO parameter.
- The device node is root-owned and restrictive, normally mode `0600`. Any
  broader access model requires a separate reviewed security decision.
- Installation must not disable, blacklist, replace, or rewrite unrelated
  drivers, overlays, packages, keys, boot entries, services, or administrator
  files.
- Release only resources and remove only files acquired or created by this
  project. Never restore another consumer's state from a stale snapshot.
- Operator warnings describe residual risk; they do not substitute for
  technical checks or claim complete exclusion against direct-MMIO software.

## Phase 5A: release-unit and policy freeze

Before implementation, freeze a machine-checkable release layout and policy:

1. source package name, module name, semantic/prerelease version rules, Git tag
   format, archive name, and one versioned archive root;
2. module source, Kbuild, `dkms.conf`, UAPI, overlay source and DTBO,
   compatibility, provenance, checksum, tooling, documentation, test, and
   release-note artifacts included in the release;
3. installed destinations, owner, group, mode, replacement policy, and removal
   ownership for every artifact;
4. deterministic archive order, paths, timestamps, ownership, permissions,
   compression metadata, tool identity, and exclusion rules;
5. compatibility and enrollment state machines, invalidation inputs, and
   operator-visible reasons;
6. signing/key ownership, enrollment, rotation, retention, and removal policy;
7. GPIO4/GPIO20 overlay selection, conflict, persistence, transition, reboot,
   rollback, and removal rules;
8. transactional install/upgrade/downgrade/rollback/recovery checkpoints;
9. diagnostics schema and redaction/secret-exclusion rules; and
10. release-candidate, calibrated qualification, publication, integration, and
    dependent-release ordering.

Use an architecture decision if a choice changes ownership, UAPI/schema,
security, compatibility, installation, signing, release, or distribution
policy. Update the engineering contract only when its durable contract changes.

## Phase 5B: deterministic offline packaging implementation

Implement the smallest maintainable release surface satisfying the freeze:

1. Use one exact version in module metadata, `dkms.conf`, archive root/name,
   compatibility metadata, provenance, and release notes. Reject inconsistency.
2. Generate a deterministic source archive from reviewed tracked inputs. Exclude
   `.git`, builds, caches, evidence captures, secrets, private keys, local
   configuration, and unrelated files. Refuse a release from dirty or
   uncommitted bytes; a deliberate development override must mark the output
   non-release and non-publishable.
3. Compile route-specific DTBOs reproducibly and verify their source, compatible,
   endpoint, route, pin, clock, DMA, and safe/default pinctrl contracts.
4. Generate cryptographic checksums and provenance covering the archive,
   canonical UAPI, overlays, compatibility manifest, source commit/tag, tool
   versions, generation commands, and dirty-state decision.
5. Provide a deny-by-default release manifest. Unknown identities are
   `Unavailable`; build/lifecycle evidence alone is non-live; exact evidence
   links are required for every stronger state.
6. Implement narrowly scoped lifecycle actions for preflight, stage, register,
   build, sign, verify, install, select route, output-disabled query, status,
   upgrade, downgrade, rollback, recover, uninstall, unregister, and complete
   removal. Prefer explicit subcommands over a monolithic implicit installer.
7. Make safe actions repeatable and state their repeat-run behavior. Refuse
   unresolved symlinks, traversal, unexpected owners/modes, mismatched versions,
   unrecognized markers, ambiguous state, and broad deletion targets.
8. Treat boot configuration as a separate explicit transaction with exact
   markers, duplicate/conflict rejection, atomic replacement, preserved
   metadata, verified backup, rollback, and no automatic reboot.
9. Use administrator-supplied signing keys/certificates. Never create a shared
   release private key, archive private material, print secrets, or delete a
   key used by other modules. Verify signer and signed bytes after every build.
10. Provide read-only diagnostics and separate explicit repair actions. A
    status command must not load, bind, apply an overlay, repair, enroll, or
    otherwise mutate the system.

Inspect every script and test before execution. Use defensive shell or a safer
implementation language consistently, strict error handling, fixed/validated
paths, bounded logs, atomic writes, explicit privileges, and cleanup traps.
Never construct destructive targets from unresolved environment variables,
globs, command substitution, `/`, a home directory, or a workspace root.

## Required diagnostics contract

Read-only diagnostics must distinguish healthy, degraded, unavailable,
rejected, indeterminate, and residue states and report, when accessible:

- tool/package/release and compatibility-manifest identity;
- installed and running kernels, header packages, DKMS version and status;
- last build/install/sign/load result and bounded relevant logs;
- module path, version, SHA-256, vermagic, signer, signature and taint status;
- loaded, bound, open/busy, endpoint, owner, group, and mode state;
- canonical UAPI version/hash, QUERY response, capabilities, bound route,
  compatibility ID/state/reason, and immutable live gate;
- selected overlay source/DTBO/hash, persistent boot marker, runtime DT
  identity, and route conflicts;
- Pi model/revision, firmware/base-DT identity, clock provider/ID, pinctrl and
  DMA identities without exposing raw physical addresses as a UAPI contract;
- administrator enrollment identity and why it is current or stale;
- cleanup-fault latch, recovery status, interrupted transaction, backups, and
  package-owned residue; and
- narrowly scoped run-local or boot-local kernel diagnostics with collection
  limits clearly stated.

Never report absence of interference from a clean diagnostic run. Never record
private keys, passphrases, tokens, unrelated logs, or unrestricted system data.

## Upgrade, downgrade, rollback, recovery, and removal semantics

Define these operations separately:

- **Upgrade** stages a distinct successor while retaining the prior complete
  version until build, signing, installation, output-disabled identity query,
  and successor cleanup pass.
- **Downgrade** intentionally selects a reviewed earlier version; version order
  does not confer compatibility or qualification.
- **Rollback** restores the immediately prior complete tool-owned state after
  successor failure without overwriting later administrator or third-party
  changes.
- **Recovery** inspects an interrupted or inconsistent transaction and either
  resumes a proven safe checkpoint or converges to a documented inactive state.
- **Complete removal** removes all and only package-owned module versions,
  overlays, markers, manifests, policy, generated state, backups, and tooling
  after proving safe absence and preserving shared/admin-owned keys and files.

Removal must reject or first synchronously quiesce, under the proven contract,
an open descriptor, bound endpoint, active generation, callback, DMA, clock,
or unsafe pin state. It must verify module absence, DKMS absence, dependency
metadata, overlay/boot-marker absence, endpoint absence, safe pins, zero owned
activity, expected clock state, no unclassified diagnostic, and no package-
owned residue. Repeated complete removal must be safe and report already absent.

## Phase 5C: deterministic and simulated validation

Add offline tests for at least:

- version consistency and invalid version syntax;
- archive contents, paths, modes, order, timestamps, gzip metadata,
  reproducibility, secret exclusion, and tamper detection;
- canonical UAPI bytes and semantic identity;
- overlay source/DTBO symmetry, allowlisted route isolation, and tampering;
- manifest schema, exact evidence linkage, impossible state/live combinations,
  unknown identity, stale enrollment, and cleanup-latch behavior;
- invalid routes, paths, symlinks, owners, permissions, markers, and broad
  targets;
- missing tools, DKMS, headers, compiler, key, certificate, and overlay support;
- each DKMS add/build/install/uninstall/remove failure point;
- signing, verification, wrong-kernel, wrong-vermagic, and wrong-signer failure;
- overlay conflict, duplicate marker, partial/failed atomic write, and rollback;
- load, bind, query, release, unbind, and unload failure;
- interruption at every upgrade/downgrade checkpoint;
- rollback and recovery failure, stale state, and cleanup latch;
- complete removal, repeated removal, and protection of every non-owned file;
- diagnostic read-only behavior, redaction, bounded logs, and privilege limits;
  and
- explicit proof that mocks cannot dispatch system, GPIO, DMA, transmitter, or
  RF actions.

Run the complete offline suite twice from clean generated-output locations,
warnings fatal where supported. Run SPDX, licensing/provenance, whitespace,
documentation/link, schema, UAPI, overlay, shell/static analysis, archive
reproducibility, and representative-header checks. Record skipped tools and
environment limitations; do not substitute an unavailable check with a claim.

Conduct a separate offline adversarial assessment, reinject every objective
finding, invalidate affected results, and repeat until no finding remains.

## Phase 5D: representative target lifecycle qualification

Under Gate D, use a fresh sealed candidate and evidence directory for every
attempt. Before mutation, record target access/recovery procedures and capture:

- hostname, privacy-safe stable identifier, model/revision, boot ID, kernel,
  architecture, packages, compiler, headers, configuration, symbol versions,
  firmware, bootloader, base/runtime DT, signing policy, taint, and UTC/monotonic
  intervals;
- current modules, DKMS registrations, overlays, boot configuration, services,
  device nodes, package files, relevant pins/clocks/DMA state, and scoped dmesg;
- source commit/tag, archive and internal hashes, UAPI, DTBOs, manifest,
  lifecycle-tool version, route, immutable output gate, and authorization; and
- hashes and metadata for every file the transaction may alter, plus the exact
  baseline and expected final state.

Use the predeclared, machine-readable
`release/representative-system-matrix-v1.json`. One Pi and one kernel are
insufficient for the packaging gate. The matrix is frozen before target
testing and includes all of these required rows:

| Class | Required rows |
| --- | --- |
| Clean install | prerequisites, verify archive, register, build, sign as policy requires, install, output-disabled load/bind/query/release/unbind/unload |
| Routes | GPIO4 and GPIO20 independently; other route remains safe and unclaimed |
| Signing | non-enforcing policy, locally trusted key, missing key, bad signature, wrong signer, enforced rejection where representative hardware is available |
| Kernel handling | known exact kernel, prior kernel/downgrade, newer unknown kernel/demotion, missing headers, build failure, wrong vermagic |
| Package transitions | upgrade, downgrade, failed successor, automatic rollback, interruption at every durable checkpoint, explicit recovery |
| Conflicts | pre-existing DKMS version, overlay/boot-marker conflict, busy/open endpoint, unrelated configuration and key ownership |
| Removal | uninstall one version, unregister all test versions, complete removal, repeated removal, residue audit |

The required stable rows additionally make explicit: current supported
Raspberry Pi OS kernel; prior supported kernel for downgrade; newer unknown
kernel for demotion; signing not enforced; signing enforced with an enrolled
key; deliberately failed build; deliberately rejected signature; missing
headers; conflicting overlay or resource; interrupted upgrade; stale manifest;
corrupted archive plus each route-specific DTBO; removal while inactive;
attempted removal while open or active; and reinstall after proved complete
removal.

For each row define the system selection, preconditions, failure injection,
expected compatibility state/reason, live eligibility, transaction state,
retained prior version, cleanup result, diagnostics, files and system state
allowed to change, final state, residue audit, maximum duration, and evidence
identity before execution.
Stop on an unexplained delta, identity mismatch, unclassified kernel diagnostic,
unsafe state, cleanup ambiguity, or exceeded deadline.

All target lifecycle rows remain output-disabled. Prove no DMA submission, no
clock prepare/enable delta, safe selected and unselected pins, restrictive
endpoint permissions, no owner after query/release, and no physical-backend
fallback. A lifecycle result cannot create calibrated or RF evidence.

At final cleanup remove only test-owned artifacts, restore only explicitly
authorized tool-owned state, and compare the complete post-state with baseline.
Retain only approved evidence. Do not leave the candidate installed merely for
convenience unless the current authorization explicitly requests that outcome.

## Evidence identity and integrity

Record commands before execution, expected results, UTC and monotonic
timestamps, deadlines, exit status, bounded stdout/stderr, file hashes, state
snapshots, dmesg baseline/delta, failure injection, rollback/recovery, cleanup,
and pass/fail decision. Preserve failed attempts; never reuse, append to,
delete, or rewrite their evidence directories.

Create relative-path evidence manifests only after all writers close and
target cleanup completes. Remove private signing material before sealing.
Archive deterministically, hash locally, copy/download to a separate location,
verify the outer digest, extract to a different path, verify every inner hash,
and rerun all analysis from preserved raw inputs.

Lifecycle evidence promotes only the exact tested identity and only as allowed
by the compatibility contract. A successful lifecycle matrix is not proof of
timing, calibrated frequency, power, spectrum, modes, RF, coexistence, another
kernel/DT/firmware, another route, or application scheduling.

## Phase 5E: calibrated qualification review

Calibrated qualification is an explicit release-state gate, not an accidental
side effect of packaging. Use the exact frozen packaged candidate that passed
the affected lifecycle rows. For each authorized route and mode, record:

- traceable absolute carrier and tone-frequency accuracy and uncertainty;
- tone spacing, ordering, transition settling, timing, and duration;
- conducted output power at the defined reference plane and uncertainty;
- harmonics, spurious emissions, occupied bandwidth, phase-noise/jitter proxy,
  startup/disable transients, and instrument dynamic-range limitations;
- the complete WSPR symbol sequence and timing where applicable;
- cancellation, terminal reason, divider readback, restoration, cleanup, and
  run-local diagnostics; and
- instrument, reference, attenuator/load/fixture identity, calibration status,
  analysis version, raw captures, hashes, and independent reviewer.

Apply thresholds declared before output. Keep QRSS/TONE, FSKCW, DFCW, and WSPR
separate. Keep GPIO4 and GPIO20 separate. A decode is not calibrated frequency,
power, spectrum, or cleanup evidence. Receiver-relative Phase 4 evidence
remains valid within its stated scope but does not fill calibrated rows.

If calibrated review changes module source, UAPI, overlays, compatibility,
timing behavior, package contents, signing, or lifecycle tooling, assign the
required new candidate identity and rerun every affected Phase 5 check. Mark
an exact identity `Qualified` only when the module contract's complete evidence
classes and independent adversarial review pass. Otherwise publish, if
authorized, only with the truthful lesser state and limitations.

## Phase 5F: release-candidate freeze and module publication

A candidate is an exact commit plus a sealed archive checksum that may be used
for authorized testing. It is not a consumable product release. A published
release exists for consumers only after Gate F publication completes and fresh
downloads of every public artifact pass outer and inner identity verification.
Neither an expected/local tag nor locally reproducible bytes cross that
boundary.

Before publication:

1. begin from a clean, synchronized worktree and reviewed committed candidate;
2. rerun the full offline suite twice and every required representative build
   and target lifecycle row against the exact bytes to be tagged;
3. close independent packaging, lifecycle, compatibility, release-integrity,
   and calibrated-claim adversarial assessments;
4. generate the final populated compatibility manifest, provenance, checksums,
   security notes, behavioral notes, supported identities, and exclusions;
5. reproduce the source archive and DTBOs independently and compare bytes;
6. verify internal versions, tag, commit, UAPI, archive root/name, DKMS package,
   module metadata, manifest, and release notes agree;
7. prove no private key, local configuration, target identifier beyond policy,
   unreviewed evidence, cache, or build residue is included; and
8. verify installation, rollback, recovery, and complete-removal instructions
   from the candidate artifacts.

Under Gate F, create and push the reviewed tag, publish the source release and
checksums, then download every public artifact into a new location and repeat
outer/inner checksum, provenance, archive-layout, signature where applicable,
and install-input verification. Publication is unconfirmed until this
post-download verification passes. Do not replace a published artifact under
the same version; publish a new reviewed version for any changed byte.

The machine-readable release and integration ordering contract is
`release/release-integration-gates-v1.json`. Its prerequisites may not be
skipped: all offline checks, representative lifecycle rows, adversarial
closure, reproduction, version/tag agreement, post-download checksum
verification, a real populated compatibility manifest, verified operator
instructions, documented limitations, and evidence-bounded claims precede a
consumable module release. Only then may canonical-UAPI adapter integration,
cross-repository byte and semantic checks, exact WsprryPi pinning, application
qualification, and dependent releases proceed in their owning repositories.

## Phase 5G: exact-release WSPR-Transmitter integration

Under separate Gate G authority, migrate the adapter to the published canonical
UAPI rather than normalizing the historical header silently. Machine-check:

- header bytes and SPDX identity where an exact copy is used;
- ABI version, ioctl magic/values, structure sizes/offsets/alignment, enums,
  flags, routes, modes, capabilities, compatibility states/reasons, terminal
  reasons, and limits;
- QUERY and capability validation before acquisition;
- bound-route and requested-route agreement;
- module/build/compatibility identity and live-eligibility handling;
- request translation for WSPR and bounded events;
- generation ownership, STOP, GET_STATE, RELEASE, stale state, process close,
  provider removal, and every terminal reason;
- deny-by-default behavior for missing/malformed manifests, old/new UAPI,
  absent capabilities, unknown states, cleanup latch, and identity mismatch;
  and
- offline fake/mock tests that never require the kernel module or hardware.

Pin the exact module release identity and checksum in reviewable compatibility
metadata. Do not copy this module tree into WSPR-Transmitter. A passing adapter
test does not publish or qualify WsprryPi.

## Phase 5H: exact-release WsprryPi integration

Under separate Gate G authority, integrate the already published module and
reviewed adapter through WsprryPi-owned policy:

- pin exact module tag, source archive checksum, UAPI identity, compatibility
  manifest identity, and allowed adapter commit/release;
- implement fail-closed physical-backend selection with no automatic fallback;
- persist only allowlisted GPIO4/GPIO20 selection and require administrative
  route transitions;
- orchestrate explicit install, signing, status, update, downgrade, rollback,
  recovery, and complete removal without duplicating module-owned logic;
- expose compatibility state/reason, live eligibility, stale enrollment,
  signing/build/overlay failure, cleanup latch, and recovery guidance;
- require durable Experimental acceptance where applicable and invalidate it
  on relevant identity changes;
- incorporate bounded diagnostics into support workflows without secrets or
  unbounded system data; and
- preserve application scheduling and per-mode qualification as application-
  owned evidence, not a module claim.

Run offline policy, configuration, migration, installer-mock, UAPI identity,
manifest, failure, recovery, and backend-selection tests first. Any real target
application validation needs its own bounded authorization and exact release
identities. Publish no dependent WsprryPi release before the module release and
integration gates pass.

## Independent adversarial assessment and reinjection loop

After every substantive slice, independently attempt to falsify:

- authorization scope and separation of offline, target, RF, publication, and
  cross-repository actions;
- release completeness, deterministic reproduction, provenance, checksum,
  version, tag, and public-download identity;
- secret exclusion, privilege boundaries, path/symlink/ownership safety, atomic
  writes, backup ownership, and destructive-target resolution;
- signing enforcement, key ownership/retention/rotation, wrong-signer and
  wrong-kernel rejection;
- overlay route isolation, boot atomicity, conflict handling, reboot recovery,
  and unselected-pin safety;
- DKMS partial failure, kernel update demotion, upgrade/downgrade transaction,
  every interruption point, rollback, recovery, and complete removal;
- diagnostics truthfulness, read-only behavior, bounded collection, redaction,
  and residue detection;
- compatibility-state ceiling, enrollment invalidation, cleanup latch, no-
  fallback behavior, and every live-eligibility claim;
- target baseline, run-local diagnostics, failed-attempt retention, evidence
  integrity, and final absence;
- calibrated threshold provenance, traceability, uncertainty, raw-to-derived
  reproducibility, route/mode independence, and scope of receiver-relative
  evidence;
- cross-repository canonical UAPI identity and exact published-artifact pinning;
  and
- module-before-adapter-before-product release ordering and every claimed exit
  condition.

Write every objective finding into this prompt, a subordinate execution prompt,
or a reviewed decision; correct it; invalidate and rerun all affected evidence;
and repeat the independent assessment. Ordinary green tests do not waive a
finding. Stop when correction requires expanded authorization, a new interface,
different hardware, unavailable calibrated equipment, external coordination,
or an unsafe operation.

## Final completion report

Lead with the outcome and include:

- completed, failed, unavailable, deferred, and unauthorized Phase 5 gates;
- files and behavior changed in each repository;
- exact module, UAPI, overlay, manifest, archive, tag, target, adapter, and
  WsprryPi identities and checksums;
- offline suite, representative-header, target lifecycle, calibrated review,
  adversarial review, and public-download verification results;
- installation, signing, permissions, diagnostics, update, downgrade, rollback,
  recovery, removal, and residue outcomes;
- compatibility state/reason and why each route/mode is or is not live eligible;
- every hardware, system, service, reboot, GPIO, DMA, transmission, SDR, RF,
  Git, tag, push, release, and issue action performed and explicitly not
  performed;
- licensing, SPDX, provenance, UAPI, schema, documentation, security, and
  qualification impact;
- final state of every target and worktree, including dirty/staged/committed/
  pushed/tagged/published status; and
- unresolved validation and the next separately authorized gate.

Do not report Phase 5 complete while a required representative identity,
calibrated claim, adversarial finding, target cleanup, published-artifact
verification, canonical-UAPI integration, or release-ordering gate remains
open.
