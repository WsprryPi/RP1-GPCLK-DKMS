<!-- SPDX-License-Identifier: MIT -->

# Release 1.0.0 final artifact reproduction prompt

## Objective

Build the final Debian product package and separate qualification archive twice
from one clean committed `1.0.0` source identity, prove byte-identical outputs
and literal inventories, and prepare—but do not execute—the exact-candidate
target verification.

## Requirements

1. Preserve the conventional Debian product boundary. The product contains
   only the complete DKMS build closure, canonical UAPI, package documentation,
   and both inactive overlays. It contains no qualification controls or
   evidence.
2. Create a minimal qualification archive containing release identity,
   package-member inventory, deny-by-default compatibility metadata, exact
   target-verification plan, validator/renderer, probe source, applicable
   schemas, release notes, and qualification documentation. It must not be
   installed by ordinary package installation.
3. Validate every package member and every qualification-archive member before
   target contact. Reject links, devices, unknown roots, duplicate members,
   unexpected modes, missing UAPI/overlay/source closure, or qualification
   files in the product.
4. Bind version `1.0.0`, Debian version `1.0.0-1`, expected tag `v1.0.0`, exact
   clean source commit, product SHA-256, qualification content identity, UAPI
   hash, both overlay identities, and inventory hashes.
5. Build independently twice with the same pinned Debian Trixie toolchain and
   require byte equality for the product package, qualification archive,
   metadata, inventories, compatibility manifest, and checksums.
6. Prepare one target plan that begins from the recorded inactive Phase 5.54
   package, installs the exact `1.0.0-1` package inactive, repeats separate
   GPIO4 and GPIO20 `live_output=0` lifecycles, performs one complete removal
   and reinstall, and restores the inactive final baseline. The plan is not an
   authorization and must not be executed in this slice.

## Authority boundary

This prompt is offline and repository-only. Do not contact `wspr5`, install or
remove a package on a target, load a module, apply an overlay, change boot
state, reboot, touch GPIO/clocks/DMA, transmit, produce RF, create or push a Git
tag, publish a release, or modify a consumer repository.

## Exit

Advance `final-artifact-reproduction` only after both clean exact-commit builds
are byte-identical and independently validated. Stop with
`final-candidate-target-verification` as the next separately authorized gate.
