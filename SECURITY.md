<!-- SPDX-License-Identifier: MIT -->

# Security policy

The current software release is `v1.0.0` (Debian `1.0.0-1`), identified by the
[maintained release binding](release/software-1.0.0.json). Development builds
remain unqualified. Installation does not qualify a kernel or physical setup;
operations remain limited to the exact systems, routes and behaviors authorized
by their operator. See the [qualification scope](docs/operator/qualification-metadata.md)
for the separately identified release evidence and its exclusions.

Report a suspected vulnerability privately through GitHub's security advisory
feature for `WsprryPi/RP1-GPCLK-DKMS`. Do not include sensitive details in a
public issue.

Security-sensitive areas include:

- UAPI validation and device-node permissions;
- integer bounds, structure sizes, and userspace memory handling;
- DMA destination derivation and transfer bounds;
- clock, pinctrl, DMA, and platform-resource ownership;
- process death, cancellation, callbacks, unbind, and module lifetime;
- signing, DKMS installation, update, rollback, and removal;
- compatibility-manifest and release-artifact integrity; and
- any condition that could leave a GPIO or clock active after failure.

Do not attempt live exploitation, module loading, GPIO manipulation, or RF
testing on systems you do not own or lack explicit authorization to test.
