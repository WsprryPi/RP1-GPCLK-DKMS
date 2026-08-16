<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.25 pre-root staging and recovery adversarial assessment

Status: offline software findings closed; clean-commit freeze not performed

Phase 5.25 adds a schema-2 pre-root envelope with an exact seven-role release
input graph. The archive, GPIO4 DTBO, GPIO20 DTBO, compatibility manifest,
provenance, release metadata, and `SHA256SUMS` must share the administrator's
release directory, be individually hash-bound input files, and agree with the
closed checksum membership before mutation. Historical schema-1 envelopes
remain parseable only for their frozen evidence.

The pre-root journal now records administrator invocation. Recovery validates
the complete partial-root tree before invoking administrator recovery or
deleting anything. It skips administrator recovery when the exact transaction
state is absent and the empty runtime baseline still holds, invokes it only
for real state after a recorded invocation, and rejects symlinked, ambiguous,
or foreign state.

The first independent adversarial pass found that recovery deleted authenticated
children before discovering a foreign partial-root child. That finding was
reproduced and corrected: the entire partial tree, directory closure, marker,
and every present transition hash are now authenticated before the first
recovery mutation. A regression test proves that the marker and foreign byte
remain untouched and administrator recovery is not invoked.

The separately installed `gate-d-residue` tool and exact Phase 5.24 recovery
document validate the observed marker and journal hashes, absent administrator
state, empty DKMS/module/overlay baseline, preservation paths, and
output-disabled safety. Offline tests cover exact cleanup, already-clean replay,
changed marker or journal, administrator state, foreign child, symlink,
baseline drift, and preservation of staged evidence.

The complete offline suite passed twice after the correction. Two development
release builds validated and were byte-identical, including archive and all
sidecars. Their archive SHA-256 was
`06b8b85750564b3d292ebbd09a19e0754ce3c2678cf7e2d50749e923f7c9677f`.
They are not frozen identities: the worktree is intentionally uncommitted, the
metadata reports dirty source, and the user has not authorized a commit.

No Raspberry Pi was contacted during this correction slice. The recorded
Phase 5.24 residue remains unchanged. A clean implementation commit is required
before deterministic rebuild and offline identity freeze. Separate
authorization is then required for exact Phase 5.24 residue cleanup, followed
by distinct authorization for Phase 5.25 representative build and later Gate D
execution.
