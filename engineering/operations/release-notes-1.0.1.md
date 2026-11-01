<!-- SPDX-License-Identifier: MIT -->

# RP1-GPCLK-DKMS 1.0.1

Version `1.0.1` / Debian `1.0.1-1` is an unpublished patch candidate based on
the maintenance changes since `v1.0.0`. Preparation, reproducible package
generation and independent validation do not establish publication or target
acceptance. The immutable `v1.0.0` tag and assets remain unchanged.

## Changes

- Add the operator handbook, documentation builds and regression checks,
  including setup, route management, status, maintenance and recovery guidance.
- Separate durable engineering contracts from operator documentation and keep
  the installed route-manager reference self-contained.
- Correct the legacy C tone and fault clients to plan dividers from the existing
  nominal 200 MHz parent. Reject a nonnominal live sweep parent; source
  calibration uses the PPM option.
- Extend hardware-free clock planning, DMA pacing, metadata consistency,
  documentation and release-identity regression coverage.
- Retain independently bound `v1.0.0` scoped qualification metadata and its local
  bundle tools; remove obsolete qualification harness scripts and schemas.
- Give the patch distinct product, module, controller, DKMS, package, runtime
  and GPIO4/GPIO20 compatibility identities. Both canonical UAPI byte identities,
  overlay sources and resource behavior remain unchanged.

## Installation and acceptance boundaries

The package contains source for the consumer and runtime controller, canonical
UAPIs and inactive route assets. Installation does not select a route, load a
module, edit boot configuration or authorize output. Stock Raspberry Pi kernels
and the existing DKMS/signing requirements remain applicable.

Direct `1.0.0-1` to `1.0.1-1` replacement and in-place downgrade are refused.
The owning workflow must quiesce and remove the installed provider before a clean
installation. Preserve exact rollback inputs. See the
[package lifecycle contract](package-lifecycle.md).

WsprryPi must explicitly accept and select the new tagged provider; this
candidate does not change its pinned provider or evidence. The retained
`v1.0.0` qualification bundle applies only to its exact software and scope.
It does not qualify `v1.0.1`. Target module builds, package lifecycle, consumer
acceptance and any scoped evidence reuse require separate validation.

The candidate compatibility manifest defaults to `Unavailable` with no target
entries. Build reproducibility establishes source/package integrity, not target
operation, timing, GPIO, transmission, RF or product qualification. Licensing
and repository ownership boundaries are unchanged.

Use the [release procedure](release-candidate.md) to build and independently
validate the seven assets from the exact clean source commit. Tagging and
publication require separate authorization after applicable acceptance.
