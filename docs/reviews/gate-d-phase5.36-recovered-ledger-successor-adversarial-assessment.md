<!-- SPDX-License-Identifier: MIT -->

# Phase 5.36 recovered-ledger successor adversarial assessment

Status: accepted for a new freeze; no target execution authorized

The implementation addresses the exact Phase 5.35 blocker rather than
weakening the existing absence check. Schema version 3 requires an explicit
`priorTerminalState` identity while schema versions 1 and 2 retain their
existing behavior.

The new identity closes the canonical and archive paths and binds the prior
ledger's SHA-256, owner UID, `0600` mode, terminal status, recovery flag,
live-output flag, and read-only archive mode. Only `status=recovered`,
`recoveryRequired=false`, and `liveOutput=false` are accepted. The archive
must be a unique file one bounded `history` directory below the canonical
state directory; an existing archive or an unsafe archive directory fails.

The pre-root journal is written before the atomic move. The canonical path is
then available for the successor administrator transaction. If interruption
occurs before administrator invocation, authenticated recovery moves the exact
archive back to the canonical path, restores mode `0600`, removes the empty
archive directory when possible, and preserves the failure journal. If the
administrator was invoked, its own authenticated recovery remains authoritative
and the historical ledger is retained separately.

Offline tests prove successful archival, interruption restoration, hash tamper
rejection, nonterminal rejection, symlink rejection, wrong-mode rejection,
preexisting-archive rejection, unsafe archive-directory rejection, escaping
path rejection, and unchanged legacy-envelope behavior. The focused pre-root
test and complete offline suite pass. The three Linux-only UAPI client compile
checks remain explicitly skipped on macOS; applicable probe and injector
compile checks pass.

No wspr5 ledger was moved or deleted. No candidate was frozen or staged, and no
DKMS, module, overlay, service, GPIO, clock, DMA, Si5351, SDR, transmitter,
reboot, transmission, or RF action occurred. No actionable finding remains in
this offline successor scope. The next gate is a new freeze and representative
build containing this implementation.
