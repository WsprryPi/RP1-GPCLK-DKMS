<!-- SPDX-License-Identifier: MIT -->

# Debian DKMS packaging

Version 1.0.1 uses the standard Debian DKMS lifecycle. Build the package with
`dpkg-buildpackage`; install, upgrade, or remove it with ordinary Debian package
tools. `dh-dkms` provides the DKMS maintainer-script integration.

The product package owns only:

- the module build closure under `/usr/src/rp1-gpclk-dkms-1.0.1`, including
  the canonical UAPI;
- `/usr/lib/rp1-gpclk-dkms/overlays/rp1-gpclk-gpio4.dtbo`; and
- `/usr/lib/rp1-gpclk-dkms/overlays/rp1-gpclk-gpio20.dtbo`.

The maintainer scripts copy the canonical overlays into
`/boot/firmware/overlays` without creating hard-link backups on the boot
filesystem. Installation refuses to replace a different existing file, and
removal deletes only a byte-identical installed copy.

Both overlays remain inactive. The package does not edit `config.txt`, apply an
overlay, select a route, load the module, enable output, or reboot. Installing
the package therefore does not authorize or initiate GPIO activity.

`BUILD_EXCLUSIVE_KERNEL` limits automatic builds to stock Raspberry Pi kernel
package identities ending in `+rpt-rpi-2712` or `+rpt-rpi-v8`. DKMS skips
other installed header trees using its standard exclusion behavior. This name
filter limits build scope; it does not qualify every matching kernel.

## Install

Install the downloaded package with APT so dependencies are resolved:

```sh
sudo apt install ./rp1-gpclk-dkms_1.0.1-1_all.deb
```

After installation, inspect DKMS status and the installed files. Do not select
an overlay or load the module until the exact kernel, firmware, device tree,
route, signing state, and compatibility policy have been reviewed.

## Remove

Remove the package with the normal package manager:

```sh
sudo apt remove rp1-gpclk-dkms
```

Removal does not deactivate an applied overlay, edit boot configuration,
unload an active module, delete administrator signing keys, or repair an
unknown runtime state. Establish an inactive, attributable state before package
removal. A foreign or modified overlay file is retained for administrator
review rather than deleted.

## Build from source

From a tagged source checkout:

```sh
dpkg-buildpackage -us -uc -b
```

The resulting package is a new artifact. Building it successfully establishes
only build compatibility and does not inherit qualification from the published
package.
