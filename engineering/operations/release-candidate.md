<!-- SPDX-License-Identifier: MIT -->

# Build, verify and publish 1.0.2

The product/source/module/DKMS version is `1.0.2`; Debian is `1.0.2-1`;
the canonical release tag is `v1.0.2`. Default candidate preparation creates no tag,
GitHub release, asset URL, immutable release or qualification claim.

## Release identity and maintenance

The current source identifies `v1.0.2` / Debian `1.0.2-1`.
The published immutable `v1.0.0` tag identifies source commit
`8c16d3c237cb1267cbedafb5da2bb74132ca5de0` and tree
`4c1ad8acf513b36ba32e58a636942655accbb52d`. Its tag and seven assets remain
unchanged. Reconstruct that release from its clean tagged checkout and retained
environment, using the scripts from that checkout and `--release`.

The patch provisions the route-manager group before neutral activation when
Debian package configuration has not created it. See the
[release notes](release-notes-1.0.2.md). Its module, package, runtime and route
compatibility versions move together. Canonical UAPI bytes, overlay sources,
kernel resource behavior and licensing are unchanged. Published `v1.0.1` and
its assets also remain unchanged. Version equality never substitutes for exact
source and asset hashes.

Every tracked file is included in the source archive. The route-manager contract
is also staged as `/usr/share/doc/rp1-gpclk-dkms/route-manager.md`, so its changes
affect the package. Never move an existing tag, overwrite an asset, edit generated
checksums or relabel evidence for a different source tree. The retained `1.0.0`
evidence is not patch qualification. Target builds, lifecycle acceptance and
WsprryPi consumer review remain separate gates. Direct in-place replacement of
`1.0.0-1` or `1.0.1-1` is refused; owning cleanup/removal precedes a clean patch installation.

## Commands and environment

Use Linux with Python 3, python3-jsonschema, Git, dpkg-dev, debhelper 13,
dh-dkms, device-tree-compiler (including fdtput), make, gzip, xz and zstd. The maintained
[container recipe](../../tools/release-builder.Containerfile) provisions these
tools without a target. Retain the built image by immutable image ID or save it
outside the checkout. Its pinned base alone does not pin later APT packages;
provenance records exact tool/package versions. Validation requires the same
tool environment and refuses drift. Container setup may access package mirrors;
candidate generation and validation need no network or root. Python is a pre-dependency because the
read-only pre-unpack guard runs before ordinary package dependencies configure.

From a clean checkout whose HEAD is the full reviewed commit:

```sh
./scripts/build-release-candidate --version 1.0.2 \
  --source-commit FULL_40_CHARACTER_SHA \
  --output /absolute/new/candidate

./scripts/validate-release-candidate \
  --candidate /absolute/new/candidate \
  --source-commit FULL_40_CHARACTER_SHA
```

Replace the commit placeholder with the actual reviewed commit. The builder
refuses abbreviated/mutable revisions, tracked or untracked changes (including
changes hidden by index flags), unsafe Git members, private key material,
version divergence, unresolved identity placeholders, existing output,
symlinked output or output inside the source checkout. There is no dirty-source
release override. Ignored files are never read as source inputs. The executable
uses isolated Python startup, ignores checkout bytecode caches, fixes Git/tool
environments and temporary roots, and disables bytecode writes.

The builder reconstructs only tracked Git blobs in fresh isolated directories,
builds the package twice, and compares every candidate asset byte. Before
publishing files to its new output directory it invokes the separate validator.
Failure removes only its own new output reservation. Neither command installs
a package, uses DKMS on the host, loads a module or operates hardware.

Determinism uses commit time as `SOURCE_DATE_EPOCH`, sorted USTAR source members,
root ownership, fixed 0644/0755 modes, a zero gzip header timestamp, locale C,
UTC, umask 0022, a fixed subprocess environment and single-thread gzip Debian
compression. Package source, control and data identities bind actual bytes.
No build path, current timestamp, login name or hostname is a release input.
The source archive preserves the reviewed DKMS template; the installed source
has its version and runtime-controller profile rendered explicitly.

