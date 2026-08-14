<!-- SPDX-License-Identifier: MIT -->

# RP1 GPCLK DKMS

`RP1-GPCLK-DKMS` is the planned stock-kernel, out-of-tree Linux module for
bounded control of Raspberry Pi RP1 GPCLK0 resources on behalf of WsprryPi.
It is intended to be distributed as source and compiled locally for the
operator's installed kernel through DKMS.

The project exists so WsprryPi can support Raspberry Pi 5-family RP1 hardware
without distributing or maintaining a custom kernel. The stock Raspberry Pi
`clk-rp1` driver remains installed and authoritative for ordinary CPU-side
clock operations.

## Current status

Repository foundation and engineering contracts only. No kernel module,
device-tree overlay, DKMS package, installer, or qualified GPIO output is
implemented here yet.

Nothing in this repository currently authorizes module installation, target
binding, system configuration, GPIO operation, transmission, or RF activity.

## Intended scope

This project will own:

- the loadable RP1 GPCLK kernel-module source;
- Kbuild and DKMS packaging;
- route-specific device-tree overlay sources;
- the canonical bounded and versioned UAPI;
- compatibility and provenance metadata;
- module signing, installation, update, rollback, removal, and diagnostics;
- kernel-header, lifecycle, static-contract, and target safety tests; and
- tagged source releases with checksums.

The initial feasibility route is GPIO4. GPIO20 will be introduced as a separate
allowlisted route after GPIO4 proves the stock-kernel path and before route,
UAPI, packaging, or operator contracts are frozen. Neither route inherits the
other's qualification.

## Project boundary

- [`WsprryPi/RP1-GPCLK-DKMS`](https://github.com/WsprryPi/RP1-GPCLK-DKMS)
  owns kernel-facing implementation and releases.
- [`WsprryPi/WSPR-Transmitter`](https://github.com/WsprryPi/WSPR-Transmitter)
  owns its userspace adapter and translation into the UAPI.
- [`WsprryPi/WsprryPi`](https://github.com/WsprryPi/WsprryPi) owns backend
  policy, configuration, scheduling, installer orchestration, operator
  workflow, and product qualification.

The projects coordinate through tagged artifacts, a canonical UAPI, explicit
compatibility manifests, and cross-repository checks. WsprryPi must not build
from this project's moving default branch.

See the [module engineering contract](docs/contracts/rp1-gpclk-dkms-module-contract.md)
and the upstream [WsprryPi product contract](https://github.com/WsprryPi/WsprryPi/blob/eb1c933ec20147aae987f06a2b8e4f1d988c00f6/docs/research/rp1-gpclk-stock-kernel-dkms-contract.md).

Phase 2 preparation is documented in the
[historical evidence index](docs/evidence/historical-evidence-index.md),
[source provenance policy](docs/development/provenance.md),
[UAPI conceptual baseline](docs/development/uapi-baseline.md),
[compatibility identities](docs/development/compatibility-identities.md), and
[historical artifact inventory](docs/development/historical-artifact-inventory.md).
The first accepted architecture decision is to
[start a clean DKMS UAPI](docs/development/decisions/0001-clean-dkms-uapi.md).

## Safety model

The design is fail-closed. Unknown or unsupported kernel, hardware, device-tree,
resource, signing, route, capability, or cleanup states must leave RP1 output
unavailable. It will not fall back to `/dev/mem`, raw userspace MMIO, a custom
kernel, or another physical transmitter backend.

The stock-kernel module cannot reproduce the stronger provider-private lease
used by the historical custom-kernel proof of concept. Cooperative kernel
resource ownership and explicit operator exclusions reduce risk but cannot
prove the absence of direct-MMIO or uncoordinated interference.

## Licensing

Original project work is MIT licensed wherever that is practical. Kernel-facing
module source is dual-licensed under `GPL-2.0-only OR MIT`, and the module will
declare `MODULE_LICENSE("Dual MIT/GPL")`. Userspace-visible UAPI headers are
intended to use `(GPL-2.0-only WITH Linux-syscall-note) OR MIT`.

See [LICENSE.md](LICENSE.md) for the authoritative per-file policy. Third-party
or adapted material retains its original license and attribution.

## Development

Read [AGENTS.md](AGENTS.md) and the module contract before working in this
project. Ordinary development and validation must remain offline,
unprivileged, hardware-free, and safe to repeat unless an exact target action
is separately authorized.

Compilation demonstrates build compatibility only. It does not qualify module
loading, GPIO timing, coexistence, cleanup, transmission, RF behavior, or an
operator installation path.
