<!-- SPDX-License-Identifier: MIT -->

# Phase 2A public-contracts and source-skeleton execution prompt

## Role and outcome

Act as the public-interface architect, kernel build maintainer, and adversarial
reviewer for `WsprryPi/RP1-GPCLK-DKMS`. Complete the offline-only Phase 2A
foundation needed before any functional resource acquisition or hardware
control is written.

The outcome is a canonical, additive UAPI; a machine-readable compatibility
manifest schema; a route-neutral kernel source and Kbuild skeleton; explicit
kernel-API seams; and deterministic identity, licensing, provenance, and
contract checks. It is not a working GPCLK driver.

## Authorities and precedence

Read and obey, in order:

1. `AGENTS.md`;
2. `docs/contracts/rp1-gpclk-dkms-module-contract.md`;
3. `docs/contracts/phased-plan.md`;
4. `docs/development/decisions/0001-clean-dkms-uapi.md`;
5. `LICENSE.md`, `docs/development/provenance.md`, and
   `docs/development/uapi-baseline.md`; and
6. this prompt.

Stop on a conflict rather than silently weakening a higher authority.

## Authorized work

- Resolve and document the first public ABI's namespace, names, versions,
  structure-growth rule, operations, capabilities, states, terminal reasons,
  routes, limits, and fixed-width layouts.
- Create the canonical userspace-visible header with no raw addresses, DMA
  selection, arbitrary register access, arbitrary GPIO selection, or
  unrestricted programs.
- Define a strict compatibility-manifest JSON Schema and a non-qualifying
  example that keeps build identity, runtime identity, route, mode, evidence,
  and compatibility state distinct.
- Create a route-neutral source tree and external-module Kbuild skeleton.
- Make the common-clock, DMAengine, pinctrl, device-tree/resource, lifetime,
  and userspace-dispatch seams explicit, but leave them unavailable stubs.
- Add deterministic offline checks for SPDX policy, source provenance, public
  header identity, UAPI sizes/numbers, forbidden interfaces, schema examples,
  and whitespace.
- Update documentation so status and limitations are truthful.

## Prohibited work

Do not install, load, bind, unbind, unload, or replace a kernel module; apply an
overlay; run DKMS; use mutating `sudo`; alter boot, signing, udev, systemd, or
kernel configuration; access a Raspberry Pi; allocate or program DMA; acquire
a clock or pinctrl state; map registers; change GPIO state; transmit; or
produce RF output. Do not add a `/dev/mem`, raw-MMIO, private-symbol, kprobe,
custom-kernel, or WsprryPi-source dependency.

The module skeleton must remain inert: module initialization may identify the
skeleton in the kernel log, but it must register no platform/misc device,
create no node, bind no resource, and expose no ioctl dispatcher.

## Public-contract rules

- Use a new ioctl namespace, not historical magic `0xb7` or its layouts.
- UAPI version 1 uses a common `{size, version, flags}` request prefix.
- The `_IOC_SIZE` is immutable, so structure growth uses a new ioctl command;
  reserved fields are zero and never silently repurposed.
- Query reports ABI range, module/build identity, bound route, compatibility,
  limits, capabilities, and a stable rejection reason without raw addresses.
- Acquisition returns an opaque nonzero lease ID. Submission returns a
  lease-scoped nonzero generation. Commands reject stale lease/generation IDs.
- Work is finite and bounded. WSPR symbols and general events are separate
  operations; modes and routes are explicit identities, not arbitrary inputs.
- State and terminal reason are separate. Exactly one stable reason is
  published for terminal completion or failure.
- Live eligibility is an explicit capability and manifest fact; build success
  alone never grants it.
- Compatibility records are deny-by-default and exact. Unknown prerequisites
  are `Unavailable`; known unsafe combinations are `Rejected`.

## Required deliverables

1. A reviewed decision record freezing Phase 2A public choices and explicitly
   listing what remains unfrozen.
2. `include/uapi/linux/rp1_gpclk.h` as the sole canonical UAPI.
3. `schema/rp1-gpclk-compatibility-manifest-v1.schema.json` and a valid example.
4. `src/` and `include/rp1_gpclk/` seams plus `Kbuild` and root `Makefile`.
5. Offline tests/checks in `tests/` and a checked UAPI identity record.
6. README/status and provenance updates.

## Validation

Inspect every command before running it. Run only offline, unprivileged,
hardware-free checks. At minimum verify:

- all newly governed files have the correct SPDX identifier;
- the UAPI compiles in userspace and its sizes, offsets, enum values, ioctl
  magic, numbers, directions, and encoded sizes match the frozen contract;
- a byte-different consumer copy fails identity checking;
- valid and deliberately invalid manifests behave as expected;
- kernel skeleton sources contain no forbidden hardware/control interface;
- Kbuild lists the intended inert objects; and
- whitespace and documentation links are clean.

A representative kernel-header build may be run only when explicitly
identified headers already exist locally. Record it strictly as compilation
evidence. Its absence does not authorize downloads or target access.

## Adversarial assessment and reinjection loop

After implementation, independently attempt to falsify:

- that ABI growth is actually additive and architecture-independent;
- that every public numeric value and semantic is documented and tested;
- that queries cannot leak raw resource addresses or overstate eligibility;
- that event/tone arithmetic is bounded and WSPR-specific limits do not infect
  general events;
- that route neutrality preserves independent GPIO4/GPIO20 identities without
  implementing either route;
- that compatibility matching is exact, deny-by-default, and unable to turn a
  build into qualification;
- that the skeleton can neither bind nor control hardware;
- that future clock, DMA, pinctrl, DT/resource, dispatch, and lifetime work has
  explicit fail-closed seams;
- that UAPI copies and identity records cannot drift silently;
- that SPDX and provenance match the licensing contract; and
- that documentation distinguishes implemented skeleton, plans, non-goals,
  and outstanding target validation.

For every objective failure, amend this prompt's requirements or frozen
decision as appropriate, implement the correction, rerun affected checks, and
repeat the full assessment. Exit only when there is no uncorrected finding.

### Requirements reinjected after adversarial pass 1

- Use explicitly 8-byte-aligned 64-bit UAPI fields so layouts remain identical
  on 32-bit and 64-bit consumers.
- Freeze a compatibility-reason enum separate from runtime terminal reasons.
- Never use placeholder hashes or historical numeric observations as manifest
  evidence; the Phase 2A example has no compatibility entries.
- A `Qualified` schema entry requires build, clock-disabled, timing, cleanup,
  recovery, and RF evidence classes in addition to live eligibility.

### Requirements reinjected after adversarial pass 2

- Tone entries must preserve bounded lower/upper Q16 divider dithering and its
  counts; one integer/fraction field cannot represent the required plan.
- The fixed DMA tick divider is a request-level contract value, not an
  event-local write count. General events contain duration, tone identity, and
  output flag only.

### Requirements reinjected after adversarial pass 3

- Distinguish literal milliamp request values from query bitmap bits in names
  and values, and report the supported drive allowlist explicitly.
- Name the query limit as a dithering-period bound, not an event-write count.

## Exit report

Report changed behavior/files, exact checks and results, skipped or unavailable
checks, the adversarial iterations and corrections, hardware/system/GPIO/RF
work explicitly not performed, licensing/documentation impact, unresolved
validation, next gated step, and exact Git state. Do not stage, commit, push,
publish, or create a pull request.
