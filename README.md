<!-- SPDX-License-Identifier: MIT -->

# RP1 GPCLK DKMS

`RP1-GPCLK-DKMS` provides a stock-kernel, out-of-tree Linux module for bounded
control of the Raspberry Pi RP1 GPCLK0 peripheral. It is the kernel component
used by WsprryPi on Raspberry Pi 5-family hardware and is distributed as source
that DKMS builds for the operator's installed kernel.

The module supplements the stock Raspberry Pi `clk-rp1` driver. It does not
replace the kernel clock provider, require a custom kernel, or expose arbitrary
MMIO, DMA channels, register writes, or GPIO routes to userspace.

## Release status

`1.0.0` / Debian `1.0.0-1` is the current release source, with canonical tag
[`v1.0.0`](https://github.com/WsprryPi/RP1-GPCLK-DKMS/releases/tag/v1.0.0). It includes
both the interlocked consumer and runtime route controller in one DKMS instance.
The UAPI bytes remain canonical; GPIO4 and GPIO20 have separate compatibility
identities and inactive overlays. No target, lifecycle, application or RF
qualification is implied.

Use the [build, validation and publication procedure](docs/operator/release-candidate.md).
Default builds remain unpublished candidates; the explicit `--release` profile
binds the stable tag and release URL. Actual publication requires independent
remote-tag and downloaded-asset verification. All qualification flags stay false.
Exact-source development remains a distinct `source-development` workflow.

## Safety

Installing the package does not select an overlay, edit boot configuration,
load the module, enable a clock, change GPIO state, or authorize transmission.
Both overlays are installed inactive. Route selection, root-only endpoint use,
and product operation are separate administrative decisions. Compatibility IDs
are stable across kernel releases; exact kernel and board identities remain
visible in build and diagnostic records.

Unknown or ambiguous RP1 topology, routes, resources, signing state,
compatibility state, or cleanup state fails closed. Eligibility is established
from the RP1 device-tree/provider/resource structure, not a Raspberry Pi product
model allowlist. Structural acceptance does not make a kernel or board qualified.
There is no `/dev/mem`, raw userspace MMIO, custom-kernel, arbitrary-route, or
alternate-transmitter fallback.

## Installation

For exact-commit development installation, follow the
[source-development guide](docs/operator/source-development.md). The current
`1.0.0` package uses the exact tagged source and checksummed assets. Review the
[identity and migration contract](docs/contracts/development-identity.md)
before installing over an existing version.

DKMS builds the module for eligible installed Raspberry Pi kernel headers. The
package installs the `GPIO4` and `GPIO20` overlays but leaves both inactive. Review
the [package transition and recovery guide](docs/operator/package-lifecycle.md) before making
any route, boot, module, or signing changes.

For a local package-only build from reviewed source:

```sh
dpkg-buildpackage -us -uc -b
```

Building from source requires the Debian packaging toolchain, DKMS development
support, and device-tree compiler. A package build is compatibility evidence
only; it does not qualify installation or hardware behavior on a target.

## Interface

The byte-authoritative userspace header is
[`include/uapi/linux/rp1_gpclk.h`](include/uapi/linux/rp1_gpclk.h). The
[userspace interface contract](docs/contracts/uapi.md) describes queries,
root-only ownership, generic finite events, state, bounded cancellation, passive
snapshots, and immutable test inhibition. This versioned
interface has no legacy layouts or compatibility fallbacks.

The API supports:

- `QUERY` for capabilities and compatibility state;
- `ACQUIRE` and `RELEASE` for exclusive ownership;
- bounded generic tone/gap event submission with fixed coherent DMA chunks;
- `GET_STATE` for stable runtime and terminal state;
- `GET_SNAPSHOT` for passive, non-owning state observation; and
- `STOP` for generation-specific bounded cancellation.

`GPIO4` and `GPIO20` are independent administrative routes. Qualification or
selection of one route never transfers to the other.

## Diagnostics and administration

`rp1-gpclk-diagnostics` produces a bounded, read-only JSON report without
installing, loading, binding, repairing, or operating hardware. See
[Read-only diagnostics](docs/operator/diagnostics.md).

Module signing and trust enrollment remain administrator-owned. The package
does not ship a private key or weaken the host's signing policy. See
[Module signing](docs/operator/signing.md).

## Development

Ordinary development and validation are offline, unprivileged, hardware-free,
and safe to repeat:

```sh
make check
make package-check
```

For a maintainer-facing build/install/load workflow from an exact
Git commit, see [Exact-source development lifecycle](docs/operator/source-development.md).
That path is package-independent and remains explicitly `Experimental`; it does
not create release or qualification identity.
Its route-neutral mode installs the exact DKMS source and module without
selecting a GPIO route, installing an overlay, loading the module, or enabling
output. Route administration and loading remain later explicit operations.

The maintained test inventory and the distinction between automatic,
parameterized build, and explicitly authorized hardware checks are documented
in [Testing](docs/testing.md).

Candidate and frozen release generation use `scripts/build-release-candidate`;
publication follows package lifecycle and exact-candidate WsprryPi acceptance.
A plain Debian build does not produce the complete asset set.

Build the module against an explicitly selected local kernel build tree:

```sh
make KERNEL_BUILD=/path/to/kernel/build
```

Compilation proves build compatibility only. It does not qualify module
loading, GPIO behavior, timing, coexistence, cleanup, transmission, RF, or an
operator installation.

Read [CONTRIBUTING.md](CONTRIBUTING.md), the
[module contract](docs/contracts/rp1-gpclk-dkms-module-contract.md) before contributing. See [LICENSE.md](LICENSE.md)
for licensing terms.

The external qualification boundary is defined by the
[Harness integration contract](docs/contracts/qualification-harness-integration.md).

## Route workflows

`GPIO4` and `GPIO20` are separate routes. With neither overlay active, the route is
`none` and there is no endpoint; two active overlays are ambiguous and rejected.

| Administration profile | Workflow |
| --- | --- |
| Packaged manager | [Configure a route, reboot and reconcile](docs/contracts/route-manager.md) |
| Source-development manager | [Passive query and current-boot adoption](docs/operator/source-development.md) |
| Opt-in runtime manager | [Rebootless `GPIO4`/`GPIO20` switching and recovery to `none`](docs/operator/runtime-manager-workflow.md) |

The runtime profile uses the [runtime controller](docs/contracts/runtime-controller.md)
and [application restoration](docs/contracts/runtime-application-restoration.md).
For diagnosis and removal, see [diagnostics](docs/operator/diagnostics.md) and
[module lifecycle](docs/operator/lifecycle.md). Passive observations and
operation authorization are distinct parts of the
[userspace interface contract](docs/contracts/uapi.md); route selection never
authorizes transmission.

## Project boundary

- This repository owns the kernel module, canonical UAPI, overlays, DKMS
  packaging, module lifecycle tooling, compatibility metadata, and releases.
- [`WsprryPi/WSPR-Transmitter`](https://github.com/WsprryPi/WSPR-Transmitter)
  owns its userspace adapter and conversion into this UAPI.
- [`WsprryPi/WsprryPi`](https://github.com/WsprryPi/WsprryPi) owns application
  policy, configuration, scheduling, installer orchestration, operator
  workflow, and product qualification.

The projects coordinate through tagged artifacts, the canonical UAPI,
compatibility metadata, and explicit cross-repository validation. WsprryPi
does not consume this repository's moving default branch.

## Licensing

Original project work is MIT licensed wherever practical. Kernel-facing module
source and device-tree sources are dual-licensed under `GPL-2.0-only OR MIT`.
The userspace-visible UAPI uses
`(GPL-2.0-only WITH Linux-syscall-note) OR MIT`. Imported material retains its
original license and attribution. See [LICENSE.md](LICENSE.md).
