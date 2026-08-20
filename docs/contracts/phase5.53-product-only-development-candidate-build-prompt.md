<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 product-only development-candidate build prompt

## Objective

Build a new deterministic Phase 5.53 development release from the exact clean
source containing product-only `--allow-development` installation and
install-both-inactive-overlays behavior. This candidate replaces the earlier
Phase 5.53 product bytes for future target installation.

## Requirements

1. Require a clean, synchronized source commit and run the release builder
   twice into new empty directories with `--development`.
2. Require byte-identical product archives, sidecars, and DTBOs across both
   builds, and validate each complete release directory.
3. Extract the product archive and prove it contains the exact current
   administrator, installation model, lifecycle documentation, module source,
   DKMS configuration, and both overlay sources, but no qualification tools.
4. Exercise product-only installation offline with the qualification archive
   absent, proving both inactive DTBOs are installed and Gate D tooling is not.
5. Record exact source and artifact identities plus a separate adversarial
   review. Do not construct a Gate D control set or treat the qualification
   archive as a deployment input.

## Constraints

This is an offline development-candidate build. Do not tag, publish, contact a
target, transfer files, install DKMS, apply overlays, load a module, change
GPIO/clock/DMA state, transmit, or perform RF activity.

## Exit criteria

Two byte-identical validated builds and an extracted product-only installation
test must pass. The next gated action is a separately authorized product-only
target installation, not qualification-root staging.
