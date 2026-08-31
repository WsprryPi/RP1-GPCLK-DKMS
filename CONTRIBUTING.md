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

## Current-state documentation

Describe current capabilities, interfaces, prerequisites, limitations and operating
procedures. Keep durable technical contracts and necessary source provenance.
Do not add phase histories, completed handoff prompts, task completion reports,
recorded test output or qualification campaigns to the repository. Report task
results and validation in the execution chat. Do not create replacement archives.

Keep maintained tests and compact deterministic fixtures. Build, package, runtime,
update and integrity metadata must remain when consumed by current workflows.
Generated run artifacts belong outside the checkout; test output is temporary.
A passing test supports only the behavior it exercises and grants no target or
RF authorization. Keep WsprryPi mode and product policy outside this module.
