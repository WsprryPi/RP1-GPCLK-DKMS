<!-- SPDX-License-Identifier: MIT -->

# Phase 5.33 retained-tool and recovery successor execution prompt

## Objective

Create and independently validate the smallest offline successor that closes
the two Phase 5.32 pre-root blockers without advancing into candidate freeze,
target staging, installation, module lifecycle, GPIO, or RF work.

## Required implementation

Define a sealed identity-aware transition for permanent tools retained by the
previous committed qualification root. An existing tool may be retained only
when its bytes equal an explicitly allowed predecessor or successor identity;
replacement must be ledgered, atomic, reversible, and limited to exact paths.
Unknown, writable, symlinked, or unbound tools remain fatal.

Bind, per exact absolute path, the predecessor SHA-256, successor SHA-256,
source identity, installed mode, and disposition on commit and recovery.
Validate the entire graph before the first mutation. Write the administrator
ledger before moving predecessor bytes; use same-filesystem temporary and
backup paths, `fsync`, and atomic rename. Recovery must accept each ledgered
interruption point, restore the predecessor exactly, and reject changed
destination or backup bytes. A committed transition removes only its
authenticated backup.

Correct pre-root recovery so a real administrator-owned transaction may invoke
the exact administrator recovery while its ledgered DKMS, source, install, and
tool-transition state exists. Authenticate the outer journal, administrator
ledger, and every owned path before mutation; reject foreign or ambiguous
state; preserve immutable failure evidence; and require the inactive
postcondition. Do not weaken fresh-run baseline checks.

Recovery dispatch must be selected from the authenticated outer journal and
administrator-ledger identity before the fresh-run baseline assertion. It may
not treat arbitrary DKMS residue as authority, infer ownership from a version
string, or bypass either ledger.

## Validation and adversarial review

Add an installed-path rehearsal beginning with the complete retained Phase
5.31 tool set, inject failure after Phase 5.32-style DKMS installation, and
prove the sealed outer recovery reaches exact administrator cleanup. Add
deterministic, unprivileged, network-free tests for wrong predecessor bytes,
partial ledgers, foreign DKMS state, symlinks, interrupted replacement,
changed backup or destination bytes, cleanup failure, repeated recovery, and
the fresh-run residue rejection.

Run focused tests, documentation-link validation, and whitespace checks.
Perform a separate adversarial assessment, reinject every actionable finding,
and repeat affected checks until clean. Record implementation, evidence,
non-goals, and the next gate.

## Authority and exit boundary

The separately authorized Phase 5.32 recovery has completed and is historical
evidence; do not repeat it. Do not create Phase 5.33 release artifacts, freeze
a candidate, stage target inputs, or claim target readiness in this slice.

No module load, overlay, GPIO, clock, DMA, Si5351, transmitter, SDR, reboot,
antenna, transmission, or RF operation is authorized. The next target-affecting
step is a separately authorized Phase 5.33 freeze and representative build,
and only if this offline successor exits cleanly.
