<!-- SPDX-License-Identifier: MIT -->

# Phase 5.50 digest-bound output-disabled authorization decision prompt

The operator may authorize only the exact Phase 5.50 Gate D control set bound
by all of these identities:

- control-set commit: `8e908928642bf3a4052f13cfb087c77a9bcbc7f8`;
- preauthorization-attestation commit:
  `dbc983e275ca6250c93d67d6dc3639f32ad3dff1`;
- frozen source: `c24160517b10900bf61243d4988f38247eeed58e`;
- release archive SHA-256:
  `ef989bf79faa5c30ddaf8ac5651d75b1755ba2fa385680692183e6145b2927c2`;
- canonical snapshot SHA-256:
  `3db85e0ada2427c997cdca878d0f2d53fc0c61d5aab68761e65a2a6cf349a6d5`;
- preauthorization execution-instance SHA-256:
  `620932f550ee70273d7f57b12a6406bfbb50722356d4ccf6542493120ad80fe0`;
- pre-root envelope SHA-256:
  `ea907b44043421a483009f1c9998be2e71732a54a32eabf398231e29af1e8226`;
- 38-attempt index SHA-256:
  `44c7bdb65e71970f1f15ef2c9d36bb6b1172ddb33350e19c0a2e3874ea3dc66f`;
- preauthorization attestation SHA-256:
  `01e66715dd410067b18263f617c068527d7cf2736ad827dce1161be49a9b7ed3`.

Authorization is limited to the 38 indexed schema-2 attempts in the ten ready
rows, their namespace `phase5.50-c24160517b10`, the exact seven release
artifacts, the snapshot-derived 28-path Phase 5.48 predecessor inventory, the
frozen Phase 5.50 successor inventory, and the authenticated schema-5 pre-root,
ledger archival, recovery, service, stock-kernel, DKMS, overlay,
load-disabled, query, unbind/rebind, unload, bounded failure-injection, and
cleanup operations sealed in those controls. The five deferred environmental
rows remain excluded and are not substitutes.

The target baseline requires all six reviewed services inactive, the module
and endpoint absent, no route overlay, no test DKMS version, a terminal-complete
Phase 5.48 ledger, exact predecessor paths and kernel identities, authenticated
recovery, an unused SDR, no antenna, and the disconnected and unused separate
I2C Si5351 path. Any authorization requires a byte-identical canonical
recapture immediately before staging.

All four attempt-controlled services are snapshot-bound to the inactive
`preserve` action. Any missing, duplicate, changed, active, or inconsistent
service state/action record invalidates authorization.

If explicitly authorized, update only the execution-instance `approved`,
`targetExecutionApproved`, approval-scope, and dependent hash edges.
Deterministically regenerate and independently validate the complete controls,
including final-envelope validation with the complete exact archived Phase
5.50 Python, schema, and executor tool graph. Commit and push the authorized
bytes before target staging. Authorization is invalid if any bound identity or
baseline changes.

Execution must use only the authenticated pre-root transition, sealed-root
policy and module graph, and installed permanent tools. Stop on the first
identity, state, timeout, service, recovery, residue, cleanup, transition, or
safety discrepancy. Use only journal-authorized recovery. Terminal pre-root
recovery must return without starting an attempt.

Output remains disabled. Active pinctrl, clock enablement, DMA submission,
GPIO output, Si5351 operation, transmitter keying, SDR operation, antenna
connection, RF, `/dev/mem`, custom-kernel qualification, forced removal,
general upgrade, and unreviewed persistent boot mutation are prohibited.

This prompt does not itself record authorization. Until the operator explicitly
authorizes these exact committed bytes, keep `approved: false`,
`targetExecutionApproved: false`, and `executionReady: false`; do not stage
inputs or begin execution.
