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

Version 0.9.0 is the current pre-release development baseline, preserving the
mature ABI-v4 implementation and independent GPIO4/GPIO20 runtime routes.
Source/DKMS/module version `0.9.0` and Debian version `0.9.0-1` are coordinated
labels, not frozen artifacts or qualification. See the
[development identity and migration contract](docs/contracts/development-identity.md).
Earlier 1.x releases and candidate evidence retain their original identities.
Development eligibility remains `Experimental`.

## Safety

Installing the package does not select an overlay, edit boot configuration,
load the module, enable a clock, change GPIO state, or authorize transmission.
Both overlays are installed inactive. Route selection, Experimental enrollment,
and live operation are separate administrative decisions. Compatibility IDs are
stable across kernel releases; the exact kernel remains visible in build and
diagnostic records.

Unknown hardware, routes, resources, signing state, compatibility state, or
cleanup state fail closed. Operators may explicitly enroll an identified 0.9.0
DKMS build on another stock Raspberry Pi kernel as Experimental; that does not
make the kernel supported or qualified.
There is no `/dev/mem`, raw userspace MMIO, custom-kernel, arbitrary-route, or
alternate-transmitter fallback.

## Installation

For exact-commit development installation, follow the
[source-development guide](docs/operator/source-development.md). The current
0.9.0 package is an unpublished development artifact; the public 1.0.0 release
is not this development build. Review the
[identity and migration contract](docs/contracts/development-identity.md)
before installing over an existing version.

DKMS builds the module for eligible installed Raspberry Pi kernel headers. The
package installs the GPIO4 and GPIO20 overlays but leaves both inactive. Review
the [package lifecycle guide](docs/operator/debian-packaging.md) before making
any route, boot, module, or signing changes.

To build an unpublished development package from the reviewed source checkout:

```sh
dpkg-buildpackage -us -uc -b
```

Building from source requires the Debian packaging toolchain, DKMS development
support, and device-tree compiler. A package build is compatibility evidence
only; it does not qualify installation or hardware behavior on a target.

## Interface

The byte-authoritative userspace header is
[`include/uapi/linux/rp1_gpclk.h`](include/uapi/linux/rp1_gpclk.h). The
[ABI v2 UAPI documentation](docs/contracts/uapi-v2.md) describes negotiation,
explicit continuous and finite TONE requests, ownership, state, cancellation,
and preserved ABI v1 behavior.

The API supports:

- `QUERY` for capabilities and compatibility state;
- `ACQUIRE` and `RELEASE` for exclusive ownership;
- bounded WSPR and keyed-event submission;
- explicit continuous and kernel-bounded finite TONE submission;
- `GET_STATE` for stable runtime and terminal state; and
- `STOP` for generation-specific bounded cancellation.

GPIO4 and GPIO20 are independent administrative routes. Qualification or
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

For a maintainer-facing build/install/load workflow from an exact unreleased
Git commit, see [Exact-source development lifecycle](docs/operator/source-development.md).
That path is package-independent and remains explicitly Experimental; it does
not create release or qualification identity.
Its route-neutral mode installs the exact DKMS source and module without
selecting a GPIO route, installing an overlay, loading the module, or enabling
output. Route administration and loading remain later explicit operations.

The maintained test inventory and the distinction between automatic,
parameterized build, and explicitly authorized hardware checks are documented
in [Testing](docs/testing.md).

Release generation and publication are disabled pending a reviewed current
release pipeline. Use the development installer or local Debian build above.

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

GPIO4 and GPIO20 are separate routes. With neither overlay active, the route is
`none` and there is no endpoint; two active overlays are ambiguous and rejected.

| Administration profile | Workflow |
| --- | --- |
| Packaged v1 manager | [Configure a route, reboot and reconcile](docs/contracts/route-manager-v1.md) |
| Source-development v1 manager | [Passive query and current-boot adoption](docs/operator/source-development.md) |
| Opt-in runtime manager, schema 3 | [Rebootless GPIO4/GPIO20 switching and recovery to none](docs/operator/runtime-manager-workflow.md) |

The runtime profile uses the [runtime controller](docs/contracts/runtime-controller-v1.md)
and [application restoration](docs/contracts/runtime-application-restoration-v1.md).
For diagnosis and removal, see [diagnostics](docs/operator/diagnostics.md) and
[module lifecycle](docs/operator/lifecycle.md). Passive observations and
[ABI-v4 operation authorization](docs/contracts/uapi-v4-operation-live.md)
are distinct; route selection never authorizes transmission.

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
