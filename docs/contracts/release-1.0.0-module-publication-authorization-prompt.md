<!-- SPDX-License-Identifier: MIT -->

# Release 1.0.0 module-publication authorization prompt

I explicitly authorize publication of Release 1.0.0 from the exact reviewed
decision commit named in this authorization, using unchanged product SHA-256
`951289ee5d0e44cff41b59756f00161aba16f43f1450715ba57c4a3679a2e6b8`
and qualification SHA-256
`c05f2f2adc20b9e99bf37d775c4bddd6cafd27e5da5e9c62410784fb835727d2`.

First require a clean synchronized branch, exact reviewed commit at `HEAD`, no
local or remote `v1.0.0` tag, no existing GitHub release, and valid GitHub CLI
authentication for `WsprryPi/RP1-GPCLK-DKMS`. Stop without creating anything
if authentication or any identity differs.

Create one annotated `v1.0.0` tag at that reviewed decision commit and push
only that tag. Copy the sealed local release directory to one new temporary
publication directory, run `scripts/finalize_release_publication.py` there,
and verify the resulting complete checksums, literal eight-file inventory,
`tagPresent=true`, `publishable=true`, exact decision commit, and unchanged
product and qualification hashes. Do not alter the retained candidate
directory or rebuild either artifact.

Create one non-draft, non-prerelease GitHub Release `v1.0.0` with concise notes
that state the output-disabled claim ceiling and attach exactly the product,
qualification archive, compatibility manifest, product inventory,
qualification identity, target-verification plan, finalized release metadata,
and checksum file from the temporary directory. Verify the public release page
and attached asset names and sizes, preserve publication evidence, remove only
the temporary publication directory, and stop before treating the release as
consumable.

If any action fails after the tag or release is created, do not delete, move,
replace, or recreate remote state. Record the exact partial state and stop for
operator direction. This authorization does not permit target contact,
hardware activity, public-download verification, consumer integration,
branch merging, or publication of any other version.
