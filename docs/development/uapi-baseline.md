<!-- SPDX-License-Identifier: MIT -->

# UAPI conceptual baseline

## Status

This records historical semantics for continuity. The project started a clean
DKMS UAPI under [Decision 0001](decisions/0001-clean-dkms-uapi.md). Phase 3
freezes the first public interface under
[Decision 0006](decisions/0006-phase3-interface-freeze.md); the historical
inventory below is not the byte authority.

The compared source is
[`rp1_gpclk_uapi.h` at `fe8a03b`](https://github.com/WsprryPi/WSPR-Transmitter/blob/fe8a03b17a817175553968f91508fccd48c78bdf/src/rp1_gpclk_uapi.h).
The historical kernel shim merely included this header by a repository-relative
path.

## Historical inventory

Version 1 provided ioctl magic `0xb7`, acquire/submit/stop/state/release,
exactly four tones and 162 WSPR symbols, 66,792 writes per symbol, tick divider
511, nominal 110.592-second frames with 6.75 ms tolerance, drive selection, and
lease-scoped generations.

Additive version 2 added submit-events and event-state, up to four tones and 512
events, nanosecond durations, total duration, an RF-on flag, current-event
observation, and terminal reasons.

States were `IDLE`, `RUNNING`, `DRAINING`, `COMPLETE`, and `FAILED`.
Reasons were `NONE`, `COMPLETE`, `STOPPED`, `DEADLINE_MISSED`,
`ADAPTER_FAILED`, `OWNER_CLOSED`, and `PROVIDER_REMOVED`.

## Concepts to preserve

- explicit version and bounded structure validation;
- bounded requests with no raw address, DMA, register, or arbitrary program;
- one owner and lease-scoped, same-lease stale generation rejection;
- STOP, RELEASE, observable draining, and stable terminal state/reason;
- bounded tone/event counts and checked duration arithmetic;
- zeroed reserved fields and additive extensions;
- drive allowlist with 2 mA default policy input; and
- route/capability reporting without arbitrary GPIO selection.

## Required stock-module additions

The first published ABI must report, in bounded form:

- bound allowlisted route;
- supported UAPI range and operations;
- module release/build identity;
- recognized provider/hardware/layout identity;
- live eligibility separately from build compatibility;
- compatibility state and rejection reason; and
- a latched cleanup fault where applicable.

Route selection is administrative. Userspace may verify an allowlisted route but
must not remux an arbitrary GPIO through the UAPI.

## Migration risks

- Historical v1 and v2 are separate version constants rather than one negotiated
  capability model.
- Acquire has no route or compatibility identity.
- Exact-size validation blocks trailing-field growth without new structures.
- WSPR-specific timing constants coexist with general event facilities.
- `ADAPTER_FAILED` may be too implementation-specific for a durable ABI.
- The header lacks SPDX and has different Linux/non-Linux include behavior.
- The historical values are not a compatibility obligation. WSPR-Transmitter
  will migrate to the new canonical UAPI.

## Settled ABI direction

- Do not preserve ioctl magic `0xb7`, commands `0x00` through `0x06`, or the
  historical structure layouts merely for compatibility.
- Do not provide a legacy dispatcher in the initial module.
- Preserve proven behavior as semantic requirements and tests, not byte-layout
  compatibility.
- Design route and capability negotiation before freezing the first public
  ABI.

## Decisions frozen by Phase 3

| Decision | Frozen contract |
| --- | --- | --- |
| Capability query shape | Exact-size `RP1_GPCLK_IOC_QUERY` v1 structure. |
| Device-node and module names | `/dev/rp1-gpclk` and `rp1_gpclk_dkms`. |
| Route values | GPIO4 = 1 and GPIO20 = 2. |
| Structure extensibility | Exact V1 sizes; additive commands or explicit new versions only. |

The canonical header, `uapi-identity.json`, UAPI contract, and Decision 0006
jointly define the frozen identity.
