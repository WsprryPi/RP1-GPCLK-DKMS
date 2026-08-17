<!-- SPDX-License-Identifier: MIT -->

# Phase 5.48 Gate D control-set construction and validation prompt

Construct and independently validate the complete output-disabled Phase 5.48
Gate D control set for frozen source commit
`ef96f246b66b25bb70536341b60a5f1e64708c65`, release archive SHA-256
`18418395eac577d8718c1e74f6601e005160d2768ea7634a35d00e4ddead9120`,
representative module SHA-256
`3ee865f9293b69f45f5c17a9217896a2d68c2addd7c494088b430aecb3faf615`,
canonical snapshot SHA-256
`9377d109235305f29e85134026cf9247e5d462b0bd2c8e05d9c0463162156e33`,
and namespace `phase5.48-ef96f246b66b`.

Bind every attempt's service contract to the canonical snapshot: an inactive
service must use `preserve`; an active service must use
`stop-then-restore-exact`. Independently reject missing, duplicate, stale, or
inconsistent service state/action records.

Generate deterministically the schema-5 route decision, target plan,
qualification bootstrap, execution instance, pre-root envelope, qualification
identity, predecessor inventory, attempt index, and all 38 attempts. Retain ten
ready and five deferred environmental rows. Require every attempt-owned path to
be unique below the Phase 5.48 namespace and disjoint from all historical
Phase 5.42, 5.43, 5.45, 5.46, and 5.47 paths.

Authenticate the complete qualification-root graph: controls, attempt files,
matrix policy, executors, and Python modules. Reconstruct a sealed root only
from declared transitions and validate it. Extract the complete executable and
Python graph from the exact frozen Phase 5.48 archive and require byte equality
with the final plan, envelope, index, and transitions.

Generate twice in isolated output trees and require byte equality. Run focused
validators and the complete archive-bound offline suite. Correct every finding
and repeat affected validation. Offline construction may be approved, but
`targetExecutionApproved` and `executionReady` must remain false.

Do not connect to wspr5, stage target inputs, request or bind target execution
authorization, change services, administer DKMS or a module, apply overlays,
change boot state, access GPIO or I2C, operate Si5351 or SDR hardware, enable
clocks, submit DMA, connect an antenna, transmit, or produce RF. Commit and push
only deterministic controls, validators, prompt, and review.
