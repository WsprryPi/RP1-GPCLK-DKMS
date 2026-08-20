<!-- SPDX-License-Identifier: MIT -->

# Phase 5.45 digest-bound output-disabled authorization decision prompt

The operator may authorize only the exact Phase 5.45 Gate D control set bound
by all of the following identities:

- control-set commit: `53e55780d6e1aec4551836e9c499de501a83a602`;
- preauthorization-attestation commit:
  `59c83bd57de5eb69c1982c4c24bc868564f5f7d7`;
- frozen source: `4b50db7868b7fe5ca9d830f51cd404c250192188`;
- release archive SHA-256:
  `21d05675e9d12ddb4c051868578c410737b733786357cee20eb2b0ce03f63356`;
- canonical snapshot SHA-256:
  `66208586a112792e91185a7ce67d5952427dc218fb8a392ac1bfb221ed51e4c8`;
- preauthorization execution-instance SHA-256:
  `8418fd031ac14e40c69c19b2d192783f2acf092351406b6455b3c96ede1f03ba`;
- pre-root envelope SHA-256:
  `39708b026f38da5edc83932a740d246233d26e4f87fccfc73a540e13542bef90`;
- 38-attempt index SHA-256:
  `3375c809dd699949f991742716628016a680bcf7253fc30ba8f3de52c294f020`;
- preauthorization attestation SHA-256:
  `ad9f538416fa34465c9fa0d0548719e5df1d4ac5947046fb0abc71298facae61`.

Authorization is limited to the 38 indexed attempts in the ten ready rows,
their candidate-derived namespace `phase5.45-4b50db7868b7`, the exact seven
release artifacts, the snapshot-derived 28-path Phase 5.43 predecessor
inventory, the frozen Phase 5.45 successor inventory, and the authenticated
schema-5 pre-root, ledger archival, recovery, service, stock-kernel, DKMS,
overlay, load-disabled, query, unbind/rebind, unload, bounded failure-injection,
and cleanup operations already sealed in those controls. The five deferred
environmental rows remain excluded and are not substitutes.

The operator-established target baseline keeps `wsprrypi.service`,
`sdrplay.service`, and `soapyremote-server.service` stopped and disabled. Any
authorization must require a byte-identical canonical recapture immediately
before staging, the exact inactive runtime and six inactive services, terminal
complete Phase 5.43 ledger, exact predecessor paths, stock kernel/header/config
and signing identities, authenticated recovery, disconnected and unused
separate I2C Si5351 path, unused SDR, no antenna, and available recovery.

If explicitly authorized, update only the execution-instance authorization
fields and dependent hash edges. Deterministically regenerate and independently
validate the complete controls, including final-envelope validation with the
exact archived Phase 5.45 pre-root bytes. Commit and push the authorized bytes
before any target staging. Authorization is invalid if any bound identity or
baseline changes.

Execution must use only the authenticated pre-root transition and installed
permanent tools. Stop on the first identity, state, timeout, service, recovery,
residue, cleanup, transition, or safety discrepancy. Use only journal-authorized
recovery. Terminal pre-root recovery must return without starting an attempt.

Output remains disabled. Prohibited operations include active pinctrl, clock
enablement, DMA submission, GPIO output, Si5351 operation, transmitter keying,
SDR operation, antenna connection, RF, `/dev/mem`, custom-kernel qualification,
forced removal, general upgrade, and unreviewed persistent boot mutation.

This prompt does not itself record authorization. Until the operator explicitly
authorizes these exact committed bytes, keep `targetExecutionApproved: false`
and `executionReady: false`; do not stage target inputs or begin execution.
