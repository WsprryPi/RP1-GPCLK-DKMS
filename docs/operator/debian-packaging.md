<!-- SPDX-License-Identifier: MIT -->

# Debian DKMS packaging

Phase 5.54 uses the standard Debian DKMS lifecycle. Build the package with
`dpkg-buildpackage`; install, upgrade, or remove it with the ordinary Debian
package tools. `dh-dkms` generates the DKMS maintainer-script integration.

The product package owns only:

- the module build closure under
  `/usr/src/rp1-gpclk-dkms-0.0.0-phase5.54`, including the canonical UAPI;
- `/boot/firmware/overlays/rp1-gpclk-gpio4.dtbo`; and
- `/boot/firmware/overlays/rp1-gpclk-gpio20.dtbo`.

Both overlays are installed but inactive. The package does not edit
`config.txt`, apply an overlay, or load the module. Qualification tools,
controls, evidence, and ledgers are not package members. A separately
authorized qualification run compiles its UAPI probe from the installed
versioned DKMS source closure.

The Phase 5.53 archive administrator and product ledger are historical. A
target that has that development installation requires one separately
authorized, verified reset before the Debian package is installed; the Debian
package must not guess at or silently remove those unowned files.
