<!-- SPDX-License-Identifier: MIT -->

# Contributing

Thank you for helping improve RP1-GPCLK-DKMS.

Before contributing:

1. Read [AGENTS.md](AGENTS.md), the
   [module contract](docs/contracts/rp1-gpclk-dkms-module-contract.md), and
   [licensing policy](LICENSE.md).
2. Keep the change within one explicit phase and repository boundary.
3. Preserve fail-closed behavior and do not broaden hardware support or
   qualification claims without evidence.
4. Add deterministic, hardware-free tests for implementation changes wherever
   possible.
5. Record exact kernel-header, toolchain, architecture, and compatibility
   identities for build evidence.
6. Keep target installation, module loading, GPIO, transmission, and RF tests
   separately authorized and reported.

Original contributions are accepted under the SPDX expression already assigned
to the destination file. New files should follow the matrix in
[LICENSE.md](LICENSE.md). Identify copied, generated, or adapted material and
its provenance in the contribution.

A pull request should state implemented behavior, tests run, skipped checks,
hardware or system effects, compatibility implications, documentation impact,
and remaining qualification.
