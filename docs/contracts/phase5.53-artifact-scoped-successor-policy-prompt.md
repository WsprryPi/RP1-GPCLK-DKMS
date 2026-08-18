<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 artifact-scoped successor policy prompt

Define the minimal invalidation and carry-forward contract required to repair
the frozen Phase 5.53 qualification archive without rebuilding or requalifying
unchanged DKMS product bytes.

Treat product and qualification archives as separate identity domains. A
qualification-only successor may supersede the unpublished qualification
candidate while retaining the exact product archive, UAPI, DTBOs, module
build, ordinary-install evidence, and product-facing offline evidence when a
machine-checked input-closure comparison proves those bytes unchanged.

Require a distinct qualification source commit, deterministic qualification
archive reproduction, updated qualification provenance/checksums, focused
tests for every changed qualification input and its consumers, one complete
offline regression pass, and renewed control-set construction. Do not require
another product archive build, `offline-checks-twice`, or representative module
build solely because qualification-only bytes changed. Any product-input,
UAPI, overlay, module, installation, administrator, lifecycle, or shared-
identity change must fail this exception closed and restore the normal affected
product gates.

This slice defines and validates policy only. Do not repair the pre-root tool,
generate replacement archives or controls, change gate status, connect to a
target, stage inputs, request authorization, administer DKMS/modules/overlays,
or perform GPIO, clock, DMA, transmission, or RF work.
