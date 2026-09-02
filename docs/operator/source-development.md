<!-- SPDX-License-Identifier: MIT -->

# Exact-source development lifecycle

`source-development` deployment remains passive-query-only. It is not deployment
enrollment or route authorization, and no automatic route startup service is
provided.

`python3 scripts/runtime_inventory.py` is a separate bounded read-only collector.
It accepts no arguments, never opens the RP1 endpoint and never invokes
dtoverlay. Unreadable files and unavailable commands remain unknown. With
explicit read-only host authorization it can be run through SSH stdin without
installation. Its non-atomic report and candidate boot directives never grant
route administration. Matching build notes corroborate artifact identity but do not establish a
full hash of executing module memory. See [diagnostics](diagnostics.md) for
observation limits.

This workflow builds an explicitly selected Git commit directly on a Raspberry
Pi. It does not require or create a Debian package, release manifest, tag,
compatibility freeze, or qualification claim. Every result is visibly
`source-development` and at most `Experimental`.

The canonical Kbuild and installed module name is `rp1_gpclk_dkms`; the DKMS
package name is `rp1-gpclk-dkms`; the endpoint is `/dev/rp1-gpclk`. Do not guess
`rp1_gpclk`. The maintained commands resolve the installed `.ko`, `.ko.xz`,
`.ko.zst`, `.ko.gz`, or `.ko.bz2` through module metadata and report both the
installed-file and decompressed-ELF hashes.

## Primary path

For a clean route-neutral installation suitable for external installer
orchestration, use:

```sh
git checkout EXACT_COMMIT

./scripts/development-preflight --kernel "$(uname -r)"

sudo ./scripts/development-install \
  --kernel "$(uname -r)" \
  --route-neutral \
  --live-output 0 \
  --install \
  --evidence-directory /absolute/evidence/path
```

This mode requires no configured or active RP1 GPCLK route, installed route
overlay, loaded consumer, or endpoint before and after installation. It requires
a clean source commit and rejects `--load`, `live_output=1`, and a simultaneous
GPIO route. The resulting `DEVELOPMENT_MANIFEST.json` records `route: null`, the
target kernel, installed and decompressed module hashes, UAPI hash,
output-disabled parameters, and pre/post route-neutral observations.
The preflight and installer derive the module version from the exact source
checkout's canonical `include/rp1_gpclk/version.h`; callers cannot substitute a
different development version.
`RESULT.json` points to that manifest and its rollback record. Neither file
authorizes route selection, module loading, output, or qualification.

An installer that requires rebootless runtime administration adds the explicit
`--runtime-controller` flag to that route-neutral command. This selects a
separate DKMS build profile whose single DKMS instance owns both
`rp1_gpclk_dkms` and `rp1_route_controller`. The manifest and rollback record
bind both installed-file and decompressed-ELF digests. The consumer must expose
the controller interlock and dependency and no OF autoload alias. Ordinary
source-development installation omits this flag and remains a one-module profile.
Neither profile loads a module in route-neutral mode.

Route-specific development remains separate. Use the maintained overlay,
route, enrollment, and module commands only under their own reviewed
authorization. The combined workflow below remains available when one explicit
route and load operation are already within the authorized scope.

```sh
git checkout EXACT_COMMIT

./scripts/development-preflight --kernel "$(uname -r)"

sudo ./scripts/development-install \
  --kernel "$(uname -r)" \
  --route gpio4 \
  --live-output 0 \
  --load \
  --evidence-directory /absolute/evidence/path

./scripts/development-status \
  --manifest /absolute/evidence/path/rendered-source/DEVELOPMENT_MANIFEST.json \
  --json
```

Use `--live-output 1` only inside a separately authorized plan with the exact
route, topology, compatibility identity, cleanup controls, and operator window.
Installation or loading alone does not authorize GPIO, GPCLK, transmission, or
RF activity.

The installer prints one kernel-identity object before mutation, resolves tools
from fixed noninteractive system locations, renders only tracked inputs without
modifying the checkout, records the exact commit and any explicitly allowed
dirty state, registers and builds with DKMS, installs for the requested kernel,
runs `depmod`, resolves the real module artifact, verifies version and vermagic,
and optionally loads with an explicit `live_output` value. Detailed command
output is retained in the evidence directory. Use `--build-only`, `--install`,
`--load`, and `--keep-build` to select the lifecycle. A same-name, same-version
development instance is replaced only after complete source-ownership validation.
The evidence directory retains its source and installed module bytes for recovery.
Non-current versions, foreign/package ownership, and active enrollment or manager
state require the [explicit removal boundary](../contracts/development-identity.md).
A rendered development tree deliberately replaces the production DKMS kernel
name filter with `.*`. The requested kernel only needs a usable header tree;
DKMS/compiler errors are returned directly. The release/package source retains
its stock Raspberry Pi kernel filter unchanged.
A non-running kernel may be built and installed but cannot be reported loaded.
Route-neutral mode never unloads a running instance for replacement; any loaded
module, route, endpoint, or installed route overlay is a preflight refusal.

