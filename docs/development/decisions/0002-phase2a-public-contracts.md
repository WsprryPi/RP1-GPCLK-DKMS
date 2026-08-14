<!-- SPDX-License-Identifier: MIT -->

# Decision 0002: Freeze Phase 2A public contracts

- Status: Accepted
- Date: 2026-08-14
- ABI identity: `RP1_GPCLK_UAPI_ABI_V1`

## Decisions

### Names and namespace

- Module/Kbuild name: `rp1_gpclk_dkms`.
- Public header: `include/uapi/linux/rp1_gpclk.h`.
- Future device basename: `rp1-gpclk`; Phase 2A creates no device.
- Ioctl type: `0xb8`, deliberately distinct from historical `0xb7`.
- V1 command numbers are `0x20` through `0x26`; lower numbers are left unused,
  not promised for legacy compatibility.

The namespace is project-owned and must be checked for collisions before a
public release. It is not a claim of assignment by the Linux ioctl registry.

### Versioning and extension

ABI version 1 is the first publishable layout. Every request begins with
16-bit `size`, 16-bit `version`, and 32-bit `flags`. V1 accepts its exact
structure size and zero flags/reserved fields. Because ioctl encodings include
structure size, extending a structure requires a new command number and name;
released layouts are immutable. Capability bits advertise optional behavior.

All public fields use Linux fixed-width UAPI types, with explicitly aligned
64-bit fields so 32-bit and 64-bit layouts agree. Pointers are represented as
aligned 64-bit user addresses only in the two bounded submission structures.
The pointed-to arrays have fixed element layouts and explicit maximum counts.

### Operations and ownership

Commands are query, acquire, submit WSPR, submit events, stop, get state, and
release. Query is available before acquisition. Acquire returns an opaque
nonzero lease ID. Each accepted submission returns a nonzero generation scoped
to that lease. Stop, state, and release carry both IDs where applicable;
stale IDs are rejected.

### Routes, modes, states, and reasons

Route zero is invalid; GPIO4 is 1 and GPIO20 is 2. These are administrative
identities only and do not select or remux a pin.

Modes are WSPR, QRSS, FSKCW, and DFCW. States are idle, running, draining,
complete, failed, and dead. Terminal reasons distinguish normal completion,
explicit stop, owner close, provider removal, deadline, validation, resource,
startup conflict, DMA, clock, pinctrl, readback, cleanup, compatibility, and
internal failures. Compatibility-query reasons separately cover missing
manifests, unknown or mismatched identities, unsupported builds, signatures,
resources, conflicts, self-tests, cleanup latches, and administrator
enrollment. Numeric values are frozen in the header and contract test.

### Capabilities and limits

Capabilities separately report WSPR submission, general events, stop/drain,
stable state, route identity, compatibility identity, cleanup-fault latching,
and live eligibility. The V1 limits are 4 tones, 162 WSPR symbols, 512 general
events, a 66,792-entry maximum dithering period, 16 fractional bits, fixed tick
divider 511, 1 ns minimum event duration, 120 s maximum event duration, and
120 s maximum request duration. Each tone is a lower/upper Q16 divider pair
with bounded dithering counts. These are acceptance ceilings, not evidence
that hardware execution exists.

### Compatibility manifest

The canonical schema is strict JSON Schema draft 2020-12. A manifest names an
exact module artifact/UAPI and contains deny-by-default entries with separate
build, runtime, route, modes, evidence, compatibility state, live eligibility,
and reason. `Qualified` requires nonempty evidence and live eligibility;
`Compatible-unqualified`, `Unavailable`, and `Rejected` prohibit it. GPIO4 and
GPIO20 require distinct entries.

## Consequences

The initial WSPR-Transmitter adapter must target this ABI explicitly; there is
no legacy dispatcher. Any compatibility copy must be byte-identical to the
canonical header. A successful header or Kbuild compile establishes no more
than build compatibility and never changes a manifest state by itself.

Phase 2A implements declarations and unavailable seams only. It does not
register a platform driver or misc device and cannot acquire a clock, DMA,
pinctrl, device-tree resource, GPIO, or route.

## Intentionally unfrozen

- Supported kernel/header identities and compatibility entries.
- Overlay names, parameters, and bindings.
- Device major/minor and udev policy.
- DKMS package/release version and installation paths.
- GPIO20 pinmux/DT implementation and all route qualification.
- Functional ioctl error details beyond the stable public reasons.
