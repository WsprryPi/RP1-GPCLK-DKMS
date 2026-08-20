<!-- SPDX-License-Identifier: MIT -->

# Debian DKMS packaging

Phase 5.54 uses the standard Debian DKMS lifecycle. Build the package with
`dpkg-buildpackage`; install, upgrade, or remove it with the ordinary Debian
package tools. `dh-dkms` generates the DKMS maintainer-script integration.

The product package owns only:

- the module build closure under
  `/usr/src/rp1-gpclk-dkms-0.0.0-phase5.54`, including the canonical UAPI;
- `/usr/lib/rp1-gpclk-dkms/overlays/rp1-gpclk-gpio4.dtbo`; and
- `/usr/lib/rp1-gpclk-dkms/overlays/rp1-gpclk-gpio20.dtbo`.

The maintainer scripts copy those two canonical overlays into
`/boot/firmware/overlays` without making `dpkg` create hard-link backups on
the boot filesystem. Installation refuses to replace a different existing
file, and removal deletes only a byte-identical installed copy. Both overlays
remain inactive. The package does not edit
`config.txt`, apply an overlay, or load the module. Qualification tools,
controls, evidence, and ledgers are not package members. A separately
authorized qualification run compiles its UAPI probe from the installed
versioned DKMS source closure.

`BUILD_EXCLUSIVE_KERNEL` limits automatic builds to stock Raspberry Pi kernel
package identities ending in `+rpt-rpi-2712` or `+rpt-rpi-v8`. DKMS skips
other installed header trees, including historical custom kernels, with its
standard exit-77 exclusion. This name filter is a build-scope guard, not a
compatibility or qualification claim for every matching kernel.

The Phase 5.53 archive administrator and product ledger are historical. A
target that has that development installation requires one separately
authorized, verified reset before the Debian package is installed; the Debian
package must not guess at or silently remove those unowned files.