## Exact asset set

| Asset | Meaning |
| --- | --- |
| `rp1-gpclk-dkms-1.0.2.tar.gz` | Exact tracked source of the identified commit/tree |
| `rp1-gpclk-dkms_1.0.2-1_all.deb` | One source-only DKMS Debian package |
| `rp1-gpclk-dkms-installation-manifest-v1.json` | WsprryPi consumer identity and complete package data inventory |
| `rp1-gpclk-compatibility-manifest.json` | Exact source/UAPI identity, default Unavailable, no target entries |
| `release-metadata.json` | Unpublished candidate classification, tool versions, module/controller/UAPI/overlay/runtime identities and provenance |
| `candidate-validation.json` | Machine-readable repeat-build result, bound to source and package |
| `SHA256SUMS` | Sorted lowercase SHA-256, two spaces, filename and LF for every other asset; no self-hash |

The installation manifest is deliberately release-shaped: `releaseChannel` is
`release` and `releaseTag` declares intended `v1.0.2`. These are the stable
consumer contract, not evidence of publication. Separate provenance says
`classification: candidate`, `published: false` and leaves actual tag, release
URL and GitHub asset digest null. WsprryPi additionally requires an actual
published immutable non-draft/non-prerelease release; a local candidate cannot
satisfy that selection gate. This preserves candidate bytes for later acceptance.

The closed [manifest schema](../../schema/rp1-gpclk-dkms-installation-manifest-v1.schema.json)
permits only the defined exact keys. Inventory records use relative destination,
file/directory type, mode and SHA-256; directory hashes cover empty bytes.
Provenance separately declares root uid/gid and inventories control members.
Source and package hashes are independent. Checksums establish integrity,
not authentication; the expected source commit and retained environment are
external trust anchors. No private signing key is generated or distributed.
Target signing and trust enrollment remain administrator-owned prerequisites.

Both `v1.0.2-rp1-gpio4` and `v1.0.2-rp1-gpio20` remain distinct. Both canonical
UAPIs retain their reviewed bytes. The runtime contracts are binding v3,
readiness v1 and update v1. The source package includes controller build inputs;
target DKMS produces both ELF modules. Installed compressed-file and decompressed
ELF hashes, vermagic, signatures and build notes remain null until actual target
builds produce them. Runtime-private overlays omit exported symbols through the
maintained controller generator; their bytes are bound during target bundle
construction. Firmware and runtime overlays have separate meanings.

## Independent verification and handoff

The validator trusts neither a builder cache nor its result declaration. It
checks the exact asset set, checksum bytes, JSON keys/schema, full Git
commit/tree and source archive, canonical archive paths/ownership/modes,
duplicate/shadowed Debian ar/tar members, package control identity, complete
inventories, passive maintainer-script constraints, every interface and
provenance identity, and absence of fabricated qualification. It reads a bounded nonsymlink asset snapshot and rechecks the original bytes
after validation. It independently reconstructs and rebuilds the package from Git and requires byte equality.
It writes no candidate or source files. Keep stdout results outside the checkout.

[The pinned consumer-contract fixture](../../release/wsprrypi-consumer-contract.json)
identifies the historical reviewed WsprryPi commit and installer digest for
`v1.0.0`; it does not assert `v1.0.2` consumer acceptance. It documents the
stable asset/key contract and application-owned acceptance follow-ups. It is a
compact format fixture, not WsprryPi implementation or acceptance evidence.
Refresh the read-only consumer comparison when selecting an acceptance candidate.

Hand the exact candidate directory, source commit/tree, checksum file and retained
build environment to [package lifecycle validation](package-lifecycle.md).
The historical `0.9.0` transition uses owning removal followed by clean installation;
direct replacement and in-place downgrade are refused.
Then use the supported exact-source/test path for current WsprryPi `devel`
acceptance of those same identities, including its update, rollback,
ownership and runtime contracts. Repair application-owned version fixtures and
any actual integration defects in the application repository under that scope.
Source or artifact changes invalidate the prior candidate identity and require
rebuilding/repeating affected checks. Freeze and publication follow acceptance;
the provider release must precede the dependent WsprryPi production release.

