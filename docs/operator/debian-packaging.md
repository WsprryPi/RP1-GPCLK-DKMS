<!-- SPDX-License-Identifier: MIT -->

# Debian DKMS packaging

The unpublished candidate is `rp1-gpclk-dkms_1.0.0-1_all.deb`. Use the
[complete candidate procedure](release-candidate.md) to build and independently
validate its exact source, package, inventory, checksums and provenance.
`dpkg-buildpackage --no-sign -b` builds only a local package, without candidate
identity or publication status.

## Package contents

One DKMS instance, `rp1-gpclk-dkms/1.0.0`, owns `rp1_gpclk_dkms` and
`rp1_route_controller`. The package stages their complete source closure below
`/usr/src/rp1-gpclk-dkms-1.0.0`: Kbuild, Makefile, rendered DKMS configuration,
consumer/controller sources, internal headers, both canonical UAPIs, both DTS
sources and the deterministic embedded-overlay generator. DKMS uses the explicit
runtime-controller profile; the consumer has its controller dependency/interlock
and no OF autoload alias. Direct ordinary source builds remain available.

Both overlays remain inactive:

- `/usr/lib/rp1-gpclk-dkms/overlays/rp1-gpclk-gpio4.dtbo`;
- `/usr/lib/rp1-gpclk-dkms/overlays/rp1-gpclk-gpio20.dtbo`.

Systemd unit files are staged directly as data; no systemd debhelper lifecycle
generator is invoked.

The package installs the route executor at `/usr/sbin/rp1-gpclk-route-manager`
and a matching `/usr/libexec/rp1-gpclk-dkms/rp1-gpclk-route-manager`, its versioned
schema, consumer documentation, read-only package preflight and disabled socket
and service template. It creates the `rp1-gpclk-route` group if absent. It does
not enroll application accounts, create runtime bindings/journals, enable or
start a socket, reload systemd, or copy overlays into `/boot`. Firmware-overlay
installation and any route selection remain separately authorized operations.
Runtime tools, private overlays/UAPIs and the WsprryPi companion remain part of
explicit runtime deployment, not package-install effects.

The generated installation manifest inventories every data member, including
directories, modes and SHA-256. Provenance independently records root ownership,
control members and hashes. No system UAPI is installed under `/usr/include`.
No application source or qualification harness is packaged.

## Prerequisites and passive lifecycle

The package requires DKMS 3.2.2 through the 3.2 series, Python,
device-tree-compiler, zstd and adduser. The DKMS bound limits native helper behavior
to the reviewed lifecycle family; older or newer families require explicit
compatibility review rather than silently inheriting passive-install claims. Before
installation, external orchestration supplies exact stock Raspberry Pi headers
for the required kernels. `BUILD_EXCLUSIVE_KERNEL` uses standard exclusion
behavior for kernels outside `+rpt-rpi-2712` and `+rpt-rpi-v8`; it is a build-scope
filter, not qualification. Configuration builds every eligible installed header
tree rather than only the running/newest pair.

Pre-unpack checks reject loaded provider modules, symlinked/foreign payloads and
changed installed package files. Before DKMS effects, preflight requires absent
provider endpoints, routes, runtime/development journals and owned application
inhibitors. Unknown boot includes or existing firmware route nodes require
administrator review. DKMS configuration must be static and use canonical trees;
nonempty `modprobe_on_install`, `post_transaction` or `symlink_modules`, and
package-specific override files, are refused. Even the string `false` is
nonempty to DKMS. Dynamic configuration is not executed by the guard.

For signing-capable header trees, the guard requires an existing administrator
key and certificate before DKMS can generate replacements. Filesystem keys must
be root-owned mode 0600; public certificates must be root-owned and not writable
by group/others. The guard neither reads private key bytes nor creates keys.
Unrecognized signing mechanisms need separate review. See [signing](signing.md).

Installation never selects a route, loads either module, applies an overlay,
changes boot files, operates a service, opens an endpoint or submits output.
Output is unavailable because neither provider module is loaded and no route
is selected. This does not change the immutable production load-time default.

## Transitions, removal and rollback

Debian ordering permits `0.9.0-1` to `1.0.0-1`, repeated installation and
same-version reinstall; a downgrade is refused. Real package lifecycle and
interruption validation, including predecessor maintainer scripts, remain a
separate gate. A build or deterministic fixture does not establish target success.

Before an authorized package removal or upgrade, the owning runtime workflow
must recover/remove routes, unload both modules and remove its deployment.
The package guard refuses retained runtime state. DKMS removes only the named
version and its modules across kernels. Package removal does not interpret or
remove foreign journals, boot state, administrator keys, trust entries or shared
configuration. Former 0.9.0 boot copies require attributable predecessor cleanup.

Retain the exact predecessor package or source/rollback record, its checksums,
installed compressed module bytes, decompressed ELF identities and any runtime
binding/inverse before replacement. An exact rollback uses that predecessor's
owning workflow after verified inactive cleanup of the successor. There is no
force flag, automatic downgrade or invented predecessor package download.

Target-built modules are not package payloads. For each installed kernel and
both module names, record the actual `.ko`, `.ko.xz`, `.ko.gz`, `.ko.zst` or
`.ko.bz2` file SHA-256 separately from the decompressed ELF SHA-256, build note,
vermagic and signing identity. Stripping, signing and compression are explicit
target transforms. The release manifest does not fabricate those values.
