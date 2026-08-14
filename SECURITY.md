<!-- SPDX-License-Identifier: MIT -->

# Security policy

RP1-GPCLK-DKMS is pre-release engineering work. No version is currently
advertised as supported or qualified for production use.

Please report a suspected vulnerability privately through GitHub's security
advisory feature for `WsprryPi/RP1-GPCLK-DKMS` once the repository is
published. Do not include sensitive details in a public issue before a private
reporting channel is available.

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
