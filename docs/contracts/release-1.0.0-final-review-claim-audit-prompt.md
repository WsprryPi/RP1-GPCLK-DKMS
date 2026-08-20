<!-- SPDX-License-Identifier: MIT -->

# Release 1.0.0 final review and claim-audit prompt

Audit the exact unchanged product package
`951289ee5d0e44cff41b59756f00161aba16f43f1450715ba57c4a3679a2e6b8`
and repaired qualification archive
`c05f2f2adc20b9e99bf37d775c4bddd6cafd27e5da5e9c62410784fb835727d2`
after successful exact-candidate output-disabled target verification.

Verify literal inventories and checksums, release identity and SemVer mapping,
licensing, product/qualification separation, installation and removal
instructions, compatibility states, safety limitations, evidence ceilings,
target-success evidence, absence of live-output/RF claims, and the remaining
publication and fresh-download gates. Treat conservative pre-execution status
sentences inside the immutable qualification control archive as provenance,
not as the later target outcome; the committed success evidence is
authoritative for that outcome. Do not rewrite or rebuild either sealed
artifact during review.

Require deterministic tag-dependent finalization of only the outer
`release-metadata.json` and `SHA256SUMS` sidecars in a fresh publication
directory. Test that finalizer offline, require it to preserve both sealed
artifact hashes, and prohibit hand-edited publication metadata.

Record and repair every actionable finding, run applicable checks, perform an
adversarial claim review, update only the release-review gate if it passes, and
prepare a separate exact publication authorization prompt. Do not create or
push a tag, publish a release, contact a target, change hardware state, or
modify another repository.
