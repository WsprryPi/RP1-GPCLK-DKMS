<!-- SPDX-License-Identifier: MIT -->

# Release 1.0.0 final review and claim audit

Result: **the exact output-disabled candidate passes release review; publication
remains separately blocked**.

The sealed Debian product
`951289ee5d0e44cff41b59756f00161aba16f43f1450715ba57c4a3679a2e6b8`
and qualification archive
`c05f2f2adc20b9e99bf37d775c4bddd6cafd27e5da5e9c62410784fb835727d2`
pass their complete checksum set and literal inventories. Version `1.0.0`,
Debian revision `1.0.0-1`, expected tag `v1.0.0`, UAPI, overlays, licensing,
product/qualification separation, conventional package behavior, instructions,
and provenance are internally consistent.

Compatibility remains conservatively `Unavailable` and `liveEligible=false`.
Exact GPIO4 and GPIO20 output-disabled lifecycles and package removal/reinstall
passed on the representative target, but no live-output, timing, transmission,
RF, arbitrary-kernel, or consumer compatibility claim is made. The
qualification archive is the immutable pre-execution control closure; its
conservative pre-execution status sentences remain provenance. The later
committed target-success evidence is authoritative for the completed
output-disabled outcome. Rewriting those members would create a new control
archive without strengthening the release claim.

One publication-mechanics gap was repaired without changing either sealed
artifact: `scripts/finalize_release_publication.py` deterministically converts
only copied outer metadata and checksums from candidate to tag-bound publication
state. It requires the expected tag at `HEAD`, preserves both artifact hashes,
rejects an unexpected directory or already-finalized input, and passed its
offline test. The original candidate directory remains unchanged.

No local or remote `v1.0.0` tag exists, and GitHub's public release endpoint
returned 404. A sandboxed authentication check could not access the macOS
Keychain and incorrectly appeared invalid; an outside-sandbox check confirmed
the active `lbussy` keyring credential with `repo` and `workflow` scopes. No
tag, release, target, hardware, transmission, RF, or consumer action occurred
during review.

Claim ceiling: reviewed exact output-disabled candidate only. Publication,
fresh public-download verification, and consumer integration remain separate
gates.
