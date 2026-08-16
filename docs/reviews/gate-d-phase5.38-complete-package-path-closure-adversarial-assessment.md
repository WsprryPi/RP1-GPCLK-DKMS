<!-- SPDX-License-Identifier: MIT -->

# Phase 5.38 complete package-path closure adversarial assessment

Status: offline successor implementation passes; target execution remains
unauthorized

Phase 5.38 removes the prospective control set's dependence on the historical
22-entry retained-tool constant. Schema 3 instead expands canonical
destinations from the exact release layout embedded in the checksummed
candidate archive. Archive trees become concrete files from the archive member
set. Duplicate destinations, empty archive-tree expansions, unsafe paths, and
ambiguous archive roots fail closed.

Before transaction creation or any external command, the administrator now
computes the exact existing subset of that package path universe and requires
set equality with the authenticated package-transition graph. The diagnostic
reports all missing and extra paths together. Each regular file binds type,
predecessor and successor SHA-256, mode, owner, and group. Each symlink binds
type, exact predecessor and successor relative target, owner, and group.
Regular files and symlinks use journaled atomic replacement and type-aware
recovery. Operator documentation uses the same replacement primitive as
permanent tools rather than a separate reject-if-present loop.

Mechanical expansion exposed and corrected a second latent source defect:
`release-layout-v1.json` named `docs/operator/signing.md` both through the
`operator-docs` archive tree and through a separate `signing-guidance`
artifact. The redundant artifact was removed; future duplicate canonical
destinations are rejected by construction.

The focused temporary-root regression proves the complete observed predecessor
surface: 22 regular permanent-tool paths, four regular documentation paths,
and two command symlinks. A schema-3 transition replaces and commits all 28.
A separate omission case proves that one missing documentation path is named
and rejected before transaction creation and before the external runner is
called. Successor mismatch injection at every one of the 28 regular-file and
symlink replacement boundaries proves complete predecessor restoration without
residue. Existing schema-2 tests continue to protect already sealed historical
control sets; new successors must use schema 3.

Adversarial review challenged manual-list drift, duplicate layout entries,
archive-tree expansion, canonical paths, missing and extra entries, file versus
symlink substitution, predecessor identities, pre-mutation ordering, commit
exhaustion, and recovery typing. The complete offline suite passed, including
SPDX, release-unit, installation, historical control-set, documentation-link,
ShellCheck, compile, lifecycle, sanitizer, and whitespace checks. The Linux-only
UAPI client compile checks were skipped on macOS as expected.

No target, DKMS, module, overlay, boot, service, GPIO, clock, DMA, separate I2C
Si5351, SDR, antenna, transmission, or RF operation was performed. This change
does not authorize a target retry and does not modify the sealed Phase 5.37
candidate or evidence. The next gate is a new Phase 5.38 freeze and exact
representative build, followed by a separately generated and independently
validated schema-3 control set.
