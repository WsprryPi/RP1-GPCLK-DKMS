<!-- SPDX-License-Identifier: MIT -->

# Phase 5.48 digest-bound output-disabled authorization decision prompt

The operator may authorize only the exact Phase 5.48 Gate D control set bound
by all of these identities:

- control-set commit: `833db92a5b3aadf30c3dd617bea734d0d7f5b20a`;
- preauthorization-attestation commit:
  `7423b5076563486123ca32d32406550f68b12d84`;
- frozen source: `ef96f246b66b25bb70536341b60a5f1e64708c65`;
- release archive SHA-256:
  `18418395eac577d8718c1e74f6601e005160d2768ea7634a35d00e4ddead9120`;
- canonical snapshot SHA-256:
  `9377d109235305f29e85134026cf9247e5d462b0bd2c8e05d9c0463162156e33`;
- preauthorization execution-instance SHA-256:
  `a477e0acc2d6e85d769791b4e6fa82e8a2ea6e9324718f1ac82cd21dd4811d8c`;
- pre-root envelope SHA-256:
  `342a4837f239033aeeccfd8b32a1972ba3189a2424e4b8d21f58ccf3c8630c88`;
- 38-attempt index SHA-256:
  `aa71bda96970d8e1c2faabf7121a8015cefa5148fde5cb89d809cfef1d37265f`;
- preauthorization attestation SHA-256:
  `b29dcbaabbbe986c0910ae731ee46b4327eacc502eb2cf5e774fe0ef6832906c`.

Authorization is limited to the 38 indexed attempts in the ten ready rows,
their namespace `phase5.48-ef96f246b66b`, the exact seven release artifacts,
the snapshot-derived 28-path Phase 5.47 predecessor inventory, the frozen
Phase 5.48 successor inventory, and the authenticated schema-5 pre-root,
ledger archival, recovery, service, stock-kernel, DKMS, overlay,
load-disabled, query, unbind/rebind, unload, bounded failure-injection, and
cleanup operations sealed in those controls. The five deferred environmental
rows remain excluded and are not substitutes.

The target baseline requires all six reviewed services inactive, the module
and endpoint absent, no route overlay, no test DKMS version, a
terminal-complete Phase 5.47 ledger, exact predecessor paths and kernel
identities, authenticated recovery, an unused SDR, no antenna, and the
disconnected and unused separate I2C Si5351 path. Any authorization requires a
byte-identical canonical recapture immediately before staging.

All four attempt-controlled services are snapshot-bound to the inactive
`preserve` action. Any missing, duplicate, changed, active, or inconsistent
service state/action record invalidates authorization.

If explicitly authorized, update only the execution-instance authorization
fields and dependent hash edges. Deterministically regenerate and
independently validate the complete controls, including final-envelope
validation with the complete exact archived Phase 5.48 Python and executor
tool graph. Commit and push the authorized bytes before target staging.
Authorization is invalid if any bound identity or baseline changes.

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
authorizes these exact committed bytes, keep `targetExecutionApproved: false`
and `executionReady: false`; do not stage inputs or begin execution.
