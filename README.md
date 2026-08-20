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

Version 1.0.0 is published. It provides:

- a conventional Debian DKMS source package;
- separately allowlisted GPIO4 and GPIO20 device-tree overlays;
- a bounded, versioned userspace API;
- fail-closed hardware, kernel, route, resource, and compatibility checks;
- exclusive ownership, finite work, cancellation, and cleanup handling; and
- read-only diagnostics plus package lifecycle tooling.

The release was validated on the recorded Raspberry Pi 5 stock-kernel
configuration for inactive installation, output-disabled administration on
both routes, removal, and reinstall. Qualification
does not automatically extend to a different kernel, firmware, device tree,
route, host, or physical installation. See the
[1.0.0 release notes](docs/releases/1.0.0-behavior.md) for the precise claim.

## Safety

Installing the package does not select an overlay, edit boot configuration,
load the module, enable a clock, change GPIO state, or authorize transmission.
Both overlays are installed inactive. Route selection and live operation are
separate administrative decisions that must satisfy the compatibility and
safety policy for the exact system.

Unknown or unsupported hardware, kernels, firmware, device trees, routes,
resources, signing state, compatibility state, or cleanup state fail closed.
There is no `/dev/mem`, raw userspace MMIO, custom-kernel, arbitrary-route, or
alternate-transmitter fallback.

## Installation

Download the Debian package from the
[v1.0.0 release](https://github.com/WsprryPi/RP1-GPCLK-DKMS/releases/tag/v1.0.0)
and install it with the normal Debian package tools:

```sh
sudo apt install ./rp1-gpclk-dkms_1.0.0-1_all.deb
```

DKMS builds the module for eligible installed Raspberry Pi kernel headers. The
package installs the GPIO4 and GPIO20 overlays but leaves both inactive. Review
the [package lifecycle guide](docs/operator/debian-packaging.md) before making
any route, boot, module, or signing changes.

To build the Debian package from a tagged source checkout:

```sh
dpkg-buildpackage -us -uc -b
```

Building from source requires the Debian packaging toolchain, DKMS development
support, and device-tree compiler. A package build is compatibility evidence
only; it does not qualify installation or hardware behavior on a target.

## Interface

The byte-authoritative userspace header is
[`include/uapi/linux/rp1_gpclk.h`](include/uapi/linux/rp1_gpclk.h). The
[UAPI documentation](docs/contracts/uapi-v1.md) describes request validation,
capabilities, ownership, submission, state, cancellation, and additive
evolution rules.

The API supports:

- `QUERY` for capabilities and compatibility state;
- `ACQUIRE` and `RELEASE` for exclusive ownership;
- bounded WSPR and event-program submission;
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

Build the module against an explicitly selected local kernel build tree:

```sh
make KERNEL_BUILD=/path/to/kernel/build
```

Compilation proves build compatibility only. It does not qualify module
loading, GPIO behavior, timing, coexistence, cleanup, transmission, RF, or an
operator installation.

Read [CONTRIBUTING.md](CONTRIBUTING.md), the
[module contract](docs/contracts/rp1-gpclk-dkms-module-contract.md), and
[LICENSE.md](LICENSE.md) before contributing.

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
