<!-- SPDX-License-Identifier: MIT -->

# Phase 5.46 digest-bound output-disabled authorization decision prompt

The operator may authorize only the exact Phase 5.46 Gate D control set bound
by all of the following identities:

- control-set commit: `f1e5fa27bed175533f6a291152fa70700b88285b`;
- preauthorization-attestation commit:
  `334d7cc3b2a14dc00e48ffb45f169ad7c8390c86`;
- frozen source: `b43e2744b212f5bc53ad40584254f52310af4684`;
- release archive SHA-256:
  `0e0debdd96560602bd61457afc59782cfad2a4fb1b6f9b54e0d2505453e6c8f2`;
- canonical snapshot SHA-256:
  `bc4c307350d6e74c9cbb85ef890fbaf0e8ad969ecdeb661a98703b70bd4a1859`;
- preauthorization execution-instance SHA-256:
  `480f5cfece7b2de88f84ec60e1bdf7ee50af08bea46e17efc49234e45ffe21cc`;
- pre-root envelope SHA-256:
  `a7c815965d5b732f50bda6c7cf9b995c261532f611b3aa215745c0fbd44d7ecd`;
- 38-attempt index SHA-256:
  `e1858c68af8362a3c9ac969b5335317617e8e67491ddc916c3190c2eb6a8243d`;
- preauthorization attestation SHA-256:
  `bae6d6251d086ee309eab190be03048e15d28c05ae92106a229e6ca9df83452b`.

Authorization is limited to the 38 indexed attempts in the ten ready rows,
their namespace `phase5.46-b43e2744b212`, the exact seven release artifacts,
the snapshot-derived 28-path Phase 5.45 predecessor inventory, the frozen
Phase 5.46 successor inventory, and the authenticated schema-5 pre-root,
ledger archival, recovery, service, stock-kernel, DKMS, overlay,
load-disabled, query, unbind/rebind, unload, bounded failure-injection, and
cleanup operations sealed in those controls. The five deferred environmental
rows remain excluded and are not substitutes.

The target baseline requires all six reviewed services inactive, the module
and endpoint absent, no route overlay, no test DKMS version, a terminal-complete
Phase 5.45 ledger, exact predecessor paths and kernel identities,
authenticated recovery, an unused SDR, no antenna, and the disconnected and
unused separate I2C Si5351 path. Any authorization requires a byte-identical
canonical recapture immediately before staging.

If explicitly authorized, update only the execution-instance authorization
fields and dependent hash edges. Deterministically regenerate and independently
validate the complete controls, including final-envelope validation with all
eight exact archived Phase 5.46 Python modules. Commit and push the authorized
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
authorizes these exact committed bytes, keep `targetExecutionApproved: false`
and `executionReady: false`; do not stage inputs or begin execution.
