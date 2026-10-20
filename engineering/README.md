<!-- SPDX-License-Identifier: MIT -->

# Engineering reference

The published [operator handbook](../docs/index.md) covers WsprryPi-managed
installation, route control, status and recovery. This directory holds the
technical contracts and procedures needed to maintain the provider.

## Contracts

- [Module ownership, safety, compatibility and distribution](contracts/rp1-gpclk-dkms-module-contract.md)
- [Canonical userspace interface](contracts/uapi.md)
- [Route manager](contracts/route-manager.md)
- [Runtime controller](contracts/runtime-controller.md)
- [Application restoration](contracts/runtime-application-restoration.md)
- [Runtime output reconciliation](contracts/runtime-output.md)
- [Runtime updates](contracts/runtime-update.md)
- [Exact development identity](contracts/development-identity.md)
- [External qualification harness integration](contracts/qualification-harness-integration.md)

## Development and administration

- [Testing and maintained inventory](testing.md)
- [Exact-source development](operations/source-development.md)
- [Runtime deployment and route workflow](operations/runtime-manager-workflow.md)
- [Debian packaging](operations/debian-packaging.md)
- [Package transitions, recovery and rollback](operations/package-lifecycle.md)
- [Module lifecycle](operations/lifecycle.md)
- [Signing and trust](operations/signing.md)
- [Diagnostics implementation and limits](operations/diagnostics.md)
- [Release build and publication](operations/release-candidate.md)
- [Documentation maintenance and publication](documentation.md)

These procedures do not grant installation, module/overlay, GPIO, transmission
or RF authorization. Follow the applicable ownership and safety contract.
