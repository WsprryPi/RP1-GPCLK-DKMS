<!-- SPDX-License-Identifier: MIT -->

# RP1 GPCLK DKMS

[![Main documentation](https://app.readthedocs.org/projects/rp1-gpclk-dkms/badge/?version=main)](https://rp1-gpclk-dkms.readthedocs.io/en/main/)

RP1-GPCLK-DKMS provides the kernel modules and managed GPIO route service used
by WsprryPi on Raspberry Pi 5 and Compute Module 5 systems. DKMS builds the
modules for the installed stock Raspberry Pi kernel. The stock `clk-rp1`
driver remains the clock provider; no custom kernel is required.

**Install and manage RP1 support through WsprryPi.** Its installer validates
the provider and establishes route-neutral administration. Use **Setup >
Transmitter** to select GPIO4 (standard 40-pin header pin 7), GPIO20 (pin 38),
or remove the route. Use the carrier's mapping for a custom connector. Only one
route can be active. Installation and route selection do
not start a transmission.

## Operator documentation

The handbook covers setup, operation, maintenance and troubleshooting:

- [Main handbook](https://rp1-gpclk-dkms.readthedocs.io/en/main/)
- [Development handbook](https://rp1-gpclk-dkms.readthedocs.io/en/devel/)
- [Use an installed system](docs/getting-started.md)
- [Install with WsprryPi](docs/installation.md)
- [Select or remove a route](docs/routes.md)
- [Understand status](docs/status.md)
- [Maintenance and recovery](docs/maintenance.md)
- [Troubleshooting and support](docs/troubleshooting.md)

The module supports finite tone/gap sequences, exclusive ownership, passive
status queries and bounded cancellation. Unknown identity, conflicting
ownership or uncertain cleanup blocks operation. A GPIO clock signal requires
an appropriate RF interface and filtering; follow the
[RF and electrical precautions](docs/safety.md) before enabling output.

## Software and support limits

The published software is
[v1.0.0](https://github.com/WsprryPi/RP1-GPCLK-DKMS/releases/tag/v1.0.0),
Debian package **1.0.0-1**. It contains the consumer module, runtime route
controller, canonical userspace interfaces and inactive GPIO4/GPIO20 overlays.
Package installation does not select a route, load a module, edit boot
configuration or authorize output. WsprryPi separately establishes its managed
runtime and restores an explicitly saved RP1 route when eligible.

Use a stock Raspberry Pi kernel with matching eligible headers and the
supported DKMS/signing configuration. Build success establishes build
compatibility only. WsprryPi includes scoped route evidence with the application;
it does not establish every kernel, band, mode or RF setup.
WsprryPi owns application band/mode eligibility and operating policy. See
[how RP1 support works](docs/about.md) and [read provider status](docs/status.md).

## Engineering and contributions

Technical contracts, API details, developer workflows and package/release
procedures are in [engineering/](engineering/README.md), separately from the
operator handbook. Before changing source, read [AGENTS.md](AGENTS.md),
[CONTRIBUTING.md](CONTRIBUTING.md), the
[module contract](engineering/contracts/rp1-gpclk-dkms-module-contract.md) and
[testing guide](engineering/testing.md).

Ordinary offline, unprivileged and hardware-free checks are:

```sh
make check
make package-check
```

Target installation, binding, route administration, GPIO and RF work require
separate authorization. See [documentation maintenance](engineering/documentation.md)
for strict local handbook builds and automatic Read the Docs publication.

## Project ownership and licensing

This repository owns the kernel modules, canonical UAPI, overlays, DKMS
packaging, lifecycle tooling, compatibility metadata and provider releases.
[WSPR-Transmitter](https://github.com/WsprryPi/WSPR-Transmitter) owns the
userspace adapter. [WsprryPi](https://github.com/WsprryPi/WsprryPi) owns
installation orchestration, configuration, scheduling, operator workflow and
product qualification. Production consumption uses explicitly compatible tagged
provider releases; development uses separately identified exact source.

Independent tools, tests and documentation use MIT. Kernel-facing module and
device-tree source uses `GPL-2.0-only OR MIT`; canonical UAPI uses
`(GPL-2.0-only WITH Linux-syscall-note) OR MIT`. Reused scaffold assets retain
their MIT notice. See [LICENSE.md](LICENSE.md).
