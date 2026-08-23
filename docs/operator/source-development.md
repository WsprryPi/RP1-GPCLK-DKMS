<!-- SPDX-License-Identifier: MIT -->

# Exact-source development lifecycle

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

```sh
git checkout EXACT_COMMIT

./scripts/development-preflight --kernel "$(uname -r)"

sudo ./scripts/development-install \
  --kernel "$(uname -r)" \
  --module-version VERSION \
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
development instance is removed and replaced automatically; it is not retained
as a predecessor.
A rendered development tree deliberately replaces the production DKMS kernel
name filter with `.*`. The requested kernel only needs a usable header tree;
DKMS/compiler errors are returned directly. The release/package source retains
its stock Raspberry Pi kernel filter unchanged.
A non-running kernel may be built and installed but cannot be reported loaded.

## Separate operations

```sh
./scripts/render-development-tree --source . --output /absolute/tree --module-version VERSION

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

Overlay installation and route application report affected files, identities,
ownership, removal evidence, and whether reboot is required.
They never reboot automatically. GPIO4 and GPIO20 remain independent; a
manifest or active identity for one never substitutes for the other. After an
approved reboot, run the read-only status and route verification commands.

The status state progresses through `development-built`,
`development-installed`, `development-loaded`, `development-endpoint-ready`,
and `development-live-enabled`. `release-qualified` is deliberately separate
and is never produced by this workflow.

## Removal and rollback

Remove an enrollment using the exact command recorded in its JSON file. Unload
with `development-module unload`. The installer emits `ROLLBACK.json`; restore
only its recorded DKMS version and created source directory with:

```sh
sudo ./scripts/development-rollback --record /absolute/evidence/path/ROLLBACK.json
```

Removal unloads and removes the selected development module/version and source
tree; it does not restore a predecessor. Boot, overlay, service, and route
operations have separately scoped removal records because they may span a
reboot. No
command removes unrelated kernels, modules, overlays, services, repositories,
boot settings, or user files.
