<!-- SPDX-License-Identifier: MIT -->

# Module lifecycle

The Debian package, DKMS, module runtime, device-tree overlays, and signing
identity have separate ownership and lifecycle. Treat them separately and fail
closed when current state is incomplete or ambiguous.

## Installation behavior

Package installation registers the module source with DKMS and installs both
allowlisted overlays as inactive files. It does not:

- select GPIO4 or GPIO20;
- edit boot configuration;
- apply a device-tree overlay;
- load or bind the module;
- create a signing identity;
- enable GPCLK or change GPIO state; or
- authorize transmission.

Route selection is an administrative configuration decision. Exactly one of
the GPIO4 or GPIO20 overlays may be selected. There is no arbitrary GPIO
parameter, combined overlay, hot route change, or automatic substitution.

## Compatibility and signing

Before loading the module, verify the exact running kernel, hardware, firmware,
device tree, clock provider, resource layout, selected route, module version,
UAPI version, and signing policy against an explicit compatibility entry.

The device endpoint remains root-owned and mode `0600`. Signing keys and trust
enrollment are administrator-owned and are not package content. See
[Module signing and key enrollment](signing.md).

## Loading and operation

The sole canonical ABI v1 endpoint is `/dev/rp1-gpclk`. A historical
`/dev/rp1-gpclk0` node is not a supported discovery fallback. A missing
endpoint does not authorize userspace to create or substitute one.

Loading with live output disabled is distinct from live eligibility. A module
that builds or loads successfully may still reject all submissions. Live use
requires the immutable load-time output gate, exact compatibility approval,
the selected allowlisted route, and application-level authorization.

One open file may hold one lease. Work is finite and generation-specific.
`STOP`, owner close, process death, unbind, and unload use the bounded cleanup
path. A cleanup fault is a stop condition and prevents further use until it is
investigated.

## Update and rollback

Retain the installed predecessor until a successor has passed all applicable
build, signing, installation, output-disabled runtime, and cleanup checks.
Version ordering alone does not establish compatibility.

On failure, remove only state attributable to the failed successor. Do not
weaken compatibility or signing policy, overwrite foreign files, or force an
unknown runtime state to make an update succeed.

## Removal

Unload before DKMS uninstall. Remove only module, overlay, and package state
owned by this package. An applied overlay, open endpoint, active owner, pending
work, cleanup fault, modified file, unknown clock state, or unproven resource
state blocks automatic removal.

After removal, verify that the module is unloaded, the device endpoint and
platform binding are absent, the package version is absent from DKMS, owned
overlay files are absent where safe to remove, and GPIO/clock state matches the
recorded inactive baseline. Administrator signing keys, certificates, trust
entries, shared configuration, and unrelated files are retained.

## Diagnostics

Use `rp1-gpclk-diagnostics` for bounded read-only inspection. It does not load,
bind, repair, select a route, edit boot configuration, or operate hardware. See
[Read-only diagnostics](diagnostics.md).

There is no custom-kernel, `/dev/mem`, raw userspace MMIO, arbitrary-route, or
alternate-transmitter fallback. Unknown hardware, kernel, device-tree,
resource, signing, route, UAPI, artifact, or cleanup state remains unavailable.
