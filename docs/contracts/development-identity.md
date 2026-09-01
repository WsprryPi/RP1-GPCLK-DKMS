<!-- SPDX-License-Identifier: MIT -->

# Development identity and installation transitions

The current pre-release development baseline is 0.9.0. It includes finite and
continuous operations, event timing, exact GPIO4/GPIO20 selection, runtime
switching through none, bounded cancellation/drain and application restoration.
WsprryPi owns present/future modes and product policy; DKMS enforces resource,
ownership, capability and cleanup contracts without a product-mode allowlist.

| Identity | Current development contract |
| --- | --- |
| Product/upstream, consumer module, DKMS version | `0.9.0` |
| Debian version | `0.9.0-1` (existing packaging revision convention) |
| Package/DKMS name | `rp1-gpclk-dkms` |
| Binary package filename | `rp1-gpclk-dkms_0.9.0-1_all.deb` |
| Consumer module / endpoint | `rp1_gpclk_dkms` / `/dev/rp1-gpclk` (unchanged) |
| Opt-in companion module | `rp1_route_controller`, version `0.9.0`; not default package content |
| Source destination | `/usr/src/rp1-gpclk-dkms-0.9.0` |
| Package schema directory | `/usr/share/rp1-gpclk-dkms/0.9.0` |
| Transmission UAPI | ABI 4, byte-identical to predecessor |
| Administrative UAPI | `rp1_route_admin.h`, ABI 1, unchanged |
| Development manifest | `rp1-gpclk-source-development-manifest-v1`, unchanged schema |
| Route-manager protocols | packaged/source v1; runtime request schema 3, unchanged |
| GPIO4 compatibility ID | `v0.9.0-pi5-gpio4` |
| GPIO20 compatibility ID | `v0.9.0-pi5-gpio20` |
| Classification | source-development / Experimental; not release-qualified |
| Future tag convention | `vMAJOR.MINOR.PATCH`; no `v0.9.0` tag is created |

Product, Debian, DKMS, UAPI and schema versions are distinct. Current
compatibility IDs identify the Pi 5 product version and route. `Experimental`
is reported separately through the UAPI and enrollment state. Kernel release is
recorded in build manifests, diagnostics and enrollment records, but is not part
of the compatibility ID and is not a per-release permission list. Exact hashes
identify each build. Canonical route overlay names and endpoint nodes are stable
and carry no product-version suffix.

An operator may build 0.9.0 through DKMS for another stock Raspberry Pi kernel
and explicitly enroll that installation for Experimental use without defining a
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
   instead render the exact 0.9.0 checkout with
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
3. **Greater version to 0.9.0:** this is a downgrade. No epoch, force flag, version-ordering
   trick or automatic updater handles it. Source installation rejects predecessor
   DKMS/source/module state. Debian `preinst` rejects a greater installed version
   before unpacking. A maintainer must execute the separately reviewed removal
   and recovery plan below, then use the clean-install path.
4. **0.9.0 to future 1.0.0:** Debian ordering is strictly increasing. Version
   ordering does not establish package lifecycle or real upgrade validation.

### Required explicit migration and recovery plan

No command below grants host, system or hardware authority. Before an actual
transition, produce one host-specific plan with substituted exact paths, versions,
hashes, service states and recovery points; obtain one consolidated authorization.
There is intentionally no general `--force-downgrade` switch.

- Inventory the configured SSH alias, boot ID, kernel, package and DKMS versions,
  `modinfo -n/-F version/-F vermagic`, loaded module version and output gate,
  all canonical module files for every kernel (including compression), versioned
  source trees, overlays, boot ownership, development enrollment, source-manager
  binding/adoption, runtime binding and journals. A missing or foreign owner is
  a stop, not permission to remove it.
- Preserve the original package, all source trees/manifests, installed compressed
  and decompressed module hashes, selected overlays, configuration, service
  states, enrollment and both manager records outside the affected paths.
  Hash the backup and verify it is readable. A version string alone is not a
  recovery point. Retain the earlier exact executors required for removal.
- Quiesce the owning application with its existing reviewed lifecycle. Verify
  global output disabled, no operation owner/lease, closed endpoint and proven
  clock/DMA/pin cleanup. Use the existing runtime manager to reach `none` if it
  owns the route. Keep application inhibition during migration. For a firmware
  route, remove only its attributable boot block and reboot under the plan;
  do not pretend a boot overlay is dynamically removable.
- Roll back adoption and source-manager integration through their exact records;
  remove enrollment with its recorded removal command. Runtime deployments use
  `runtime_deployment.py`'s prepare/apply/recover transaction and exact plan digest
  to preserve/restore predecessor bytes. A digest authorizes no RF. Archive
  completed predecessor state outside the active paths after proving ownership;
  never erase it to bypass a refusal.
- Unload the known consumer/controller only after quiescence. For a Debian-owned
  predecessor, use its exact package removal path. For a source-owned instance,
  use its validated rollback record or exact `dkms remove -m rp1-gpclk-dkms -v
  OLD_VERSION -k EXACT_KERNEL` under the plan. Do not use wildcard or cross-kernel
  removal. Remove/archive only inventory-verified old source and overlay files.
  Preserve unrelated module, package, service, boot and administrator key data.
- Run `depmod -a EXACT_KERNEL`. Require zero stale canonical module candidates,
  no predecessor DKMS entry, no old source destination or active enrollment/
  manager binding, and no foreign file conflict before installing 0.9.0.
- Install exact 0.9.0 with output disabled; verify discovered filename, metadata,
  compressed and ELF hashes, ABI, fresh per-route enrollment, status and manager
  binding. Exercise same-version reinstall only within the approved lifecycle.
  Regenerate runtime deployment bundles from new modules and source. Do not
  load the old runtime consumer against a new controller by guessing compatibility.
- On failure, leave output inhibited. Remove only validated successor objects.
  `development-rollback` checks every path, source-manifest and installed module
  identity before any unload/removal; it removes the successor and retains its
  recovery directory. It does **not** automatically restore a predecessor.
  Restore the retained exact predecessor package/source/DKMS records and exact
  installed files, overlay bytes, enrollment and manager/boot/service state using
  their recorded owning workflow. Compare original hashes and module precedence
  after `depmod`; require output-disabled status before releasing inhibition.
  Restoring a firmware route requires its recorded reboot. If exact restoration
  cannot be demonstrated, retain recovery-required state and stop.

The maintained runtime filesystem transaction already saves exact old bytes,
serializes changes and checks unchanged preconditions before apply/recover.
Its opt-in explicit plan is a maintainer migration path, not a normal package
updater. It must be reviewed as a downgrade when installed module metadata is
greater than 0.9.0.
Actual-host validation must exercise this migration/rollback policy; offline
fixtures do not establish actual-host package or DKMS success.
