<!-- SPDX-License-Identifier: MIT -->

# RP1 GPCLK DKMS module contract

## Purpose and authority

This document defines the engineering, ownership, safety, compatibility,
packaging, and release contract for `WsprryPi/RP1-GPCLK-DKMS`.

This repository is authoritative for the kernel module, canonical UAPI,
device-tree overlays, DKMS packaging, module lifecycle tooling, compatibility
metadata, and module-specific releases. WsprryPi remains authoritative for
application behavior, operator policy, scheduling, integration, and product
qualification. Conflicting contracts require an explicit coordinated change;
neither repository silently overrides the other.

Nothing in this contract authorizes installation, module loading, binding,
system configuration, GPIO operation, transmission, or RF activity.

## Product

The product is source for an out-of-tree Linux module built by DKMS against the
operator's installed stock Raspberry Pi kernel. It supplements the stock
`clk-rp1` provider and does not recreate the private provider lease used by the
historical custom-kernel implementation.

The Debian package contains the versioned module source, Kbuild and DKMS
configuration, canonical UAPI, and inactive GPIO4 and GPIO20 overlays. Package
installation does not select a route, edit boot configuration, apply an
overlay, load the module, enable output, or authorize use.

Release checksums and compatibility metadata are functional machine inputs.
They identify artifacts and detect substitution; they are not signatures,
authorization, or qualification by themselves.

## Repository boundaries

### This repository owns

- loadable kernel-module source and kernel-facing lifecycle behavior;
- Kbuild and DKMS configuration;
- route-specific device-tree overlays;
- the bounded, versioned userspace API;
- compatibility identities and release metadata;
- package installation, update, rollback, removal, signing, and diagnostics
  behavior; and
- module-specific tests, releases, and security reporting.

### WSPR-Transmitter owns

- its userspace provider adapter;
- conversion of application plans into the UAPI;
- application-side state and terminal-reason handling; and
- adapter tests using fakes or mocks rather than embedded kernel source.

### WsprryPi owns

- physical-backend selection and fail-closed product policy;
- persisted GPIO4 or GPIO20 selection;
- scheduling and application integration;
- installation orchestration for explicitly compatible tagged releases;
- operator enrollment, warnings, diagnostics, and recovery workflow; and
- product qualification and release decisions.

The repositories coordinate only through tagged artifacts, the canonical UAPI,
compatibility metadata, and explicit cross-repository validation. This complete
module source tree is not vendored into WsprryPi.

## Licensing

- Original module and kernel-facing source uses
  `GPL-2.0-only OR MIT`.
- The module declares `MODULE_LICENSE("Dual MIT/GPL")`.
- Original userspace-visible UAPI headers use
  `(GPL-2.0-only WITH Linux-syscall-note) OR MIT`.
- Independent original tools, tests, documentation, schemas, and metadata use
  `MIT`.
- Original device-tree sources use `GPL-2.0-only OR MIT` unless their actual
  derivation requires a narrower license.
- Imported or adapted material retains its upstream license, copyright, and
  provenance.

The SPDX identifier in each file is authoritative. Kernel loader metadata does
not replace source licensing or resolve derivation questions.

## Kernel and resource model

The module targets stock Raspberry Pi kernels. It must not introduce a custom
kernel dependency or fall back to `/dev/mem`, raw userspace MMIO, unexported
kernel internals, arbitrary physical addresses, or another transmitter backend.

The stock `clk-rp1` provider remains authoritative for ordinary clock
operations. Resources are derived from device tree and exported kernel APIs.
Provider identity, resource layout, DMA translation, pinctrl state, clock
state, and route must all match an explicit compatibility entry before live use
can become eligible.

The module supplies GPCLK0 and the RP1 200 MHz `pll_sys` output as distinct
named clock resources. An output operation explicitly selects the
independently identified provider clock with the common clock framework,
verifies parent and nominal-rate readback, and restores the preceding parent
and rate during bounded cleanup. It does not authorize automatic substitution
of another GPCLK0 source. Consumers must plan divider words from the contracted
200 MHz nominal parent; a consumer that still assumes 50 MHz is incompatible.
Divider plans use the provider's 16-bit integer and 16-bit fractional GPCLK0
field: integer values 1 through 65,535 are valid, while the complete Q16 word
remains bounded by `0xffffffff`.

