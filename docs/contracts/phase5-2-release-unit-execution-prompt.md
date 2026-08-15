<!-- SPDX-License-Identifier: MIT -->

# Phase 5.2 release-unit execution prompt

## Authority and bounded outcome

Execute Phase 5A and the release-unit portion of Phase 5B from
`phase5-packaging-operator-enablement-execution-prompt.md`. Produce a complete,
deterministic, machine-verifiable release unit for one release-candidate
identity. This slice authorizes repository changes, offline generation, and
offline validation only. It does not authorize DKMS registration, installation,
module loading, overlay application, boot changes, key enrollment, target
access, GPIO, DMA, transmission, RF, tagging, release publication, issue
changes, or changes to WSPR-Transmitter or WsprryPi.

Phase 5.2 is complete when the source tree contains the release policy and
inputs, a clean committed tree can generate every distributable artifact twice
with identical bytes, and validation rejects any mismatch among the module
version, `dkms.conf`, module metadata, release metadata, Git tag expectation,
archive root/name, UAPI identity, overlay identity, and compatibility identity.

## Frozen identity and release inventory

Use release `0.0.0-phase5.2`, expected tag `v0.0.0-phase5.2`, package
`rp1-gpclk-dkms`, module `rp1_gpclk_dkms`, and UAPI ABI 1. The authoritative
inventory is `release/release-layout-v1.json`. It must enumerate every source,
generated artifact, installation destination, owner, group, mode, replacement
rule, and removal owner.

The distributable unit must contain:

- `rp1-gpclk-dkms-0.0.0-phase5.2.tar.gz`, containing the versioned source root,
  module sources and headers, Kbuild, Makefile, final `dkms.conf`, canonical
  UAPI, both overlay sources, schema, release inputs, lifecycle/diagnostic
  tools, operator documents, and security/behavioral release notes;
- reproducibly compiled GPIO4 and GPIO20 DTBOs;
- the compatibility-manifest schema and populated release manifest;
- a provenance manifest and SHA-256 checksum manifest; and
- machine-readable release metadata.

Generated metadata must bind the release version, source commit, expected tag,
UAPI ABI and header hash, both overlay source and DTBO hashes, source archive
hash, compatibility-manifest hash, and the identities of Python, `dtc`, C
preprocessor, tar format, and gzip implementation/options where those tools
affect bytes.

## Deterministic generation contract

`scripts/build_release.py` is the sole release-unit generator. It must:

1. require a clean tracked and untracked worktree and require `HEAD` to carry
   the exact expected tag for publishable output; a development override may
   admit dirty bytes or bypass the tag check only when every metadata artifact
   records the exact exception and is marked non-publishable;
2. obtain source inputs from Git's tracked file list, not a recursive filesystem
   walk, and reject symlinks, traversal, special files, secrets, private keys,
   generated output, and unexpected modes;
3. use the commit timestamp as `SOURCE_DATE_EPOCH`, sorted POSIX paths, uid/gid
   zero, empty owner/group names, normalized `0644`/`0755` modes, PAX tar, and
   gzip with an empty filename and fixed timestamp;
4. preprocess and compile each allowlisted overlay with explicitly recorded
   tools/options, normalize the DTBO timestamp inputs, and reject warnings;
5. emit metadata only after archive and DTBO bytes exist, avoiding cyclic hash
   claims; the compatibility manifest and provenance are signed-content
   sidecars and are not members of the source archive;
6. write into a new empty output directory, use temporary files plus atomic
   replacement, and remove partial output on failure; and
7. generate `SHA256SUMS` last, covering every distributable artifact except
   itself, in stable filename order.

`scripts/validate_release.py` must independently validate the release unit. It
must verify every checksum; JSON schema; metadata cross-reference; archive
name, root, members, order, modes, times, ownership, safety and required
contents; exact source bytes; UAPI ABI/hash; overlay source/DTBO hashes;
compatibility default-deny state; release notes identity; tooling identity; and
the complete installation inventory. Any missing, extra, renamed, or mismatched
release artifact fails.

## Installation policy

The inventory must freeze these destination classes without performing them:

- source inputs under `/usr/src/rp1-gpclk-dkms-VERSION/`;
- DKMS-built module under DKMS' kernel-specific `/lib/modules/KERNEL/updates/dkms/`;
- DTBOs under `/boot/firmware/overlays/`;
- canonical UAPI under `/usr/include/linux/` only for an explicit development
  install, never silently during DKMS registration;
- compatibility, release metadata, provenance, and checksums under
  `/usr/share/rp1-gpclk-dkms/VERSION/`;
- lifecycle and diagnostic tools under `/usr/libexec/rp1-gpclk-dkms/`; and
- operator documentation and release notes under
  `/usr/share/doc/rp1-gpclk-dkms/`.

All installed files are root-owned, directories are `0755`, ordinary files are
`0644`, executables are `0755`, and `/dev/rp1-gpclk` remains root:root `0600`.
Replacement is exact-version and checksum guarded. Removal may delete only a
path recorded as owned by this package and only when its current identity still
matches package state. Shared signing keys and certificates are never owned or
removed by this package.

## Compatibility and claim boundary

The release manifest is populated with the release identity but has no positive
runtime entries. Its default is `Unavailable`: Phase 4 evidence belongs to
module `0.0.0-phase4d-combined`, while this release has a different module and
archive identity. Phase 5.2 therefore makes no `Experimental` or `Qualified`
claim. Representative-header and output-disabled lifecycle work can later add
exact entries but cannot exceed `Compatible-unqualified`. There is no fallback
to `/dev/mem`, a custom kernel, or another physical backend.

## Validation and adversarial loop

Inspect every command before execution. Run SPDX, whitespace, UAPI, schema,
documentation/link, existing offline tests, release-unit negative tests, and
two independent release generations from the same committed/tagged bytes.
Compare all artifacts byte-for-byte. Record tools that are unavailable; do not
claim the affected gate passed.

Then conduct a separate adversarial review attempting to falsify completeness,
destination coverage, version/tag identity, archive determinism, dirty-tree
refusal, secret exclusion, symlink/path safety, overlay reproducibility,
checksum/provenance coverage, compatibility claim ceilings, diagnostics being
read-only, signing/key ownership, removal boundaries, and every authorization
non-goal. Write each objective finding into this prompt or the Phase 5.2 review,
correct it, invalidate affected evidence, rerun it, and repeat until no finding
remains.

Commit and push the cohesive Phase 5.2 implementation when all offline gates
pass. Do not create or push the release tag: the generator's development mode
is for pre-tag verification, while publishable generation is a later clean-tag
gate requiring explicit release publication authority.
