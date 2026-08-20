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

Only GPIO4 and GPIO20 are supported. They are separate administrative routes
with distinct overlays and qualification. The module accepts no arbitrary GPIO
parameter, combined overlay, or automatic route substitution.

## UAPI

The canonical header is `include/uapi/linux/rp1_gpclk.h`. The UAPI is bounded,
additive, versioned, and route-neutral. It does not expose physical addresses,
DMA channels, unrestricted programs, or arbitrary register access.

Requests use fixed-size structures, checked arithmetic, bounded counts and
durations, zero reserved fields, and explicit capability checks. Userspace
pointers are copied once into bounded kernel-owned storage. Unknown commands,
flags, values, routes, capabilities, or structure variants fail closed.

One open file may own one opaque lease. Work is finite and identified by a
strictly increasing generation. Cancellation prevents a successor and uses a
bounded drain. Stale callbacks are rejected. Terminal outcomes are stable and
specific. A cleanup fault remains latched and cannot be cleared by releasing a
lease.

## Lifetime and cleanup

Open-file, platform-device, DMA callback, unbind, overlay, and module lifetimes
are explicit. Managed allocation does not replace reference counting or a
dead-state transition.

Removal or unbind first prevents new work, rejects stale callbacks, drains or
cancels bounded work, restores only state owned by this module, and proves
resource quiescence before freeing state. The module never restores another
consumer's state from a stale snapshot and never releases a resource it did not
acquire.

Process death, interruption, timeout, unbind, and cleanup failure must converge
to a safe terminal state or an explicit fault that prevents further use.

## Compatibility

Compatibility is deny-by-default. A live-eligible entry binds the module
release and UAPI to the relevant kernel, architecture, hardware, firmware,
device tree, clock provider, resource layout, DMA translation, route overlay,
and signing policy.

Unknown, missing, ambiguous, or mismatched identity disables live eligibility.
A successful module build establishes build compatibility only. It does not
qualify loading, binding, GPIO output, timing, cleanup, coexistence,
transmission, RF behavior, or a different system.

## Packaging and administration

The Debian package owns only its declared module source and inactive overlay
files. Standard `dpkg`, `dh-dkms`, and DKMS mechanisms own package lifecycle.
Installation refuses to overwrite foreign files. Removal deletes only files
whose identity and ownership remain attributable to the package.

Signing keys and trust enrollment are administrator-owned. No private key is
distributed or created as a silent installation side effect. Signing proves
provenance and possible load eligibility; it does not qualify behavior.

Diagnostics are bounded and read-only. They do not install, load, bind, repair,
select a route, change boot state, operate GPIO, or enable output.

## Validation

Ordinary checks are offline, unprivileged, network-free, hardware-free, and
safe to repeat. Implementation changes receive deterministic tests. Kernel
build results record the kernel, configuration, compiler, architecture, module
version, UAPI version, and outcome.

Target tests require inspection of the exact test implementation and explicit
authorization for their system effects. Output-disabled administration, live
GPIO behavior, timing, transmission, and RF are separate evidence classes and
must not be inferred from one another.

## Releases

A release is tagged, checksummed, reproducible from source, and accompanied by
compatibility, provenance, licensing, and security metadata. The source
version, tag, Debian version, DKMS version, module version, UAPI, package, and
release metadata must agree according to the release policy.

WsprryPi consumes only an explicitly compatible tagged release. Module and
application commits, reviews, releases, and qualification claims remain
separate. A clean test run or published artifact never broadens the stated
qualification scope.
