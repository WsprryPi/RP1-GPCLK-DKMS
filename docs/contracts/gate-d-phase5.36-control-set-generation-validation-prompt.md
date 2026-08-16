<!-- SPDX-License-Identifier: MIT -->

# Phase 5.36 Gate D control-set generation and validation prompt

Generate a distinct hash-closed Gate D control set for frozen
`0.0.0-phase5.36` at `20f7a21ad8601f2e2fd4dec4640ea919acc22ce0`,
archive SHA-256
`a5d9fa6d83a4ea7405ede432be0bfcea201d850d21b3860fc40931f7e2fef271`,
and representative module SHA-256
`c11f89a63c4e2fbe09f6f0a401df348cbe5f4d713747f8c105a7731dc1007909`.
Preserve all Phase 5.35 controls, authorization, staging, failure, and review
evidence unchanged.

Create and mutually bind the route decision, target plan, schema-version-2
qualification identity, bootstrap, 38-attempt bundle/index, execution instance,
and schema-version-3 pre-root envelope. Bind all 18 successors from the frozen
archive and target-built helpers and all predecessors by path from the last
successful Phase 5.31 retained-tool graph.

The schema-version-3 envelope must bind the live canonical administrator ledger
at `/var/lib/rp1-gpclk-dkms/transaction.json`, SHA-256
`48946aff65cc88a765510e86891fc9b67de71fa9b651a8ba0198893a053d2afa`,
root ownership, mode `0600`, `status=recovered`,
`recoveryRequired=false`, and `liveOutput=false`. Bind the unique archive path
`/var/lib/rp1-gpclk-dkms/history/phase5.34-transaction-recovered.json` with
mode `0400` and require it to be absent.

Validate the ledger and all 18 predecessor tools read-only on wspr5. Verify
schema closure, exact import closure, deterministic generation, 38 unique fake
executions, 15 interruption attempts, four busy-removal attempts, copied-
executor validation/planning, and the authorization gate. Mutate ledger fields,
paths, identities, roles, hashes, transitions, authorization, and safety values
and require fail-closed results.

Keep `targetExecutionApproved=false` and `executionReady=false`; readiness-
required validation must fail. Do not stage inputs, move the live ledger,
administer DKMS, load/bind modules, activate overlays, change services or boot,
access GPIO/clocks/DMA, operate Si5351/SDR/transmitter equipment, reboot,
transmit, or produce RF. Run the full offline suite, independently review,
commit attributable files, and push.
