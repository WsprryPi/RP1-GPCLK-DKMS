<!-- SPDX-License-Identifier: MIT -->

# Phase 5.33 retained-tool and recovery successor evidence

Status: offline implementation complete; not frozen; not target-authorized

The qualification identity now has a closed schema-version-2 transition graph.
Each permanent-tool record binds one absolute destination, predecessor and
successor SHA-256 identities, and installed mode. The complete predecessor
graph is authenticated before the administrator creates its transaction or
performs DKMS work. Schema version 1 remains accepted for fresh installations
only and retains its categorical rejection of existing permanent tools.

Qualification replacement writes a `planned` ledger record before mutation,
uses same-directory atomic renames for predecessor backup and successor
installation, checkpoints both states, authenticates both copies at commit,
and deletes only the authenticated backup. Inactive recovery handles planned,
predecessor-backed-up, and successor-installed states; it rejects altered,
missing, symlinked, or ambiguous bytes and restores the predecessor exactly.

Pre-root recovery now preserves its authenticated recovery-required journal as
a read-only failure journal before retrying the fresh transition. The
administrator recovery remains selected only by the authenticated outer
journal plus a real administrator transaction ledger. Fresh execution still
rejects administrator state and non-baseline DKMS residue.

Focused installation, pre-root, bootstrap, frozen Phase 5.32 control-set,
documentation-link, and whitespace checks passed. No target command was run.
No module, overlay, GPIO, clock, DMA, Si5351, transmitter, SDR, reboot,
transmission, or RF operation occurred.

The next gate is a new Phase 5.33 candidate freeze and exact representative
build. This evidence does not authorize or claim either one.