## Separate operations

```sh
./scripts/render-development-tree --source . --output /absolute/tree

sudo ./scripts/development-enroll --manifest MANIFEST --route gpio4 --kernel "$(uname -r)"
sudo ./scripts/development-module load --live-output 0 --manifest MANIFEST
sudo ./scripts/development-module reload --live-output 0 --manifest MANIFEST
./scripts/development-module status --manifest MANIFEST
./scripts/development-endpoint --manifest MANIFEST --json
sudo ./scripts/development-module unload --manifest MANIFEST

sudo ./scripts/development-overlay build --manifest MANIFEST --output /absolute/overlay-build
sudo ./scripts/development-overlay install --manifest MANIFEST --output /absolute/overlay-build
sudo ./scripts/development-route apply --route gpio4 --development-manifest MANIFEST
./scripts/development-route verify --development-manifest MANIFEST
sudo ./scripts/development-route rollback --development-manifest MANIFEST
sudo ./scripts/development-overlay rollback --manifest MANIFEST
```

Before enrolling, query the loaded module and require compatibility ID
`v0.9.0-pi5-gpio4` or `v0.9.0-pi5-gpio20` for the selected route. If an existing
`0.9.0` installation reports another identifier, keep output inhibited, remove
its enrollment using the removal command in that enrollment record, perform the
guarded same-version replacement, and enroll the current installation. Do not
edit an enrollment record or substitute an expected identifier for the value
reported by the module.

Overlay installation and route application report affected files, identities,
ownership, removal evidence, and whether reboot is required.
They never reboot automatically. `GPIO4` and `GPIO20` remain independent; a
manifest or active identity for one never substitutes for the other. After an
approved reboot, run the read-only status and route verification commands.

The status state progresses through `development-built`,
`development-installed`, `development-loaded`, `development-endpoint-ready`,
and `development-live-enabled`. `release-qualified` is deliberately separate
and is never produced by this workflow.

## Passive exact-source route manager

For an exact-source `Experimental` installation, install the route manager from
a clean, exact Git checkout without replacing package-owned files:

```sh
sudo ./scripts/development-route-manager install \
  --source /absolute/clean/checkout \
  --module-manifest /absolute/module/DEVELOPMENT_MANIFEST.json \
  --kernel "$(uname -r)" --route gpio4
sudo ./scripts/development-route-manager adopt-current-boot
sudo ./scripts/development-route-manager status
sudo ./scripts/development-route-manager rollback-adoption
sudo ./scripts/development-route-manager rollback
```

The installer copies the executable and module manifest below
`/opt/rp1-gpclk-dkms-development/COMMIT`, records their separate source
commits and hashes, and activates only a drop-in below `/etc/systemd/system`.
The package executables and unit fragment remain unchanged. Installation alone
is reported as `deployed-awaiting-current-boot-adoption`, not ready. The
installer preserves a validated terminal `rolled-back` prior record under
the same root-owned development state directory and binds its path and digest
into the current record. Active, malformed, altered, or archive-colliding prior
state fails closed.
The explicit adoption operation records the observed boot ID, complete boot
configuration digest, configured and active route, executable and manifest
identities, kernel, UAPI, and compatibility identity in a root-owned mode 0600
record. Passive `QUERY` reports `bootOwnership: current` only while every bound
field still matches and no route transaction is pending. A reboot, configuration
change, route disagreement, artifact replacement, or missing record fails
closed. Completed journals never substitute for current adoption.

The same `source-development` `QUERY` returns its authenticated runtime observations
under `state.safety`: `endpointOwned` confirms the root-owned mode 0600
character endpoint, `endpointOpen` reports whether a process currently holds
it, `liveOutput` reports the immutable module load gate, and `services` records
the bounded service observations. These fields are observations for the
consuming policy; they do not acquire the endpoint or authorize output.

This integration
accepts only passive `query`; every route mutation remains subject to the
packaged identity contract. Status authenticates systemd resolution, package
file preservation, the module binding, selected route, endpoint closure, and
the passive socket response. Rollback removes only the recorded integration
files and restores packaged unit resolution. None of these operations opens
the endpoint, reloads the module, changes the route, enables output, or creates
a qualification claim.

## Removal and rollback

Remove an enrollment using the exact command recorded in its JSON file. Unload
with `development-module unload`. The installer emits `ROLLBACK.json`; restore
only its recorded DKMS version and created source directory with:

```sh
sudo ./scripts/development-rollback --record /absolute/evidence/path/ROLLBACK.json
```

Removal unloads and removes the selected development module/version and source
tree; it does not restore a prior installation. Boot, overlay, service, and route
operations have separately scoped removal records because they may span a
reboot. No
command removes unrelated kernels, modules, overlays, services, repositories,
boot settings, or user files.