All frequencies and execution modes share this parent-selection path. Rate
selection can reparent GPCLK0, so checking the parent only before setting a
rate is insufficient. While output is inactive, setup makes at most four
attempts using the observed parent and verifies the planned integer
divider against the provider's whole-Hz readback and Q16 divider bounds.
Every unsuccessful attempt moves the next seed request inward by one more Hz,
including after a parent switch. Keeping that bias across parent switches
prevents repeating an identical nearest-rate parent-selection cycle.
The operation's fractional DMA sequence remains unchanged. Setup selects the
contracted parent after the final rate request and verifies the parent,
200 MHz nominal rate, and integer divider before activation. Preparation
rechecks the parent and nominal rate. No band-specific 50 MHz exception exists.

Cleanup disables output and restores safe pinctrl before restoring the saved
parent and nominal output rate. Restoration also selects the saved parent
after rate requests and checks both identities; it is bounded to four attempts.
When a requested rate equals the common-clock cached rate, an inactive
intermediate rate forces a provider update before the final request, preventing
fractional DMA's last value from surviving a cached no-op.
Each attempt therefore makes at most two provider rate requests.
Unverifiable restoration faults the endpoint, including when startup cleanup
is followed by a second cleanup call. This changes neither the shared PLL's
frequency nor other consumers' clocks. A different future parent contract must
update the module identity and userspace divider planning together.

Only GPIO4 and GPIO20 are supported. They are separate administrative routes
with distinct overlays and qualification. The module accepts no arbitrary GPIO
parameter, combined overlay, or automatic route substitution.

## Endpoint discovery and platform-device ownership

Each route overlay owns one route-specific enabled endpoint node beneath the existing `rp1`
bus. The node carries the canonical compatible, route, pin, clock, DMA,
register, and pinctrl identities. Keeping that ancestry is mandatory: resource
translation continues through the stock RP1 device-tree ranges and providers.
GPIO4 and GPIO20 use distinct node names. Consequently, applying both overlays
produces two matching nodes and module initialization rejects the ambiguous
topology before publishing an endpoint. With neither overlay there are zero
matching nodes and no endpoint; with exactly one overlay there is exactly one
candidate node. Overlay order can never silently select a last-applied route.

The module owns bounded discovery of that endpoint. Initialization requires
exactly one matching node and rejects zero, duplicate, disabled, malformed,
ambiguous, conflicting, or inconsistently populated nodes. A platform device
already created by the kernel is preferred and must be bound to this driver.
Probe validation requires the endpoint, clock provider, and DMA provider to be
children of the same RP1 node; supplier phandles alone do not establish valid
ancestry.
The module never replaces, unregisters, or otherwise assumes ownership of a
kernel-created platform device.

Some stock Raspberry Pi boot paths do not instantiate a newly overlaid child
of the RP1 node. When the single valid endpoint has no platform device, the
module may create only that exact device with exported OF platform APIs. The
module walks upward from the endpoint and uses the nearest instantiated
platform ancestor as the Linux device parent. On stock Raspberry Pi 5 kernels
the intermediate `rp1` firmware node need not have its own platform device, so
the nearest instantiated ancestor can be the PCIe platform device while the
endpoint's firmware ancestry still passes through `rp1`. Absence of any
instantiated platform ancestor rejects creation. The module records this
ownership and may unregister only the device it created and still owns.
Synchronous creation must also produce a successful bind;
deferred or failed binding rejects module initialization and removes the
module-created device. Owned-device teardown holds the endpoint OF-node
reference across unregister and clears only that node's populated flag after
unregister completes, permitting a later bounded fallback creation without
exposing a duplicate-device window.

