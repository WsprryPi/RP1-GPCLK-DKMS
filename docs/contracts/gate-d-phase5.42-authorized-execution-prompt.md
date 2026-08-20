<!-- SPDX-License-Identifier: MIT -->

# Phase 5.42 authorized output-disabled execution prompt

Bind the operator's explicit authorization to the exact Phase 5.42 control set
at commit `71a9c3a6a27967d6c30398af9f9b01ef087738d7`, frozen source commit
`5dc05b6e10cdb50c4f937b484fc92cf4469e54ab`, pre-authorization
attestation commit `1af17f1d091f55e3cdf9a220b4fec16ea68fe1d1`, canonical snapshot
SHA-256 `d228a5fe8eaa52a2fa44d003947d51b2a3a6798e4535c0570c3836ab5b283b9a`,
pre-authorization execution-instance SHA-256
`8f2c5bf201573e033508e456a8fe1a04984f9e27b7ae64a785268022e3aaeb75`,
and attempt-index SHA-256
`a4e333c7dda53d03db0b9ad90109f13f93d205f08df0965f33b752f07708dd5d`.

Authorization is limited to the 38 indexed attempts in the ten ready rows,
the exact seven-artifact representative-build inventory, the complete typed
28-path Phase 5.39 predecessor and Phase 5.42 successor inventories, and their
authenticated schema-5 pre-root, current-ledger archival, recovery, service,
stock-kernel, DKMS, overlay, load-disabled, query, unbind/rebind, unload,
failure-injection, and cleanup operations. Five environmental rows remain
deferred and are not authorized substitutes.

Recompute the authorized execution-instance hash and all dependent hash edges
in the schema-5 pre-root envelope. Deterministically regenerate the complete
control set, repeat focused and complete independent validation, and commit
and push the authorized bytes before target staging.

On `wspr5`, require the byte-identical canonical snapshot, exact Phase 5.39
predecessor inventory and terminal `complete` administrator ledger, inactive
baseline, authenticated terminal recovery, exact release inputs, stock kernel,
headers, configuration, compiler, non-enforcing signing identity, disconnected
and unused separate I2C Si5351 path, unused SDR, no antenna, and available
sealed recovery. Stop if the pre-staging state no longer matches.

Execute only through the authenticated schema-5 pre-root transition and
installed permanent tools. The pre-root transition must archive only the exact
snapshot-bound current administrator ledger before invoking the successor
administrator. Stop on the first identity, path, type, size, link-target,
ownership, mode, state, timeout, service, recovery, residue, cleanup,
transition-membership, or safety discrepancy. Use only recovery authorized by
authenticated journals. Terminal pre-root recovery must return without
beginning another attempt.

Output remains disabled. Prohibited operations include active pinctrl, clock
enablement, DMA submission, GPIO output, Si5351 operation, transmitter keying,
SDR operation, antenna connection, RF, `/dev/mem`, custom-kernel
qualification, forced removal, general upgrade, and unreviewed persistent boot
mutation. Preserve complete evidence and independently assess the result.

This authorization-recording step does not itself stage target inputs or begin
execution. Target staging and execution may start only after these authorized
bytes are committed, pushed, synchronized, and revalidated.
