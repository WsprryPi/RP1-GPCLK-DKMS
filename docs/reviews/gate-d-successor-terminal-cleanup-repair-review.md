<!-- SPDX-License-Identifier: MIT -->

# Gate D successor terminal-cleanup repair independent review

Status: PASS for offline implementation and regression coverage. No successor
release was frozen and no target state changed.

The repair introduces attempt schema 2 as an explicit generator option while
preserving schema-1 generation. Schema 2 normalizes every row to exactly one
`remove-attempt-residue` operation after `restore-services` and immediately
before `audit-residue`. The interrupted-upgrade recipe no longer duplicates
its earlier row-specific cleanup when emitted as schema 2. The closed
dispatcher and existing bounded removal primitive remain authoritative.

Schema-2 residue audit uses `lstat` and accepts only `FileNotFoundError` as
proof of absence. Permission denial is converted to a hard validation error;
an existing file, directory, or link also fails. This closes the protected
parent false-negative that hid Phase 5.48 attempt-1 residue.

The regression generates and independently validates all 38 schema-2
documents, proves the exact cleanup ordering and uniqueness for every row,
executes a representative complete attempt through the stateful rooted
executor, and requires its staging directory absent before evidence sealing.
A fault-injected permission-denied probe fails closed. Separate schema-1
generation assertions and the unchanged Phase 5.48 deterministic control-set
test prove that the frozen authorized bytes were not regenerated.

The full offline suite initially exposed two historical representative-build
tests that compared frozen Phase 5.47 and Phase 5.48 manifest hashes to moving
workspace source. They now compare against bytes read from each manifest's
exact recorded source commit. This strengthens rather than relaxes the frozen
identity assertion and allows a legitimate successor executor to evolve.

Focused checks and the complete offline suite pass, including all historical
deterministic generators, 38-attempt rehearsal, documentation links,
shellcheck, compiled tests, sanitizers, SPDX, and whitespace validation.

This commit is not a release or authorization artifact. The next gate is a
new successor freeze and representative build that explicitly selects schema
2; new controls and authorization must follow before any further target
lifecycle attempt.

No wspr5, module, overlay, GPIO, clock, DMA, Si5351, SDR, antenna,
transmission, or RF activity occurred.
