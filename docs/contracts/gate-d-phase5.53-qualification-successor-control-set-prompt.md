<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 qualification-successor control-set prompt

## Objective

Construct and independently validate the complete output-disabled Phase 5.53
Gate D control set using the retained product candidate and the repaired,
qualification-only successor. Do not repeat product freezing, paired product
offline suites, representative module compilation, or target snapshot capture.

## Exact retained and renewed inputs

- product source: `1884c0f1c53c661495576bf10ce08d8bf7a90bc3`;
- product archive SHA-256:
  `ae6df3a66a9a26a6fb8474e5896c9053b9f69580d8c45383a5556fc397ebb549`;
- qualification source: `834d05c5c5da0c383c4a229eaeff9dae07a4359b`;
- qualification archive SHA-256:
  `d931912d6ccc381b10a2a13d7f3a9122b0f748490ec8eefe0f86a28cb352c8d0`;
- canonical read-only snapshot SHA-256:
  `df8e80bc4b3382d9213d52cbc273b398e85124a2d2f58169c3a6f6aa339dbcf7`;
- retained representative-build manifest SHA-256:
  `0f80c2a7f9920ca9d6b7d8f471adf9e4edd89f2aff477f93f97313d437281abb`.

## Required construction

1. Generate a unique Phase 5.53 namespace and the complete 38-attempt,
   schema-2 attempt bundle, ten ready matrix rows, five deferred environmental
   rows, route decision, target plan, qualification bootstrap, execution
   instance, qualification identity, predecessor inventory, and schema-6
   pre-root envelope.
2. Bind product identity fields to the product source and product archive.
   Bind qualification-root executable and schema bytes to the qualification
   source and qualification archive. Never collapse the two source identities.
3. Require exactly eight pre-root release inputs in one release directory:
   product archive, qualification archive, GPIO4 DTBO, GPIO20 DTBO,
   compatibility manifest, provenance, release metadata, and checksums.
   Validate each exact successor sidecar hash and exact `SHA256SUMS` coverage.
4. Reconstruct the sealed qualification root from only the frozen product and
   qualification inputs. Require the repaired schema-6 pre-root validator and
   JSON Schema to accept the complete graph. Retain historical validator tests.
5. Set `authorization.approved=false`, `targetExecutionApproved=false`, and
   `executionReady=false`. This construction creates no execution authority.
6. Generate twice in independent temporary roots and require byte-identical
   output. Independently validate both generations, all hashes, paths,
   inventories, attempt counts, namespaces, safety fields, and claim ceilings.

## Constraints and non-goals

This is offline construction only. Do not connect to or recapture `wspr5`,
stage target inputs, run a pre-root transition, request or consume operator
authorization, install or administer DKMS/modules/overlays, alter services or
boot state, access GPIO/I2C, enable clocks, submit DMA, use Si5351 or SDR
hardware, connect an antenna, transmit, or produce RF. Do not modify the frozen
product or qualification archives or their byte-input closures.

## Validation and exit criteria

Run focused deterministic and adversarial validators, the complete offline
regression suite, documentation links, whitespace checks, and machine-checked
product and qualification closure comparisons. Reinject every actionable
failure and repeat affected checks. Exit only with byte-identical controls,
all execution flags false, the lifecycle matrix still blocked pending explicit
authorization, and no claim beyond offline-valid control-set construction.
