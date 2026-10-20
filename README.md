<!-- SPDX-License-Identifier: MIT -->

# RP1 GPCLK DKMS

`RP1-GPCLK-DKMS` provides a Linux kernel module for bounded control of the
Raspberry Pi RP1 GPCLK0 peripheral. WsprryPi uses it on Raspberry Pi 5-family
hardware. DKMS builds the module for the operator's installed stock Raspberry
Pi kernel.

The module supports finite tone/gap sequences, exclusive ownership, passive
status queries and bounded cancellation. GPIO4 and GPIO20 are separate
administrative routes. Only one route can be active at a time; selecting a
route does not authorize output.

The stock Raspberry Pi `clk-rp1` driver remains the clock provider. The module
requires no custom kernel and exposes no arbitrary memory access, DMA channels,
register writes or GPIO routes to userspace.

## Current release and support limits

The current software release is
[`v1.0.0`](https://github.com/WsprryPi/RP1-GPCLK-DKMS/releases/tag/v1.0.0),
Debian package `1.0.0-1`. It includes the consumer module, runtime route
controller, canonical userspace interface and inactive GPIO4/GPIO20 overlays.
Use the published package and checksummed assets from that exact release.

The separately identified qualification supplement describes the accepted
systems, routes and finite conducted TONE cases for this release. It does not
establish support for every kernel, band, mode or physical setup. WsprryPi owns
application eligibility and operating policy. See
[qualification scope and installed status](docs/operator/qualification-metadata.md)
for applicability and exclusions. Qualification of one route never transfers
to the other.

Maintenance checkouts have their own source identities and do not replace the
published release. Contributors can use the
[release procedure](docs/operator/release-candidate.md) to verify source and
package identities.

## Prerequisites and installation

Use a stock Raspberry Pi kernel with matching eligible kernel headers, DKMS
and the device-tree tools required by the package. The actual RP1 topology,
clock and DMA providers, resource ownership and selected route must match the
module contract. Signing and trust requirements depend on the installed
kernel's policy. Unknown or ambiguous state is refused; there is no alternate
hardware backend.

Installing the package builds its modules and installs both overlays inactive.
It does not edit boot configuration, load a module, select a route, change GPIO
state or authorize transmission. Review the
[package prerequisites](docs/operator/debian-packaging.md) and
[installation, update and recovery procedure](docs/operator/package-lifecycle.md)
before making administrative changes.

Module signing and trust enrollment are administrator-owned. The package ships
no private key and does not weaken the host's signing policy. See
[module signing](docs/operator/signing.md).

## Select and manage a route

GPIO4 and GPIO20 have distinct overlays and compatibility identities. With
neither overlay active, the route is `none` and there is no consumer endpoint.
Two active overlays are ambiguous and rejected.

| Administration profile | Workflow |
| --- | --- |
| Packaged manager | [Configure a route, reboot and reconcile](docs/contracts/route-manager.md) |
| Source development | [Install an exact source identity and adopt the current boot](docs/operator/source-development.md) |
| Opt-in runtime manager | [Switch GPIO4/GPIO20 without rebooting and recover to none](docs/operator/runtime-manager-workflow.md) |

The runtime manager serializes route changes and restores application service
intent after a successful transition. Failed or unresolved transactions retain
output inhibition and require recovery. Follow the selected profile's procedure;
a saved route or successful status query is not permission to transmit.

## Interface and diagnostics

The consumer endpoint is `/dev/rp1-gpclk`, a root-owned, root-only device. One
open file can own one lease and submit a bounded finite sequence. Cancellation
prevents successors and drains at most the current fixed DMA chunk before
cleanup. Passive queries do not grant ownership or output authority.

The API supports:

- `QUERY` for capabilities and compatibility state;
- `ACQUIRE` and `RELEASE` for exclusive ownership;
- bounded generic tone/gap event submission;
- `GET_STATE` for runtime and terminal state;
- `GET_SNAPSHOT` for passive, non-owning observations; and
- `STOP` for generation-specific bounded cancellation.

The canonical header is
[`include/uapi/linux/rp1_gpclk.h`](include/uapi/linux/rp1_gpclk.h). The
[userspace interface contract](docs/contracts/uapi.md) defines layouts, limits,
state and immutable test inhibition. The interface has no legacy-layout
fallbacks.

`rp1-gpclk-diagnostics` produces a bounded, read-only JSON report without
installing, loading, binding, repairing or operating hardware. Follow the
[diagnostic procedure](docs/operator/diagnostics.md) to interpret its status.
For removal and recovery, see the [module lifecycle guide](docs/operator/lifecycle.md).

## Development

Ordinary development checks are offline, unprivileged and hardware-free:

```sh
make check
make package-check
```

Read [CONTRIBUTING.md](CONTRIBUTING.md), the
[module contract](docs/contracts/rp1-gpclk-dkms-module-contract.md) and
[maintained test inventory](docs/testing.md) before changing the source. The
[source-development procedure](docs/operator/source-development.md) provides a
separate, explicitly Experimental path for exact-commit work. Installation,
loading, binding, route administration and output each retain their documented
authorization requirements.

A successful module build proves build compatibility only. It does not qualify target
behavior, timing, coexistence, cleanup, transmission or RF performance. External
qualification follows the
[harness integration contract](docs/contracts/qualification-harness-integration.md).

## Project boundary

- This repository owns the kernel module, canonical UAPI, overlays, DKMS
  packaging, module lifecycle tooling, compatibility metadata and releases.
- [`WsprryPi/WSPR-Transmitter`](https://github.com/WsprryPi/WSPR-Transmitter)
  owns its userspace adapter and conversion into this UAPI.
- [`WsprryPi/WsprryPi`](https://github.com/WsprryPi/WsprryPi) owns application
  policy, configuration, scheduling, installer orchestration, operator workflow
  and product qualification.

The projects coordinate through tagged artifacts, the canonical UAPI,
compatibility metadata and explicit cross-repository validation. WsprryPi does
not consume this repository's moving default branch.

## Licensing

Independent original tools, tests and documentation use MIT. Kernel-facing
module and device-tree sources use `GPL-2.0-only OR MIT`. Canonical
userspace-visible UAPI headers use
`(GPL-2.0-only WITH Linux-syscall-note) OR MIT`. Imported material retains its
license and attribution. See [LICENSE.md](LICENSE.md).
