<!-- SPDX-License-Identifier: MIT -->

# Development identity and installation transitions

The current pre-release development baseline is `0.9.0`. It includes finite and
continuous operations, event timing, exact `GPIO4`/`GPIO20` selection, runtime
switching through none, bounded cancellation/drain and application restoration.
WsprryPi owns present/future modes and product policy; DKMS enforces resource,
ownership, capability and cleanup contracts without a product-mode allowlist.

| Identity | Current development contract |
| --- | --- |
| Product/upstream, consumer module, DKMS version | `0.9.0` |
| Debian version | `0.9.0-1` |
| Package/DKMS name | `rp1-gpclk-dkms` |
| Binary package filename | `rp1-gpclk-dkms_0.9.0-1_all.deb` |
| Consumer module / endpoint | `rp1_gpclk_dkms` / `/dev/rp1-gpclk` |
| Opt-in companion module | `rp1_route_controller`, version `0.9.0`; not default package content |
| Source destination | `/usr/src/rp1-gpclk-dkms-0.9.0` |
| Package schema directory | `/usr/share/rp1-gpclk-dkms/0.9.0` |
| Transmission UAPI | exact `include/uapi/linux/rp1_gpclk.h` bytes and SHA-256 |
| Administrative UAPI | exact `include/uapi/linux/rp1_route_admin.h` bytes |
| Development manifest | `rp1-gpclk-source-development-manifest` |
| Route-manager protocols | packaged/source and runtime profiles |
| `GPIO4` compatibility ID | `v0.9.0-pi5-gpio4` |
| `GPIO20` compatibility ID | `v0.9.0-pi5-gpio20` |
| Classification | `source-development` / `Experimental`; not release-qualified |
| Future tag convention | `vMAJOR.MINOR.PATCH`; no `v0.9.0` tag is created |

Product, Debian, DKMS, UAPI, and schema identities are distinct. Current
compatibility IDs identify the Pi 5 product identity and route. `Experimental`
is reported separately through the UAPI and enrollment state. Kernel release is
recorded in build manifests, diagnostics and enrollment records, but is not part
of the compatibility ID and is not a per-release permission list. Exact hashes
identify each build. Canonical route overlay names and endpoint nodes are stable
and carry no product-version suffix.

An operator may build `0.9.0` through DKMS for another stock Raspberry Pi kernel
and explicitly enroll that installation for `Experimental` use without defining a
new compatibility ID. The running kernel must still be identified, the module
must be built for it, and all hardware, route, resource, ownership, signing and
cleanup checks still apply. Such use establishes no support or qualification
claim. A kernel change can change module bytes and therefore requires the normal
DKMS rebuild and current-installation enrollment checks.

The supported development paths are `development-*` and the opt-in runtime
manager. Release generation and finalization are disabled until the release
pipeline has a reviewed current contract. Local Debian package builds are
unpublished development artifacts, not release qualification.

## Maintainer transition policy

1. **Clean install:** external orchestration uses
   `development-install --route-neutral --live-output 0 --install` from a clean
   exact commit. It installs the DKMS source and module for the named kernel but
   does not select a route, install or apply an overlay, enroll, load, edit boot
   configuration, operate a service, or enable output. Its manifest records
   `route: null` and exact installed identities. A route-specific maintainer may
   instead render the exact `0.9.0` checkout with
   `scripts/render-development-tree --source SOURCE --output NEW_TREE`.
   The renderer derives the version from the canonical source header and changes
   only the DKMS placeholder and explicit development kernel filter.
   `development-install` needs no release package or tag.
2. **Same-version replacement:** the source installer requires the complete
   recorded inventory to match the existing development tree. Foreign files,
   changed bytes, symlinks, package ownership, other kernel instances and stale
   enrollment/manager/runtime state block replacement. It retains `prior-source`
   and original installed/compressed module files in the new evidence directory,
   with hashes and DKMS status in `ROLLBACK.json`, before removing the instance.
3. **Any non-current installation:** no general compatibility, adoption or
   automated migration is claimed. Package and source workflows fail closed on non-current or foreign
   DKMS, source, module, overlay, enrollment, manager, or runtime state. A
   maintainer must separately inventory ownership, quiesce the application,
   prove output/clock/DMA/GPIO cleanup, preserve a recovery point, and use the
   owning workflow to remove only attributable state before a clean install.
   The candidate-provider retirement of an exact prior-boot terminal activation
   journal is one bounded WsprryPi-owned runtime migration, not a general
   exception. There is no force flag or version-normalization bypass.

No transition command grants host, system, GPIO, transmission, or RF authority.
Actual-host installation, removal, and recovery require a reviewed host-specific
plan and separate authorization. Offline fixtures establish only deterministic
workflow behavior.