The module must not populate or depopulate the RP1 bus generally, create
unrelated children, move the endpoint to an unrelated bus, manufacture
resources, hard-code translated CPU physical addresses, or bypass normal
device-tree address, clock, DMA, or pinctrl translation. Boot-time firmware
overlays and dynamic overlay notification are distinct validation cases and
neither result transfers qualification to the other.

## UAPI

The canonical header is `include/uapi/linux/rp1_gpclk.h`. The UAPI is bounded,
additive, versioned, and route-neutral. It does not expose physical addresses,
DMA channels, unrestricted programs, or arbitrary register access.

Requests use fixed-size structures, checked arithmetic, bounded counts and
durations, zero reserved fields, and explicit capability checks. Userspace
pointers are copied once into bounded kernel-owned storage. Unknown commands,
flags, values, routes, capabilities, or structure variants fail closed.

One open file may own one opaque lease. WSPR, keyed events, and finite TONE
work are bounded; continuous TONE is an explicit ABI v2 operation with no
hidden duration and remains owned by its lease until cancellation. Every
submission has a strictly increasing generation. Cancellation prevents a
successor and uses a bounded drain. Stale callbacks are rejected. Terminal
outcomes are stable and specific. A cleanup fault remains latched and cannot be
cleared by releasing a lease.

### Version 1.0.1 normative UAPI and endpoint freeze

The canonical endpoint is `/dev/rp1-gpclk`. ABI v1 is byte-identified by the
SHA-256 recorded in `release/uapi-contract-freeze-v1.0.1.json`; that manifest
also freezes ioctl identities and sizes, GPIO4/GPIO20 route identities, lease,
submission, terminal-state, cleanup, packaging, and version relationships.
Submission remains unavailable unless both the immutable load-time output gate
and an exact positive compatibility entry for the selected route permit it.

Changing the endpoint or canonical UAPI reopens the freeze and invalidates
dependent consumer work. Final documentation freeze remains pending until
target evidence and release claims are complete.

## Lifetime and cleanup

Open-file, platform-device, DMA callback, unbind, overlay, and module lifetimes
are explicit. Managed allocation does not replace reference counting or a
dead-state transition.

Module initialization registers platform-device removal observation before
the platform driver, discovers or creates the endpoint, and publishes success
only after the device is bound. Failure unwinds in strict reverse order.
Module exit detaches its ownership record, unregisters any still-owned created
device so `remove()` can quiesce it, unregisters the driver, and finally
unregisters removal observation. External removal of a created device clears
the ownership record before its storage can be released. Creation holds a
temporary device reference and observes removal across the interval between
device registration and ownership publication. These rules prevent duplicate
creation, stale ownership, double removal, and destruction of a kernel-created
device.

Removal or unbind first prevents new work, rejects stale callbacks, drains or
cancels bounded work, restores only state owned by this module, and proves
resource quiescence before freeing state. The module never restores another
consumer's state from a stale snapshot and never releases a resource it did not
acquire.

Process death, interruption, timeout, unbind, and cleanup failure must converge
to a safe terminal state or an explicit fault that prevents further use.
STOP and close cancellation do not synthesize DMA completion or force-abort an
active RP1 paced descriptor. They reject every successor and allow only the
current kernel-bounded descriptor to drain before cleanup.

On the validated Pi 5 firmware baseline, TICK_DMA0 may be enabled and running
at 50 reference cycles while the downstream DMA_TICK0 handshake is disabled.
After exclusive acquisition of both MMIO resources, development execution may
temporarily stop and later restore only that exact `CTRL=3`, `CYCLES=50`,
`DMA_TICK_EN=0`, `DMA_TICK_CTRL=0` baseline. All other nonzero combinations
remain ownership conflicts. This exception does not permit takeover of an
active DMA handshake or a different tick configuration.

## Compatibility

Compatibility is deny-by-default. A live-eligible entry binds the module
release and UAPI to the relevant kernel, architecture, hardware, firmware,
device tree, clock provider, resource layout, DMA translation, route overlay,
and signing policy.

