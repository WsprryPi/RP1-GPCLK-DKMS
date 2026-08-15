<!-- SPDX-License-Identifier: MIT -->

# Phase 4A stock-kernel live-path implementation execution prompt

## Mission and hard stop

Act as the kernel-module implementer, safety reviewer, test author, build
qualification operator, and evidence custodian for
`WsprryPi/RP1-GPCLK-DKMS`.

Implement and adversarially validate the frozen ABI v1 stock-kernel live path.
Finish with a clock-disabled regression on the exactly authorized `wspr5`
target and a complete evidence bundle. Stop before the first GPIO4 burst.

This prompt never authorizes active pinctrl selection, clock preparation or
enablement, DMA submission to live hardware, GPIO output, SDR capture,
transmission, or RF. Gate C may already be recorded, but it cannot be exercised
inside Phase 4A. The next phase begins only after a separate review accepts the
exact Phase 4A source and evidence identity.

## Exit gate

Phase 4A passes only when:

- the live path is implemented using stock-kernel exported APIs and validated
  DT-derived resources, with no custom-kernel or private-symbol dependency;
- ABI v1 validation, ownership, generation, state, finite-work, DMA,
  cancellation, readback, restoration, and cleanup contracts have deterministic
  tests and representative kernel builds;
- capabilities remain truthful and `LIVE_ELIGIBLE` is unavailable on the
  clock-disabled target configuration;
- the complete Phase 3B two-route clock-disabled matrix passes against the
  exact new bytes on `wspr5` without executing the new live path;
- the target returns to the verified absent/safe baseline;
- portable checksummed evidence reproduces after relocation;
- a separate adversarial assessment has no unresolved objective finding; and
- the final Git diff, source identity, build artifacts, tests, documents, and
  evidence all correspond.

Any failure leaves Phase 4A open. Build success cannot promote compatibility
above `Compatible-unqualified` and cannot qualify GPIO, timing, modes, or RF.

## Authority and immutable inputs

Read completely and follow, in order:

1. `AGENTS.md`;
2. `docs/contracts/rp1-gpclk-dkms-module-contract.md`;
3. `docs/contracts/phased-plan.md`;
4. `docs/contracts/uapi-v1.md`;
5. `docs/contracts/phase4-timing-controlled-live-output-execution-prompt.md`;
6. Decisions 0004, 0005, and 0006;
7. Phase 2D, Phase 2E, and Phase 3B evidence and adversarial reviews;
8. `include/uapi/linux/rp1_gpclk.h` and `uapi-identity.json`; and
9. the compatibility-manifest schema and route-isolation rules.

ABI v1 bytes, ioctl numbers, layouts, sizes, offsets, flags, enums, routes,
states, reasons, capabilities, and reserved fields are frozen. Overlay names,
DT compatible/properties, module/device names, and public identity vocabulary
are also frozen unless a reviewed contract defect requires stopping this phase.
Do not alter a frozen contract merely to make implementation convenient.

At entry, production dispatch implements only `QUERY`, `ACQUIRE`, and
`RELEASE`; other commands return `EOPNOTSUPP`; capabilities are `0x70`; and
`rp1_gpclk_quiesce()` is inert. The portable core models more behavior than the
kernel-facing implementation. Never advertise modeled behavior as implemented.

Historical WsprryPi provider code and downstream-kernel patches are research
evidence only. Preserve their provenance and licensing. Do not copy their
custom `rp1_gpclk_dma_lease_*` API, provider-private state, fixed-address
assumptions, or GPL-only material under a different license.

## Repository and target boundaries

- Work only in this repository. Do not modify or vendor WsprryPi application
  or transmitter source.
- Preserve all pre-existing untracked Phase 4 documents and all unrelated user
  work. Inspect the complete diff before every phase exit.
- Offline work is unprivileged, repeatable, network-free, and hardware-free.
- Gate B authorization permits `wspr5` build/install/sign/load/bind/unbind/
  unload/removal, only the GPIO4/GPIO20 test overlays, and disposable test,
  signing, and evidence files. It forbids boot changes, reboot, service changes,
  and all GPIO/RF output.
- Do not stage, commit, push, tag, release, or publish until the exit gate and
  explicit publication condition are satisfied.

