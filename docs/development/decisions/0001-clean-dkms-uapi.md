<!-- SPDX-License-Identifier: MIT -->

# Decision 0001: Start a clean DKMS UAPI

- Status: Accepted
- Date: 2026-08-14
- Decision owner: Project owner

## Context

The historical custom-kernel provider used ioctl magic `0xb7`, version-1 WSPR
structures, and additive version-2 finite-event structures. That ABI supported
successful engineering and qualification work, but it was not released as a
stock-kernel DKMS interface.

The historical contract lacks unified capability negotiation, route identity,
module and compatibility identity, and a clean extensibility model. Preserving
it would permanently carry development-era divisions and GPIO4 assumptions
into a new independently released kernel project.

## Decision

`RP1-GPCLK-DKMS` will define a new canonical UAPI rather than preserve the
historical ioctl numbers or structure layouts as ABI.

The new UAPI will:

- use one coherent version and capability-negotiation model;
- report module, UAPI, hardware/provider, route, and compatibility identities;
- use bounded, explicitly sized, additive structures;
- support allowlisted routes without arbitrary GPIO selection;
- preserve the proven semantic concepts of exclusive ownership,
  lease-scoped generations, finite work, draining, stable terminal states, and
  explicit failure reasons;
- keep WSPR and finite-event requests bounded without exposing addresses,
  register access, DMA selection, or unrestricted programs; and
- be canonical in this repository, with automated identity checks for every
  userspace compatibility copy.

The historical ioctl magic `0xb7`, operations `0x00` through `0x06`, version-1
and version-2 layouts, and `/dev/rp1-gpclk0` name are evidence, not reserved
choices for the new ABI. Names and numeric assignments will be selected during
the reviewed Phase 2 UAPI design.

## Consequences

- WSPR-Transmitter requires a coordinated adapter migration.
- The custom-kernel provider is not a drop-in implementation of this module.
- Historical tests can supply semantic cases but not byte-layout compatibility
  claims.
- No legacy ioctl dispatcher is planned. Adding one would require a new
  reviewed decision and complete security/lifecycle justification.
- GPIO20 and compatibility reporting can be designed before the first public
  ABI freezes them.

## Non-decisions

This decision does not yet assign:

- ioctl magic or command numbers;
- public structure layouts or numeric enum values;
- module, device-node, overlay, or package names;
- compatibility-manifest encoding; or
- supported kernel versions.

Those choices remain gated by the Phase 2 UAPI and packaging design.