Unknown, missing, ambiguous, or mismatched identity disables live eligibility.
A successful module build establishes build compatibility only. It does not
qualify loading, binding, GPIO output, timing, cleanup, coexistence,
transmission, RF behavior, or a different system.

The dual-route functional-development branch contains independent GPIO4 and
GPIO20 development-candidate entries for the Raspberry Pi 5 Model B / BCM2712
/ aarch64 / 6.18.34+rpt-rpi-2712 target class. The unique active device-tree
route selects which entry can pass; the other route is absent. Zero active
route overlays provides no endpoint. Both overlays present is ambiguous and
must fail closed; overlay order never selects a route. There is no fallback,
substitution, or evidence transfer between GPIO4 and GPIO20. These entries
permit bounded development testing only and are reported as `Experimental`;
they are not completed qualification or normal product live eligibility.
Hostname is retained in target evidence and is not a kernel compatibility
input.

## Packaging and administration

The Debian package owns only its declared module source and inactive overlay
files. Standard `dpkg`, `dh-dkms`, and DKMS mechanisms own package lifecycle.
Installation refuses to overwrite foreign files. Removal deletes only files
whose identity and ownership remain attributable to the package.

Beginning with 1.1.1, the package also owns a versioned application-facing
route executor, its JSON schema, and consumer documentation. The executor owns
only the delimited RP1-GPCLK-DKMS route block and attributable journals below
`/var/lib/rp1-gpclk-dkms/route-transactions`. It keeps saved/configured and
post-boot active routes separate, rejects ambiguous ownership, and exposes no
qualification-plan interface. Package installation remains route-neutral and
does not create runtime state.

Signing keys and trust enrollment are administrator-owned. No private key is
distributed or created as a silent installation side effect. Signing proves
provenance and possible load eligibility; it does not qualify behavior.

Diagnostics are bounded and read-only. They do not install, load, bind, repair,
select a route, change boot state, operate GPIO, or enable output.

Exact-source maintainer development is a separate, package-independent
administrative path. Its manifest binds the exact Git commit, explicitly
recorded source state, bounded rendering transformation, DKMS/module/kernel,
UAPI, overlays, route, installed artifact, tools, and removal evidence. Its
state is visibly `source-development` and at most `Experimental`; it cannot
create release metadata, satisfy release compatibility, or establish product
or RF qualification. The canonical module name remains `rp1_gpclk_dkms`.

The exact-source route-manager lifecycle is likewise package-independent. It
must preserve Debian-owned executables and unit fragments, use a reversible
administrator drop-in, bind userspace and module source identities separately,
and expose only passive query while active. Successful deployment or query is
not execution authorization or qualification.

Where source-development consumers require current boot ownership, deployment
alone is insufficient. A separate attributable adoption record must bind the
current boot and configuration digest to exact route, userspace, module,
kernel, UAPI, and compatibility identities. Historical package ownership and
completed historical journals do not establish that current proof.

While that exact-source binding is active, passive query also returns a nested
`state.safety` snapshot containing authenticated endpoint ownership, endpoint
open state, the observed immutable `live_output` gate, and bounded service
states. The snapshot remains observational and cannot acquire the endpoint,
change the module gate, or authorize an operation.

## Validation

The opt-in [clock-disabled runtime controller](runtime-controller-v1.md) is a
separate development implementation using exported stock-kernel overlay APIs.
It owns overlay IDs and error results, interlocks the consumer's module lifetime,
rejects output-enabled loads, and supplies concrete inhibited administration and
same-boot crash recovery. It adds a separate administrative UAPI, not transmission
commands. It is excluded from default packaging and has no target qualification.
Deployment and hardware tests remain separately authorized gates. It does not
enable mutation through the packaged or source-development v1 manager.

The [Experimental runtime-route v2 engine](runtime-route-v2.md) is explicitly an
offline reference model with a blocked public mutation entry point. The
[target source review](runtime-route-target-review.md) rejects its synthetic
atomic effects as a Linux adapter contract and identifies the stock configfs
removal path's discarded error result as a concrete recovery blocker. A bounded
read-only collector exists; that foundation supplied no write adapter or deployment
path. The later opt-in controller above does not reuse the synthetic adapter or
enable source-development v1 mutation.
Snapshot observations and model tests do not establish exclusion, post-removal
success, kernel lifetime safety, or hardware readiness.