These commands establish source/package reproducibility and format integrity.
They do not establish real package lifecycle, target binding/cleanup, signing
trust, WsprryPi acceptance, product eligibility, transmission or RF qualification.

## Frozen publication profile

The publication procedure below defines the release workflow. The existing
`v1.0.0` publication is complete; its tag and assets must remain unchanged.
Publication of a new tag requires explicit authorization; rebuilding an existing
tag must reproduce its immutable assets without replacing them.

To prepare the patch publication profile, use the accepted clean source commit
and retained environment with `--release` on both commands above. Repeat into a second new
directory and compare every file. This profile retains identical source archive,
Debian package and installation-manifest bytes for the same commit/environment;
only provenance, compatibility manifest ID, validation classification and their
checksums change. No generated asset is edited by hand.

Release provenance uses `rp1-gpclk-release-provenance-v1`, classification
`release`, canonical `releaseTag` and tag-specific `releaseUrl`.
Its `published: true` describes the intended published artifact profile; local
building or validation does not verify GitHub publication. Command results
always return `published: false` because they perform no publication. The retained
`candidate-validation.json` filename records reproducibility of the frozen set
with classification `release`; it grants no qualification. The compatibility
manifest ID is `v1.0.2-FULL_SOURCE_COMMIT`, defaults to Unavailable and has no
target entries. Actual target module identities remain null until built.
`githubAssetDigest` remains null because provenance cannot embed its own final
digest; GitHub's independently queried per-asset digests and `SHA256SUMS` bind
the published files. Candidate and release profiles are never accepted
interchangeably by the validator.

Initial publication uses an annotated tag at the exact accepted source commit,
after exact-commit CI, reproducible builds and independent validation. The
`v1.0.2` tag must name the exact reviewed patch source, after coordinated
version/identity and consumer review. Candidate preparation does not create it.
Inspect existing tags/releases first; conflicting identities stop publication. Never move an existing tag or overwrite an asset.

Enable repository release immutability before publishing. With authenticated
`gh`, create a draft using `--verify-tag`, reviewed release notes and every
validated asset. Download the draft and compare the complete set against the
frozen directory before `gh release edit v1.0.2 --draft=false --verify-tag`.
Published releases must be immutable, non-draft and non-prerelease. Independently
query the peeled remote tag and release, download all seven assets into a new
external directory, recompute every SHA-256 and compare every byte. Retain the
build image by immutable ID for reconstruction. If interrupted, inspect and
finish the existing draft; never replace an immutable publication.

Provider publication precedes application release. WsprryPi separately owns
acceptance of each selected published provider identity and migration to it.
Provider publication does not perform that migration or extend conducted
acceptance into calibrated or general RF qualification.

## Authenticated source enumeration

Each builder, independent validator, and predecessor renderer enumerates its
exact full commit independently. Source reads use fresh `git cat-file --batch`
processes with replacement objects disabled and the fixed Git environment.
Every reply must match the requested blob ID, type, declared length, delimiter,
and independently recomputed Git object hash. Missing, extra, or reordered
responses fail. Repeated requested IDs at different paths are valid and retain
separate path/mode entries. Unsafe paths/modes, private-key contents, and signing
material suffixes remain refused.

Enumeration accepts at most 16,384 regular source members, 64 MiB per member,
and 256 MiB total source bytes. Standard output and error have separate byte
budgets. Git control calls and the batch use 120-second guards; output progress
does not renew the batch deadline. EOF must be followed by successful process
exit. Timeout, cancellation, or failure kills and reaps the owned Git process
group; unresolved cleanup fails the operation.

These source-map reads do not reuse a builder cache as validator evidence.
Independent clean package rebuilds, poisoned-cache/environment rejection,
classification checks, and final candidate snapshot/drift validation remain
required. The candidate in its final output directory must still pass the
independent validator before consumption.
