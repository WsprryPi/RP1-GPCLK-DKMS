<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 split pre-root path repair prompt

Repair only the authenticated pre-root path bindings exposed by the fail-closed
Phase 5.53 target-staging validation. Preserve the frozen product archive
SHA-256 `ae6df3a66a9a26a6fb8474e5896c9053b9f69580d8c45383a5556fc397ebb549`
and qualification archive SHA-256
`d931912d6ccc381b10a2a13d7f3a9122b0f748490ec8eefe0f86a28cb352c8d0`
byte-for-byte.

The current schema-6 envelope incorrectly binds `stagedExecutor` and
`preRootModule` beneath the extracted product archive. Those qualification
tools are intentionally absent from the 54-file product distribution. Bind
both identities instead to their already sealed, input-declared files beneath
`control-set/scripts/`. Keep the administrator beneath the extracted product
archive because it remains a product installation tool.

Regenerate all transitively affected Phase 5.53 controls and attestations from
the existing dual-archive release-input graph. Machine-check that every
pre-root executable identity is present in the exact staged closure, has the
declared hash, and is covered by `inputFiles`. Add a regression that constructs
the 118-file split staging closure and successfully runs the exact archived
executor read-only validation. Re-run deterministic generation, complete
offline checks, documentation/link checks, whitespace checks, and a separate
adversarial review.

Do not contact the target. Do not stage files, invoke the administrator, create
a qualification root or journal, begin lifecycle attempt 1, alter either
archive, install or load a module, touch GPIO/clock/DMA state, transmit, or
produce RF. Any newly generated envelope and execution instance require a new
explicit authorization decision before target work resumes.

Exit only when the repaired offline control set is deterministic, the exact
split staging rehearsal passes, both frozen archive identities remain
unchanged, and the repository records the superseded invalid envelope without
claiming that pre-root transition occurred.
