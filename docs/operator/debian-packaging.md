<!-- SPDX-License-Identifier: MIT -->

# Debian DKMS packaging

Version 1.1.1 uses the standard Debian DKMS lifecycle. Build the package with
`dpkg-buildpackage`; install, upgrade, or remove it with ordinary Debian package
tools. `dh-dkms` provides the DKMS maintainer-script integration.

The product package owns only:

- the module build closure under `/usr/src/rp1-gpclk-dkms-1.1.1`, including
  the canonical UAPI at
  `/usr/src/rp1-gpclk-dkms-1.1.1/include/uapi/linux/rp1_gpclk.h`;
- `/usr/lib/rp1-gpclk-dkms/overlays/rp1-gpclk-gpio4.dtbo`; and
- `/usr/lib/rp1-gpclk-dkms/overlays/rp1-gpclk-gpio20.dtbo`.

The Debian package does not install a system header under `/usr/include`, the
qualification harness, or the optional administration and diagnostic tooling
described by the separate source-release installation model. Those artifacts
have distinct ownership and are not part of the binary package file list.

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

Install the downloaded package with APT so dependencies are resolved:

```sh
sudo apt install ./rp1-gpclk-dkms_1.1.1-1_all.deb
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

For source version `1.1.1`, the binary package version is `1.1.1-1` and the
expected artifact name is `rp1-gpclk-dkms_1.1.1-1_all.deb`. The eventual
release tag is `v1.1.1`; do not build a release artifact from a moving branch.

The resulting package is a new artifact. Building it successfully establishes
only build compatibility and does not inherit qualification from the published
package.


## Preliminary candidate validation

`build_release_candidate.py` and `validate_release_candidate.py` are a strict
pair for the preliminary Debian/DKMS candidate set. Validate a generated set
with:

```sh
make validate-release-candidate OUTPUT_DIR=/path/to/release-set \
    SOURCE_COMMIT=EXACT_40_HEX_COMMIT
```

The validator independently parses the Debian archive, recomputes its member
inventory and all sidecar/archive hashes, verifies source/version/UAPI/overlay
identity, and requires GPIO4 and GPIO20 to remain unavailable and non-live.
`validate_release.py` remains intentionally scoped to the separately generated
published-release archive layout; the two validators are not interchangeable.
