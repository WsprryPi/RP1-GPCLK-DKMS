<!-- SPDX-License-Identifier: MIT -->

# Debian DKMS packaging

The planned Version 0.9.0 package uses the standard Debian DKMS lifecycle.
After the later package-freeze gate, build it with `dpkg-buildpackage`; install,
upgrade, or remove a reviewed artifact with ordinary Debian package tools.
`dh-dkms` provides the DKMS maintainer-script integration. No 0.9.0 package or
final package identity is frozen by the current functional-development state.

The product package owns:

- the module build closure under `/usr/src/rp1-gpclk-dkms-0.9.0`, including
  the canonical UAPI at
  `/usr/src/rp1-gpclk-dkms-0.9.0/include/uapi/linux/rp1_gpclk.h`;
- `/usr/lib/rp1-gpclk-dkms/overlays/rp1-gpclk-gpio4.dtbo`; and
- `/usr/lib/rp1-gpclk-dkms/overlays/rp1-gpclk-gpio20.dtbo`.

The Debian package does not install a system header under `/usr/include` or the
qualification harness. Those artifacts have distinct ownership and are not
part of the binary package file list.

The maintainer scripts copy the canonical overlays into
`/boot/firmware/overlays` without creating hard-link backups on the boot
filesystem. Installation refuses to replace a different existing file, and
removal deletes only a byte-identical installed copy.

Both overlays remain inactive. The package does not edit `config.txt`, apply an
overlay, select a route, load the module, enable output, or reboot. Installing
the package therefore does not authorize or initiate GPIO activity.

Version 0.9.0 additionally installs the stable application executor at
`/usr/sbin/rp1-gpclk-route-manager` (with a byte-identical package-owned copy
at `/usr/libexec/rp1-gpclk-dkms/rp1-gpclk-route-manager`), its closed JSON schema
at `/usr/share/rp1-gpclk-dkms/0.9.0/rp1-gpclk-route-manager-v1.schema.json`,
and its consumer contract at
`/usr/share/doc/rp1-gpclk-dkms/route-manager-v1.md`. These are the only route
manager executable/data additions. The package also installs disabled
`rp1-gpclk-route-manager.socket` and `rp1-gpclk-route-manager@.service` units,
creates the restricted `rp1-gpclk-route` group, and creates only the empty
`/var/lib/rp1-gpclk-dkms` state parent. It does not enroll WsprryPi, enable or
start the socket, create the owned boot block, or create a transaction journal.
Journals are created only by an explicitly executed root mutation.

The supported interactive transport is the fixed group-restricted Unix socket
at `/run/rp1-gpclk-dkms/route-manager.sock`. WsprryPi installation policy may
explicitly enroll its fixed service account in `rp1-gpclk-route` and enable the
socket. Each connection starts the root executor in a separate systemd service
cgroup with JSON on the socket as standard input/output. No arbitrary sudo,
command argument, path, wrapper, or shell is accepted.

`BUILD_EXCLUSIVE_KERNEL` limits automatic builds to stock Raspberry Pi kernel
package identities ending in `+rpt-rpi-2712` or `+rpt-rpi-v8`. DKMS skips
other installed header trees using its standard exclusion behavior. This name
filter limits build scope; it does not qualify every matching kernel.

The package depends on DKMS, but it intentionally does not recommend the broad
Debian linux-headers-arm64 metapackage. Before installation, the consuming
installer must resolve and install the exact running-kernel package named
linux-headers-$(uname -r), verify the matching
/usr/src/linux-headers-$(uname -r) tree, and fail closed if either is
unavailable. A generic architecture header package is not evidence for a
Raspberry Pi kernel identity.

The source-package build dependencies are debhelper-compat (= 13), dh-dkms,
device-tree-compiler, and python3. They belong on the package build host and
are not WsprryPi runtime dependencies.

## Install

After a reviewed 0.9.0 package is produced in the later packaging roadmap step,
install that downloaded artifact with APT so dependencies are resolved:

```sh
sudo apt install ./rp1-gpclk-dkms_0.9.0-1_all.deb
```

After installation, inspect DKMS status and the installed files. Do not select
an overlay or load the module until the exact kernel, firmware, device tree,
route, signing state, and compatibility policy have been reviewed.

DKMS strips debug symbols by default before installing this module. Validate
`moduleUnsignedSha256` against the unstripped exact-kernel build artifact and
validate `moduleInstalledSha256` against the uncompressed ELF after applying
the manifest's `moduleInstalledTransform`. Also record the hash of the actual
installed `.ko`, `.ko.xz`, `.ko.gz`, or `.ko.zst` file separately; filesystem
compression is packaging evidence and is not the normalized installed ELF
identity.

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

For the intended source version `0.9.0`, the coordinated binary package label
is `0.9.0-1`, the intended artifact name is
`rp1-gpclk-dkms_0.9.0-1_all.deb`, and the eventual release tag is `v0.9.0`.
These names do not freeze source, UAPI, overlay, compatibility, inventory,
hash, artifact, or consumer identities. Do not build a release artifact from a
moving branch.

The resulting package is a new artifact. Building it successfully establishes
only build compatibility and does not establish qualification or release
eligibility. Fresh release metadata, validators, checksums, and publication
controls will be added when the canonical release candidate is prepared. A
local `dpkg-buildpackage -us -uc -b` build remains an unpublished development
artifact. See the [version and downgrade contract](../contracts/development-identity.md).