## Required design record before implementation

Write a reviewed decision describing:

1. the exact stock-kernel exported APIs used for clock, DMAengine, pinctrl,
   timing, synchronization, allocation, and lifetime;
2. authoritative DT nodes/resources for GPCLK0, `DIV_FRAC`, DMA TICK0 pacing,
   and the DMA request, including provider identity, offsets, sizes,
   containment, translation, and exclusive ownership;
3. whether adding named DMA-tick resources or properties is compatible with
   Decision 0006. If not, stop for an explicit additive DT/overlay contract
   decision and update both route overlays and all negative fixtures
   symmetrically before implementation;
4. why any module MMIO mapping is necessary, bounded, DT-derived, non-overlap
   checked, and limited to module-owned DMA-tick control—not arbitrary RP1 or
   clock-provider access;
5. common-clock prepare/rate/enable semantics and the residual race because
   exclusive rate ownership is not exclusive enable ownership;
6. initially enabled/claimed clock rejection and cooperative-consumer conflict
   behavior;
7. active/safe pinctrl ordering and how output-disabled events are implemented
   without sleeping in atomic context or creating enable-reference imbalance;
8. finite DMA program shape, maximum allocation, pacing equation, descriptor
   boundaries, callback context, and deadline model for WSPR and event modes;
9. exact device-to-memory `DIV_FRAC` readback, value packing, comparison, and
   why `clk_get_rate()` is insufficient;
10. initial-divider capture and restoration through supported common-clock
   operations without overwriting a later consumer from a stale snapshot;
11. STOP, owner-close, process-death, unbind, callback, and removal ordering;
12. cleanup-fault latching and the only permitted recovery path;
13. an immutable-at-load, default-disabled live-output enrollment gate. When
    disabled it must reject submission before pinctrl, clock, tick, DMA, or
    hardware allocation/mutation while leaving query/state diagnostics useful;
    it cannot be enabled through sysfs or an ioctl after load; and
14. compatibility identity and the condition that eventually permits
    `LIVE_ELIGIBLE`—which Phase 4A must not enable on `wspr5`.

If exported APIs plus validated DT resources cannot establish a bounded
stock-kernel contract, stop with `Unavailable`. Never fall back to `/dev/mem`,
raw userspace MMIO, a custom kernel, kprobes, private symbols, another physical
backend, or an unsupported fixed address.

## Implementation workstreams

### 1. Request ingestion and validation

- Implement `SUBMIT_WSPR` and `SUBMIT_EVENTS` with exact header, version, size,
  flag, reserved-field, pointer, count, mode, drive, duration, divider,
  dither-period, symbol, event, and checked-arithmetic validation.
- Copy user arrays exactly once into bounded kernel-owned storage. Retain no
  userspace pointers. Zero sensitive/freeable plan storage on release.
- Require four tones and 162 symbols for WSPR. Require QRSS, FSKCW, or DFCW for
  events; a constant TONE is one enabled QRSS event with one tone.
- Reject arbitrary dividers beyond the reviewed GPCLK0/source/rate envelope;
  adjacency and UAPI bounds alone are insufficient authorization.

### 2. Ownership, generations, and state

- Connect dispatch to the portable core without creating two authorities for
  hardware state.
- Maintain one file owner, one lease, and one active nonzero generation.
  Reject stale owner/lease/generation callbacks and ioctls.
- Implement `GET_STATE` as a stable, locked, side-effect-free snapshot with
  bounded elapsed/remaining calculations and one terminal reason.
- Implement `STOP` as generation-specific, idempotent only for the same stopped
  terminal generation, and unable to admit successor work.
- Make close, process death, unbind, and removal converge through one reviewed
  quiescence state machine without use-after-free or double cleanup.

### 3. Finite DMA and pacing

- Allocate bounded coherent or mapped kernel buffers using checked products and
  explicit maximum bytes. Never allocate from unbounded durations.
- Generate deterministic divider words with proved Q16 packing and exact
  per-tone dither counts. Prove no skipped, duplicated, or extra word.
- Configure only the DT-selected DMA channel and validated `DIV_FRAC` target.
  Validate direction, bus width, burst, cookies, completion, residue semantics,
  and DMA mapping device.
