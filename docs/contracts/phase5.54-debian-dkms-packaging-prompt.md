<!-- SPDX-License-Identifier: MIT -->

# Phase 5.54 conventional Debian DKMS packaging prompt

## Objective

Replace the experimental Phase 5.53 product deployment mechanism with one
conventional, minimal Debian DKMS package while preserving the already frozen
Phase 5.53 product and qualification evidence as history.

## Verified starting context

- Phase 5.53 installed the product through a custom archive administrator and
  ledger.
- The actual product source closure is versioned under `/usr/src`; it does not
  own the global `/usr/include/linux/rp1_gpclk.h` path.
- Qualification tooling has already been repaired to compile its UAPI probe
  from the installed versioned product closure.
- The Phase 5.53 product layout describes more destinations than its product
  installer actually creates. It must not be patched into a new installer.

## Scope and requirements

1. Introduce `0.0.0-phase5.54` as a new product identity; do not regenerate or
   alter frozen Phase 5.53 archives or evidence.
2. Use Debian source packaging with `debhelper` and `dh-dkms`. Let `dpkg` own
   files and let generated DKMS maintainer scripts own add/build/install and
   removal behavior.
3. Package only the complete module build closure under
   `/usr/src/rp1-gpclk-dkms-0.0.0-phase5.54` and both compiled overlays under
   `/boot/firmware/overlays`.
4. Include both overlay sources and the canonical UAPI in the versioned source
   closure. Do not install a second global UAPI copy.
5. Install both GPIO4 and GPIO20 overlays as inactive files. Do not edit boot
   configuration, apply an overlay, or load the module.
6. Keep qualification controls, evidence, probes, ledgers, and orchestration
   out of the product package.
7. Treat the literal binary-package member inventory and Debian control
   archive as the installation contract. Do not introduce another custom
   layout executor or transaction framework.

## Validation and evidence

- Run repository packaging-contract and SPDX checks plus `git diff --check`.
- Build the binary package with the actual Debian Trixie
  `dpkg-buildpackage`/`dh-dkms` toolchain.
- Inspect every literal package member and generated maintainer script.
- In a disposable Debian-compatible environment, install the package, verify
  the exact versioned UAPI/source and both inactive DTBOs, upgrade to a second
  package revision with the same DKMS module version, then purge it and prove
  all package-owned source and overlay paths are absent.
- Build twice from the same committed source and require byte-identical `.deb`
  output before freezing an artifact hash.

## Safety and non-goals

Do not contact `wspr5`; stage or install on a target; run `sudo`; load, bind, or
unload a module; activate or remove an overlay; change boot configuration;
reboot; touch GPIO, clocks, or DMA; transmit; or produce RF. Do not package
qualification tooling or reconcile historical Phase 5.53 controls into the
new deployment path.

## Adversarial completion rule

Review the package from the perspective of a clean install, same-module
package upgrade, purge, missing headers, both route choices, qualification UAPI
lookup, and accidental target activation. Correct every actionable finding and
repeat the affected validation until clean.

## Exit criteria

Exit only when the package builds conventionally, its literal inventory is
minimal and complete, install/upgrade/purge passes in a disposable system, two
committed-source builds are byte-identical, documentation matches the package,
and no target or hardware boundary was crossed.