The additive ABI-v3 passive snapshot contract is specified in
`docs/contracts/uapi-v3-passive-snapshot.md`. ABI v4 adds the operation-scoped
live authorization described in `docs/contracts/uapi-v4-operation-live.md`.
The passive snapshot exposes presence and tri-state
observations without granting ownership or disclosing lease tokens. Terminal
generation, reason, and completed-unit state remain observable after lease
release until the next successful acquire.

Ordinary checks are offline, unprivileged, network-free, hardware-free, and
safe to repeat. Implementation changes receive deterministic tests. Kernel
build results record the kernel, configuration, compiler, architecture, module
version, UAPI version, and outcome.

Binding validation records the firmware-applied device-tree node, platform
device, driver link, probe result, and canonical character device as separate
facts. A loaded module or matching OF modalias alone is not binding evidence.

Target tests require inspection of the exact test implementation and explicit
authorization for their system effects. Output-disabled administration, live
GPIO behavior, timing, transmission, and RF are separate evidence classes and
must not be inferred from one another.

For the 1.1.2 dual-route development identity, live compatibility also requires
the route-specific endpoint node name emitted by the corresponding current
overlay: `rp1-gpclk-dkms-gpio4` for route 1 or
`rp1-gpclk-dkms-gpio20` for route 2. The predecessor shared
`rp1-gpclk-dkms` endpoint name is rejected even when its remaining properties
are otherwise valid. This prevents predecessor overlay bytes from satisfying
the changed development candidate identity.

The ABI-v4 operation-scoped build reports candidate IDs ending in
`development-candidate-r4`. The r4 build does not inherit either route's r3
target evidence. Its exact Pi 5, kernel, architecture, module-version, resource,
and route allowlist admits each candidate only to an explicitly authorized
development attempt; eligibility is not qualification. Each exact
route-specific artifact must still be separately requalified before a route can
carry an r4 qualification claim. Earlier candidate IDs remain historical
identities and cannot satisfy the current client contract. Immutable module and
overlay hashes remain mandatory evidence; the revision suffix is not a
substitute for artifact hashing.

GPIO4 r2 and GPIO20 r2 each have completed, independently bound target-functional
development evidence for module execution and cleanup. Hardware-free validation
and successful build, binding, or functional output are separate evidence
classes. None establishes waveform or spectral integrity, timing or frequency
accuracy, receiver capture or decode, WsprryPi product-path behavior, product
eligibility, transmitter-system qualification, SDR qualification, RF
qualification, packaging evidence, or release qualification.

## Releases

A release is tagged, checksummed, reproducible from source, and accompanied by
compatibility, provenance, licensing, and security metadata. The source
version, tag, Debian version, DKMS version, module version, UAPI, package, and
release metadata must agree according to the release policy.

Version 1.1.2 remains an unreleased functional-development identity. Its
current UAPI, source, overlays, compatibility entries, package naming,
inventories, and hashes are development inputs, not frozen final consumer or
release identities. Packaging and immutable artifact freezing require a later
roadmap gate and separate review.

WsprryPi consumes only an explicitly compatible tagged release. Module and
application commits, reviews, releases, and qualification claims remain
separate. A clean test run or published artifact never broadens the stated
qualification scope.


### Version 1.1.0 ABI v2 TONE freeze

Release 1.1.0 supersedes ABI v1 for new consumers while preserving all v1
ioctls unchanged. ABI v2 adds explicit continuous and kernel-bounded finite
TONE operations and v2 negotiation as specified in `docs/contracts/uapi-v2.md`.
The canonical endpoint and route identities are unchanged. The 1.0.1 freeze is
historical; its GPIO4 positive evidence does not transfer to changed module or
UAPI bytes. Both routes therefore fail closed until new exact-build evidence is
issued, and GPIO20 remains unavailable.
