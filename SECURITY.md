<!-- SPDX-License-Identifier: MIT -->

# Security policy

Version 1.0.0 is the current published release. Its qualification is limited to
the systems and behaviors stated in the release notes; publication does not
make every Raspberry Pi kernel or physical installation supported.

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
