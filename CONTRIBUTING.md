<!-- SPDX-License-Identifier: MIT -->

# Contributing

Thank you for helping improve RP1-GPCLK-DKMS.

Before contributing, read [AGENTS.md](AGENTS.md), the
[module contract](docs/contracts/rp1-gpclk-dkms-module-contract.md), and
[licensing policy](LICENSE.md).

Keep changes within this repository's ownership boundary and preserve its
fail-closed safety model. New hardware, routes, kernels, capabilities, or
qualification claims require explicit supporting evidence; build success alone
is not enough. Add deterministic, hardware-free tests for implementation
changes wherever practical.

Record the kernel headers, toolchain, architecture, module version, and UAPI
version used for build-compatibility results. Keep installation, module
loading, binding, GPIO, transmission, and RF validation separately authorized
and clearly labeled.

Original contributions are accepted under the SPDX expression already assigned
to the destination file. New files follow the matrix in [LICENSE.md](LICENSE.md).
Identify copied, generated, or adapted material and preserve its provenance and
license.

A pull request should describe the behavior changed, tests run, skipped checks,
hardware or system effects, compatibility implications, documentation impact,
and remaining validation.
