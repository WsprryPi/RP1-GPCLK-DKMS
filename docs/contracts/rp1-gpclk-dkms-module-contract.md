<!-- SPDX-License-Identifier: MIT -->

# RP1 GPCLK DKMS module engineering contract

Status: Phase 1 architectural authority
Project: [`WsprryPi/RP1-GPCLK-DKMS`](https://github.com/WsprryPi/RP1-GPCLK-DKMS)
Product tracker: [`WsprryPi/WsprryPi#412`](https://github.com/WsprryPi/WsprryPi/issues/412)
Corollary product contract: [RP1 GPCLK stock-kernel DKMS contract](https://github.com/WsprryPi/WsprryPi/blob/eb1c933ec20147aae987f06a2b8e4f1d988c00f6/docs/research/rp1-gpclk-stock-kernel-dkms-contract.md)

## 1. Purpose and authority

This document translates the WsprryPi product contract into the engineering,
licensing, release, and evidence contract for the standalone kernel-module
project. It governs implementation inside `RP1-GPCLK-DKMS`.

The WsprryPi contract remains authoritative for application behavior,
operator-facing policy, integration, and product qualification. This document
is authoritative for module internals, the canonical UAPI, DKMS packaging,
overlays, module compatibility metadata, and module release artifacts. If the
contracts conflict, work stops until both repositories receive a reviewed,
coordinated amendment; neither contract silently overrides the other.

This contract does not itself authorize installation, loading, binding, system
changes, GPIO output, transmission, or RF activity. Each target phase requires
separately bounded authorization. Phase 5.1 tasks may separately authorize
offline packaging work and representative DKMS/signing/install/overlay/update/
rollback/removal lifecycle administration. That lifecycle authority remains
clock/output-disabled unless an exact test receives additional live-output
authorization; it never implicitly authorizes GPIO output or RF.

## 2. Intended deliverable

The deliverable is source for a stock-kernel-compatible out-of-tree Linux
module, normally compiled locally for the operator's installed kernel through
DKMS. It supplements rather than replaces the stock Raspberry Pi `clk-rp1`
driver. WsprryPi will not distribute or maintain a custom kernel for this
feature.

Every release unit includes all of the following; the machine-readable
installation inventory in
[`release/release-layout-v1.json`](../../release/release-layout-v1.json) freezes
the exact destination, owner, group, mode, replacement policy, and removal
owner for each item:

- a versioned deterministic source archive and one versioned archive root;
- module source and internal headers, `Kbuild`, `Makefile`, and finalized
  `dkms.conf`;
- the canonical versioned UAPI header;
- GPIO4 and GPIO20 overlay source plus reproducibly generated DTBO files;
- the compatibility-manifest schema and populated release compatibility
  manifest;
- provenance and checksum manifests;
- installation, update, downgrade, rollback, recovery, complete-removal, and
  read-only diagnostic tooling;
- module-signing and administrator key-enrollment guidance;
- operator documentation and security/behavioral release notes; and
- machine-readable release metadata and restrictive device-node policy.

Each generated release identity binds the module release, exact source commit,
expected release tag, UAPI ABI and canonical-header hash, overlay source and
DTBO hashes, source-archive hash, compatibility-manifest hash, installation
inventory hash, and every byte-affecting build-tool identity and option. A
mismatch among the source version, `dkms.conf`, `MODULE_VERSION`, UAPI,
manifest, release metadata, release tag, archive root, or archive name fails
validation. Generated compatibility, provenance, checksum, and release
metadata remain sidecars so their hashes do not create a cyclic archive hash.

An artifact is not implemented or qualified merely because it is enumerated in
this contract or inventory; the release generator, validator, and applicable
evidence gates must pass for its exact identity.

## 3. Repository ownership

### This repository owns

- loadable kernel-module source;
- kernel-facing validation, state, lifetime, and cleanup logic;
- Kbuild and DKMS configuration;
- device-tree overlay sources and module-specific route binding;
- the canonical additive UAPI and capability identifiers;
- module compatibility identities and artifact provenance;
- kernel-header builds, static checks, KUnit or equivalent kernel tests, and
  clock-disabled module-lifetime tests;
- module signing and lifecycle tooling; and
- module-specific releases, security reports, and kernel-compatibility issues.

### `WsprryPi/WSPR-Transmitter` owns

- its userspace provider adapter;
- transmission planning and conversion into the bounded UAPI;
- application-side lifecycle and terminal-reason handling;
- compatibility checks against reported module capabilities; and
- adapter tests using fakes or mocks rather than embedded kernel source.

### `WsprryPi/WsprryPi` owns

- physical-backend selection and fail-closed product policy;
- persisted GPIO4/GPIO20 selection;
- scheduling and integration;
- installer orchestration for an explicitly compatible tagged module release;
- operator enrollment, warnings, diagnostics, support bundles, and recovery
  workflow; and
- product qualification and release decisions.

Repositories keep separate branches, reviews, commits, releases, issue
lifecycle, and qualification claims. This repository must not vendor
WsprryPi's application source, and WsprryPi must not vendor this complete
module source tree.

## 4. Licensing contract

The project owner intends original work to remain MIT-licensed wherever
practical without misrepresenting Linux kernel integration or imported GPL
material.

- Original module and kernel-facing source uses
  `SPDX-License-Identifier: GPL-2.0-only OR MIT`.
- The module declares `MODULE_LICENSE("Dual MIT/GPL")`.
- Original userspace-visible UAPI headers use
  `SPDX-License-Identifier: (GPL-2.0-only WITH Linux-syscall-note) OR MIT`.
- Independent original tools, tests, documentation, schemas, and metadata use
  `SPDX-License-Identifier: MIT`.
- Original device-tree sources use `GPL-2.0-only OR MIT` unless their actual
  derivation requires a narrower license.
- Imported or adapted code retains its upstream license and provenance. Linux
  kernel or other GPL-only material must not be relabeled MIT.

The SPDX identifier in each file is authoritative. `MODULE_LICENSE()` is
loader metadata, not a substitute for source licensing. See the root
`LICENSE.md` and included license texts.

## 5. Stock-kernel ownership limitation

The historical custom kernel placed a private GPCLK lease inside `clk-rp1`.
This out-of-tree consumer cannot acquire the provider's private register lock
or reproduce that exclusion exactly.

Specifically:

- exclusive-rate protection does not grant exclusive clock-enable ownership;
- clock prepare and enable counts are shared;
- no supported consumer API closes every race between clock-state inspection
  and output-route selection;
- DMA writes to `DIV_FRAC` bypass the stock clock driver's private register
  lock; and
- direct-MMIO software can bypass common-clock, pinctrl, and DMAengine
  arbitration.

The module must acquire every supported resource exclusively where exported
APIs permit, reject every conflict it can observe, and state the residual risk.
It must never claim that a clean run proves the absence of competing software.

## 6. Component architecture

```text
WsprryPi planner and scheduler
             |
      bounded versioned UAPI
             |
     RP1-GPCLK-DKMS module
       |        |        |
   DMAengine  pinctrl  common-clock
       |                   |
 validated GPCLK0      stock clk-rp1
 DIV_FRAC target
```

The module owns:

- version, size, bounds, route, state, and capability validation;
- one userspace owner and generation at a time;
- finite kernel-owned DMA work and the allocated DMA channel;
- selected-route pinctrl states;
- supported clock preparation, rate protection, and balanced enable
  references;
- cancellation, bounded drain, completion, and cleanup;
- file, device, callback, unbind, and module lifetime; and
- stable terminal states and diagnostics.

The module must not expose arbitrary physical addresses, DMA-channel
selection, raw register access, unrestricted programs, or general-purpose RP1
control to userspace.

## 7. Resource derivation and exported-API rule

Production dependencies must be supported exported kernel APIs for the exact
compatibility identity. Visibility in one kernel build does not make an
internal symbol a product contract. Kprobes and private-symbol discovery may
inform bounded research but are rejected as production dependencies.

The module must:

1. parse and validate its clock phandle and arguments;
2. require the expected RP1 clock provider and exactly GPCLK0;
3. translate the authoritative provider resource through device tree;
4. validate compatible identity, resource size, allowlisted offsets,
   containment, and checked arithmetic;
5. derive the CPU-physical fractional-divider target from the validated
   resource rather than a fixed absolute address;
6. use the proven DMAengine slave path for required RP1 DMA translation; and
7. reject every unexpected provider, clock ID, resource, offset, or
   translation.

Exact divider readback must use the validated DMA-owned readback path when the
design directly changes the divider. `clk_get_rate()` is not exact direct-write
readback.

## 8. Route contract

Stable conceptual route identities are:

```text
RP1_GPCLK_ROUTE_GPIO4  = 1
RP1_GPCLK_ROUTE_GPIO20 = 2
```

The numeric values are frozen by Phase 3 Decision 0006. They are additive and
must not be repurposed.

Requirements:

- only explicit allowlisted routes are accepted;
- arbitrary GPIO numbers are rejected;
- code, UAPI, diagnostics, and packaging remain route-neutral;
- a capability query reports the bound route and relevant compatibility
  identity;
- application selection must match the administratively bound route;
- route changes are rejected while acquired, running, or draining;
- one route must not reserve the other without reviewed target evidence; and
- GPIO4 and GPIO20 have independent compatibility and qualification records.

Exactly one production route overlay may be selected in persistent
configuration. Production overlays expose no arbitrary GPIO parameter and no
automatic route substitution. Their source and DTBO hashes and their exact
compatible, endpoint, route, pin, clock, DMA, resource, and safe/default
pinctrl identities are release identities. Deterministic compilation and
semantic verification of the compiled artifact are both required.

Conflict detection precedes every persistent route-configuration change. A
bound route is never mutated in place. Changing routes is a controlled
lifecycle: prove the module and endpoint idle; disable live eligibility;
remove the old binding through the proven cleanup path; verify GPIO4 and
GPIO20 safe; select the one new overlay; revalidate the entire compatibility
identity; and renew enrollment whenever policy requires it. Failure stops the
transition with live output disabled. Qualification or enrollment for one
route never authorizes the other.

The preferred boundary is one selected route per boot/admin overlay, exposing
only that route's pinctrl mapping. GPIO4 is the Phase 2 feasibility route.
GPIO20 enters during Phase 3, after GPIO4 feasibility and before interfaces,
overlays, manifests, installation, or documentation are frozen.

## 9. UAPI contract

The project starts a clean DKMS ABI under
[Decision 0001](../development/decisions/0001-clean-dkms-uapi.md). Historical
ioctl numbers and layouts are evidence rather than compatibility obligations;
no legacy dispatcher is part of the initial design.

The UAPI is bounded, versioned, additive, route-neutral, and canonical in this
repository. It includes:

- explicit API version and structure-size validation;
- capability and compatibility identity reporting;
- bounded tone/event tables and duration limits;
- single-owner acquisition and release;
- generation identifiers and stale-generation rejection;
- idle, running, draining, complete, and failed states;
- explicit STOP and RELEASE operations; and
- stable terminal-reason identifiers.

Released fields, values, flags, states, sizes, offsets, and meanings are never
silently reused. Reserved fields remain reserved until an additive reviewed
revision assigns them.

If `WSPR-Transmitter` requires a compatibility copy, CI must compare the
selected release's header bytes and semantic identity, including versions,
ioctls, sizes, offsets, flags, states, reasons, and capabilities. Any mismatch
fails; it is never normalized silently.

## 10. Lifetime and cancellation

The implementation explicitly protects:

- module versus open descriptor;
- platform device versus open descriptor;
- active generation versus owner close or process death;
- DMA callback versus terminal generation;
- unbind or overlay removal versus active work; and
- managed resource lifetime versus provider-object lifetime.

The module owner field alone does not make platform unbind safe. Removal needs
a dead state, misc-device deregistration, synchronous hardware quiescence, and
reference-counted object lifetime until every open descriptor closes.

Cancellation follows the previously validated bounded-drain model unless exact
target evidence establishes a safer replacement:

1. latch STOP or failure;
2. prevent a successor descriptor;
3. permit at most the defined finite current descriptor to drain;
4. verify a stable final divider through the DMA-owned readback path;
5. stop pacing and release DMA in validated order;
6. restore clock state through supported common-clock operations;
7. place the selected pin in its defined safe state; and
8. publish exactly one terminal reason.

Cleanup releases only resources acquired by this module. It must not overwrite
another consumer's later state using an earlier snapshot.

## 11. Compatibility contract

States are:

- `Qualified`: the exact model, kernel identity, device tree, route, module,
  mode, timing, cleanup, recovery, and RF evidence passed;
- `Experimental`: clock-disabled gates passed and an administrator explicitly
  accepts residual coexistence risk;
- `Compatible-unqualified`: build and identity checks pass, but live output is
  disabled;
- `Unavailable`: required headers, APIs, build, signature, resource, overlay,
  or hardware contract is absent; and
- `Rejected`: a known unsafe layout, conflict, startup state, self-test,
  cleanup, or compatibility result exists.

A successful build never promotes beyond `Compatible-unqualified`. Unknown
kernel, device-tree, overlay, module, or relevant firmware identities demote a
combination unless an explicit compatibility rule covers them. Cleanup failure
latches `Rejected` until remediated. Only complete recorded evidence can mark
an exact combination `Qualified`.

## 12. DKMS, signing, and release contract

DKMS builds the module locally for each installed kernel. GLIBC is not the
controlling compatibility boundary; headers, kernel configuration, exported
symbols, compiler expectations, architecture, vermagic, module ABI, signing,
device tree, firmware, and runtime behavior are.

The packaging gate requires the predeclared, machine-readable representative
system matrix in
[`release/representative-system-matrix-v1.json`](../../release/representative-system-matrix-v1.json).
One Pi and one kernel cannot close it. Before target testing, the matrix must
name at least: the current supported Raspberry Pi OS kernel; a prior supported
kernel and downgrade; a newer unknown kernel and demotion; signing not enforced;
signing enforced with an enrolled key; deliberate build failure; deliberate
signature rejection; missing headers; an overlay or resource conflict; an
interrupted upgrade; a stale manifest; corrupted archive and route-specific
DTBO attempts; removal while inactive; refused removal while open or active;
and reinstall after proved complete removal.

Every row freezes the system selection, preconditions, injection, exact
compatibility state and reason, live gate, transaction state, cleanup result,
prior-version retention, required diagnostics, allowed changes, final state,
and residue audit. Missing or indeterminate evidence, an unexplained delta, or
cleanup ambiguity fails the row. Rows are independent: evidence for one
kernel, signing policy, route, failure, or lifecycle transition cannot satisfy
another. All representative lifecycle rows remain output-disabled and cannot
create `Qualified` or RF evidence.

Kernel updates may trigger a rebuild. Build success does not preserve
qualification automatically. Build, signing, or load failure leaves the module
unavailable and must not select another physical backend.

Strict module-signing systems require a documented trusted local signing and
key-enrollment workflow. A valid signature demonstrates provenance and load
eligibility, not behavioral safety.

Every consumable release must be tagged and include:

- exact source and UAPI versions;
- cryptographic checksums and artifact provenance;
- supported build identities and explicit exclusions;
- compatibility-state implications;
- installation, rollback, and complete-removal instructions; and
- security and behavioral release notes.

A release candidate is not a consumable release. A candidate is one exact
reviewed commit plus a sealed deterministic archive and its checksum; it may be
used for authorized qualification before a release exists. An expected tag, a
local tag, reproducible bytes, or locally verified checksums do not establish
publication. A published release exists for consumers only after the module
publication gate passes, the reviewed tag and immutable artifacts are public,
and every downloaded public artifact passes fresh outer and inner checksum,
provenance, archive-layout, and install-input verification.

The module publication gate requires the full offline suite, complete
representative lifecycle matrix, closed independent adversarial review,
independent artifact reproduction, exact tag/internal-version agreement,
post-download checksum verification, a real populated compatibility manifest,
verified install/rollback/recovery/removal instructions, documented known
limitations, and a claim-to-evidence audit with no over-broad statement. A
missing, failed, stale, or indeterminate prerequisite leaves the identity a
candidate. Published bytes are immutable under their version and tag.

WsprryPi consumes only an explicitly allowed release artifact through its
compatibility manifest. Module publication precedes the dependent WsprryPi
release, which records the allowed module/UAPI range and exact artifact
identity.

After confirmed module publication, `WSPR-Transmitter` first consumes the
canonical UAPI and exact module release and passes byte-for-byte and semantic
ABI checks. WsprryPi then pins the exact downloaded archive/tag/checksum,
compatibility-manifest identity, UAPI identity, and reviewed adapter identity.
Application integration qualification follows under separate authority;
dependent adapter and application releases follow only after their respective
evidence and reviews pass. Each repository retains separate commits, reviews,
tags, releases, and qualification claims.

## 13. Security and operator responsibility

- The device node is root-owned and restrictive, normally mode `0600`.
- Only one process owns an acquired generation.
- Live output defaults disabled.
- Experimental operation requires durable explicit administrator acceptance.
- Installation must not silently blacklist or disable unrelated drivers.
- Known resource conflicts are diagnosed and rejected where possible.
- Runtime overlay removal is unsupported until removal lifetime is proven.
- Operators must exclude uncoordinated software that manipulates RP1 GPCLK0,
  the selected pinmux, relevant DMA-tick resources, the allocated DMA channel,
  or RP1 clock registers through direct MMIO.

Warnings must describe the limits of conflict detection. They are not a
substitute for technical ownership and cannot promise safe cohabitation.

## 14. Failure-test minimum

At minimum, test:

- unsupported provider, compatible, clock ID, resource, or offset;
- arithmetic overflow and invalid DMA translation;
- unavailable DMA channel, DMA-tick resource, pinctrl state, or clock;
- selected pin or GPCLK0 rate already claimed;
- GPCLK0 initially enabled or retained by another consumer;
- every allocation, mapping, preparation, and submission failure point;
- cancellation at every descriptor boundary;
- stale callbacks after completion, failure, and owner loss;
- invalid UAPI version, size, route, state, duration, and table bounds;
- process death, descriptor close, unbind, and removal while open or active;
- prohibited overlay removal;
- signing rejection and DKMS build/install failure;
- kernel upgrade and downgrade;
- cleanup or readback failure; and
- direct-MMIO interference as explicitly not exhaustively detectable.

Every test defines expected terminal reason, maximum residual activity, final
pin and clock state, owned-resource release, retained failure latch, and exact
evidence identity.

## 15. Phased execution and gates

The authoritative sequence is maintained in the repository's
[phased plan](./phased-plan.md):

1. contract and feasibility design;
2. GPIO4 clock-disabled prototype;
3. GPIO20 injection before interface freeze;
4. timing and separately controlled live qualification; and
5. packaging and operator enablement.

Offline work may implement portions of later phases but cannot close a target
gate without its required target evidence. Module binding requires explicit
authorization even while output remains disabled. Phase 4 inherently requires
separate GPIO and RF authorization.

## 16. Adversarial review rule

At every phase exit, conduct a separate assessment attempting to falsify:

- exported API availability and stability;
- provider, resource, offset, and DMA translation identity;
- claimed ownership and absence of conflicts;
- clock prepare, enable, rate, restoration, and readback assumptions;
- route isolation and GPIO20 independence;
- UAPI bounds, additive compatibility, and cross-repository identity;
- cancellation, callback, cleanup, unbind, and open-file lifetime;
- signing, DKMS, update, rollback, and removal safety;
- release provenance and manifest integrity; and
- every compatibility and qualification claim.

Inject each failed assertion into the phase specification and repeat affected
work. A passing review validates only the evidence actually examined; it does
not qualify untested hardware behavior.

## 17. Persistent non-goals

- No maintained custom kernel.
- No replacement of the stock `clk-rp1` provider through DKMS.
- No `/dev/mem`, raw userspace MMIO, or private-symbol production dependency.
- No complete exclusion claim against direct-MMIO or hostile kernel software.
- No arbitrary GPIO routing.
- No qualification inferred from build success or another route/kernel.
- No automatic fallback to another physical transmitter backend.
- No pre-Pi 5 GPIO driver in this project without a later reviewed boundary
  decision.
- No live GPIO, transmission, or RF work without separately bounded
  authorization.

## 18. Next implementation gate

Phase 2 is closed only for the exact GPIO4 clock-disabled identity recorded in
`docs/evidence/phase2e-clock-disabled-target.md`. Phase 3 GPIO20 injection and
the first public interface freeze are implemented offline under Decision 0006.
Phase 3B closes the Phase 3 target exit only for the exact clock-disabled
identity recorded in `docs/evidence/phase3b-clock-disabled-route-closure.md`.
GPIO4 and GPIO20 use independent allowlisted routes and evidence rows; the
successful two-route matrix does not let either route inherit the other's
qualification.

Phase 3 does not authorize active pinctrl selection, clock preparation or
enablement, DMA execution, GPIO output, transmission, or RF. Phase 4 live
qualification retains separately bounded GPIO and RF authorization gates.
