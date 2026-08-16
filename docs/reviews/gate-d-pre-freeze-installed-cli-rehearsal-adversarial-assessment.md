<!-- SPDX-License-Identifier: MIT -->

# Gate D pre-freeze installed-CLI rehearsal adversarial assessment

Status: clean after correction

The rehearsal copies the same eight Python sources and executable installed by
the release layout into an isolated libexec tree. Each subprocess therefore
uses the copied executor and resolves its local imports from that installed
tree rather than importing the repository executor directly. It covers all 38
index entries and compares each document byte hash with the index before use.

The initial implementation covered every index entry but did not independently
assert its recorded SHA-256. That made the phrase "hash-indexed" stronger than
the evidence. The assertion was added and the affected checks repeated.

For every exact document, validation and fixed-plan generation must succeed.
The execute CLI is then invoked without root execution flags and must stop at
the explicit pre-mutation authorization gate without a traceback. An AST check
also rejects imports inside `main()` that shadow a module-level imported name,
covering the lexical defect that escaped Phase 5.31.

This is not authenticated qualification-root execution: deliberately, no
synthetic test option weakens the production root or identity boundary. That
boundary remains covered by the exact installed-import-graph test, while the
stateful fake-system test executes all 38 attempt workflows. The three gates
together cover packaging/import identity, real CLI control flow, and lifecycle
state behavior without claiming target equivalence.

The rehearsal is temporary, offline, unprivileged, network-free, and performs
no system or hardware action. It does not install or load a module, activate an
overlay, alter services or boot state, access GPIO, enable clocks, submit DMA,
operate Si5351, use a transmitter or SDR, reboot, transmit, or produce RF.