- Own, configure, start, stop, and restore only the validated DMA TICK0 pacing
  resource. Reject any conflicting owner or unexpected register state.
- Use generation-tagged callbacks and synchronous teardown. A callback may
  publish progress only for the current live generation.

### 4. Clock, pinctrl, readback, and restoration

- Reject unsafe initial GPCLK0 state before mutation. Record rate/parent and
  module-owned reference transitions without claiming provider-private state.
- Prepare/configure while the selected pin is safe; keep output gated until the
  finite program and cancellation path are armed; activate only the bound
  route; and reverse the order during cleanup.
- Use only sleepable or atomic-safe APIs in their permitted contexts. Defer
  sleepable cleanup to synchronized work when necessary.
- Drain at most the defined finite current descriptor, prevent a successor,
  read back the exact final divider by DMA, stop pacing, disable/unprepare,
  restore supported clock state, select safe pinctrl, and release owned
  resources.
- Prove the unselected route is never requested or changed.
- Treat readback, cleanup, or restoration ambiguity as failure and latch
  `Rejected`; do not turn a later nominal result into a pass.

### 5. Capability and compatibility truthfulness

- Add submission, STOP/drain, and stable-state capability bits only when the
  corresponding production code and tests exist.
- Keep `LIVE_ELIGIBLE` clear and live hardware activation administratively
  impossible throughout Phase 4A and the Gate B regression.
- Separate implemented-operation capability from live eligibility precisely:
  under the default-disabled enrollment gate, submission must return the
  documented compatibility rejection before hardware mutation even if its
  parser/state-machine code exists. Tests must prove the ordering.
- Report a new immutable build/compatibility identity for the tested source.
  Unknown kernel/DT/module/UAPI combinations remain non-live.
- Ensure failure cannot select another physical backend.

## Deterministic offline test matrix

Inspect every test before running it. Add host-side seams/fakes at the
clock/DMA/pinctrl boundary and test at least:

- every valid and invalid UAPI field, pointer-copy failure, zero/nonzero
  reserved byte, count boundary, duration overflow, allocation overflow,
  divider envelope, dither count, symbol, event, drive, mode, and route;
- lease/generation exhaustion, stale commands/callbacks, concurrent owners,
  repeated terminal calls, successor suppression, and stable snapshots;
- WSPR word generation and every QRSS/FSKCW/DFCW event boundary;
- cancellation before start, every descriptor boundary class, final
  descriptor, callback race, terminal publication, owner close, and removal;
- every allocation, clock, pinctrl, DMA map/config/prep/submit/callback,
  readback, deadline, restoration, and cleanup failure point;
- exact reverse-order unwind and release-only-if-acquired behavior;
- cleanup latch persistence and capability/compatibility demotion;
- GPIO4/GPIO20 route neutrality and unselected-route noninterference;
- tick/divider resource containment, overlap, translation, unknown identity,
  volatile-mask, and neighboring-register policy; and
- lifetime under sanitizer and deterministic stress/repetition.

Tests must assert terminal reason, maximum residual work, final pin/clock/DMA
model, plan release count, terminal publication count, latch state, and owned
resource balance—not only return codes.

## Build and static qualification

1. Run the complete offline suite twice with warnings fatal where supported.
2. Run SPDX, provenance/licensing, UAPI byte/semantic identity, manifest,
   overlay symmetry, route isolation, documentation links, ShellCheck, and
   whitespace checks.
3. Build against each repository-defined representative Raspberry Pi kernel
   header identity. Record kernel/config/package, architecture, compiler,
   module version, UAPI identity, vermagic, warnings, symbols, and hashes.
4. Inspect undefined symbols against the exact target exports. Visibility in
   one build is not a stable product API.
5. Statically prove the Phase 4A target runner cannot set `LIVE_ELIGIBLE`,
   select active pinctrl, prepare/enable/change GPCLK0, submit DMA, write tick
   controls, or produce output.
   Also prove every Gate B module load omits or explicitly disables the
   immutable live-output enrollment parameter.
6. Preserve exact commands and results, including skipped tools and host
   limitations. Do not interpret compilation as target qualification.

