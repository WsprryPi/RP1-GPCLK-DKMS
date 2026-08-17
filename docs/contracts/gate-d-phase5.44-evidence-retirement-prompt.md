<!-- SPDX-License-Identifier: MIT -->

# Phase 5.44 Phase 5.42 evidence-retirement prompt

Retire only the exact sealed Phase 5.42 attempt-1 evidence that blocks the
Phase 5.43 evidence path. Bind the operation to the committed retirement
document and `scripts/gate_d_residue.py` bytes. Before execution, independently
validate the document, tool tests, source directory type, two-file closure,
ownership, modes, file hashes, parsed failure identity, inactive runtime, and
absent destination.

Run the committed tool read-only on `wspr5` and require `status: ready`. Then
invoke the same bytes once as root with `--execute`. The only permitted
mutation is an atomic rename from
`/var/lib/rp1-gpclk-dkms/gate-d/current-supported-kernel/gd-current-supported-kernel-gpio4`
to
`/var/lib/rp1-gpclk-dkms/gate-d/history/phase5.42/gd-current-supported-kernel-gpio4`,
plus creation of missing destination parent directories. Preserve the exact
`transaction.json` and `SHA256SUMS` bytes, modes, owner, and group. Require the
source path absent, destination present, hashes unchanged, and runtime still
inactive after execution.

Stop on the first discrepancy. Do not recover or retry Phase 5.43, start any
lifecycle attempt, install or remove DKMS state, load or unload a module,
apply or remove an overlay, change services or boot state, operate GPIO,
enable a clock, submit DMA, operate the separate I2C Si5351 path, use an SDR,
connect an antenna, transmit, or produce RF. Record and independently assess
the exact result. This slice removes one authenticated path collision only; it
does not make the phase-independent attempt paths suitable for another retry.
