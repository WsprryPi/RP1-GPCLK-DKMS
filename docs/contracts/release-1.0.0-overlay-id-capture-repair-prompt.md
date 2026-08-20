<!-- SPDX-License-Identifier: MIT -->

# Release 1.0.0 overlay-ID capture repair prompt

Repair only the separate Release 1.0.0 qualification controls after the
recorded GPIO4 target failure. Keep the Debian product package frozen at
SHA-256 `951289ee5d0e44cff41b59756f00161aba16f43f1450715ba57c4a3679a2e6b8`.

Replace the invalid assumption that `dtoverlay` apply stdout contains an
identifier. Capture authoritative runtime-overlay inventories immediately
before and after apply, require an empty baseline, require exactly one added
identifier, require that identifier to name the requested project overlay, and
use only that identifier for removal and failure cleanup. Test the same path
with both empty and nonempty apply stdout and reject ambiguous deltas.

Reconstruct the successor target plan from the new qualification closure and
the actual installed `1.0.0-1` target baseline. Do not reinstall the already
installed package before GPIO4. The remaining sequence is GPIO4, GPIO20,
complete removal audit, reinstall of the unchanged product package, and final
inactive verification.

Run applicable offline, documentation, packaging, and adversarial checks.
Commit the repair, then build the separate qualification artifact twice from
that exact clean commit using the pinned builder and unchanged product package.
Require byte-identical qualification archives, literal inventories, extracted
control validation, fake-system coverage, unchanged product hash, and a new
digest-bound authorization prompt. Do not contact `wspr5`, modify its retained
staging directory, load a module, apply an overlay, perform package operations,
create a tag, or publish anything.
