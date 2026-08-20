<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 final staging-transport successor prompt

## Objective

Before requesting target-staging authority, reconstruct the metadata-free
transport from the final product, qualification, envelope, and same-version
closures. Replace no historical transport artifact. Prove that every staged
path-bearing consumer is present and executable offline.

## Requirements

1. Build a new transport consumer for namespace `phase5.53-4e7a64a0ca35`.
2. Materialize all 63 envelope inputs from their explicit owners, extract all
   54 product and 33 qualification archive files, and add the separately sealed
   schema-7 envelope and same-version transition plan.
3. Emit deterministic metadata-free USTAR bytes with an exhaustive source map.
   Require exactly 151 regular files, regular files/directories only, fixed
   metadata, no PAX headers, and no unowned or hash-different input.
4. Generate the transport from both independent release directories and
   require byte-identical archives and source maps.
5. Extract the transport offline, validate every envelope input, execute the
   staged same-version driver in read-only validation mode, and execute the
   archived pre-root entrypoint in read-only validation mode.
6. Add the focused regression to the offline suite, perform adversarial review,
   commit, and push only attributable changes.

## Non-goals

Do not contact the target, transfer or extract files on it, remove or install
the product, invoke the same-version transition, perform a pre-root transition
or lifecycle attempt, or conduct module, overlay, boot, service, GPIO, clock,
DMA, transmission, or RF activity.

## Exit criteria

Both transport generations are byte-identical, both archived entrypoints pass
offline validation, every final path resolves from its declared closure, and
the next gate is an exact authorization-decision prompt covering validated
transfer and one recoverable same-version product-to-qualification transition
that stops before lifecycle attempt 1.
