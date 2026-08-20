<!-- SPDX-License-Identifier: MIT -->

# Phase 5.51 canonical snapshot and Gate D control-set prompt

Before constructing controls, capture wspr5 twice with the reviewed read-only
canonical snapshot tool streamed directly into privileged Python. Bind the
existing physical declarations: the separate I2C Si5351 path is disconnected
and unused, the SDR is unused, and no antenna is connected. Require byte-equal
captures, stock kernel and headers, six inactive services, inactive module,
endpoint, overlay, DKMS test versions and live output, terminal Phase 5.50
administrator state, and the sealed Phase 5.48 terminal lifecycle journal.
Explain every difference from the Phase 5.50 predecessor snapshot.

Construct the complete output-disabled Phase 5.51 control set from frozen
source `cc87e0cdec7195eb69de2a6606f388e23ee0799c`, archive SHA-256
`253bd54054eb0b673f9e61c58a46b6b7ca2cf78d756fe4e80656f4ac1233f549`,
representative module SHA-256
`5fcfcc41e44a3685b7051b7ea8fbcce67f0fa79fefb29b8e203a231d7295d192`,
and the new canonical snapshot.

Generate exactly 38 schema-2 attempts under
`phase5.51-cc87e0cdec71`, ten ready matrix rows, five deferred environmental
rows, and the complete schema, route, bootstrap, plan, execution-instance,
pre-root, package-transition, service, recovery, and sealed-root graph. Use
execution-instance schema 6 with `attemptSchemaVersion=2`. Require
`inputsReady=true` but keep `approved`, `targetExecutionApproved`, and
`executionReady` false.

Generate twice in independent temporary roots and require byte equality for
every path. Reject missing, extra, duplicate, stale-phase, schema-1 attempt,
unnamespaced runtime, moving-worktree, or authorization-bearing content.
Reconstruct the final qualification root and validate the execution instance
and all 38 attempts using their exact frozen source and archived dependency
bytes. Independently validate all hashes, release inputs, predecessor and
successor package inventories, service pre-states, route/build/snapshot
identities, qualification-root marker, transition destinations, Python module
graph, attempt index, ready/deferred rows, and false authorization/readiness.

This slice permits only read-only snapshot capture and offline control
construction. Do not stage target inputs, perform a pre-root transition,
request or consume authorization, administer DKMS or a module, change overlays,
services, or boot state, access GPIO or I2C, operate Si5351 or SDR hardware,
enable clocks, submit DMA, connect an antenna, transmit, or produce RF. Commit
and push only after deterministic generation, independent validation, complete
offline checks, whitespace review, and staged-diff review pass.