## Separate adversarial implementation assessment

After ordinary checks pass, perform a distinct review attempting to falsify:

- exported-API availability and atomic/sleeping context correctness;
- DT authority, containment, translation, tick ownership, and register scope;
- the claim that common-clock operations balance every module-owned reference;
- divider packing, DMA direction, pacing math, readback, and restoration;
- bounded allocation/work/drain and absence of a successor after STOP;
- owner/file/device/module/callback lifetimes and stale callback rejection;
- partial-failure unwind and cleanup-fault persistence;
- route neutrality and GPIO20 independence;
- UAPI immutability, capability truthfulness, and compatibility ceiling;
- licensing/provenance of every adapted idea or source fragment; and
- whether any test passes without proving the assertion named by the test.

Record every objective finding in a Phase 4A review. Reinject it into this
prompt or a reviewed decision, correct the implementation and tests, invalidate
affected evidence, rerun the complete affected matrix, and repeat assessment.
Ordinary green tests do not waive an adversarial finding.

## Authorized `wspr5` clock-disabled regression

Only after the offline adversarial gate passes:

1. Record the Gate B authorization, exact source/archive digest, clean/dirty
   state, target identity, boot ID, full dmesg baseline, both pin states,
   GPCLK0 rate/parent/prepare/enable/protect counts, overlays, modules, devices,
   clients, services, signing policy, headers, compiler, firmware, base FDT,
   and runtime DT.
2. Require GPIO4 and GPIO20 input/safe, all clock counts zero, no test module,
   overlay, device, holder, or conflict, and no active output.
3. Build warnings-fatal against the exact running headers. Compile/decompile
   and machine-check all production and negative overlays. Sign a disposable
   copy where supported and prove built/signed/installed/loaded byte identity.
4. Load with no overlay and prove no endpoint or state change.
5. Repeat the complete Phase 3B GPIO4 and GPIO20 clock-disabled matrices,
   including mismatch, conflicts, partial probe failures, process death,
   open-descriptor unbind/unload, repeated route changes, update-failure
   recovery, exact diagnostics, and per-transition baselines.
6. Query the new capabilities and require `LIVE_ELIGIBLE` absent. Invoke every
   submission/state/STOP operation through an inert qualification gate and
   require the reviewed fail-closed result without active pinctrl, clock, tick,
   or DMA action.
7. Run an inert instrumentation/evidence rehearsal only. Do not open the SDR or
   capture samples under Gate B.
8. Remove all test-owned assets and prove both pins safe, counts zero, no DMA,
   overlay, module, device, installed artifact, key, client, or unclassified
   dmesg delta. Do not alter services, boot configuration, or reboot.

Every command has a TERM deadline, KILL deadline, expected status, timestamps,
and cleanup armed before mutation. Stop and clean up on the first unexpected
state. Preserve every failed attempt separately.

## Evidence integrity and final review

Record source, module, UAPI, overlay, kernel, DT, tool, command, diagnostic,
authorization, and target identities with SHA-256 hashes. Generate the final
relative-path manifest only after writers close and disposable assets are
removed. Download the archive, verify its outer hash, extract it elsewhere,
verify every inner hash, and rerun deterministic analysis from preserved raw
inputs.

Perform a final adversarial assessment of the target ledger, exact diagnostic
classification, route independence, capability truthfulness, cleanup, archive
portability, and every claim. Reinject and rerun on any finding.

The final accepted state is still output-inhibited. Explicitly prove that no
active pinctrl selection, clock preparation/enable/rate change, live DMA/tick
execution, GPIO output, SDR capture, transmission, or RF occurred.

## Completion and handoff

Lead with pass/fail. Report changed files and behavior; exact tests/builds and
results; target and artifact identities; adversarial findings and reruns;
evidence archive/hash; licensing, UAPI, compatibility, and documentation
impact; final target state; all hardware/system/output actions performed and
not performed; unresolved validation; and the exact next gate.

Do not start GPIO4. Do not mark any route or mode `Qualified`. Do not commit or
push unless Phase 4A is complete, the exact tested bytes are reviewed, the
worktree/staged set is cleanly scoped, and publication is appropriate under the
current explicit authorization.
