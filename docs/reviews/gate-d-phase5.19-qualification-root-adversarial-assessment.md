<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.19 qualification-root adversarial assessment

Status: offline software review passed; candidate frozen

The correction separates installed package-tool identity from test-owned
qualification-document identity and eliminates implicit source-checkout root
fallback. The root is absolute, real, non-symlinked, UID-bound, mode-0700, and
bound by a hashed marker. Target plan schema 4, execution instance schema 3,
attempt index schema 2, bootstrap schema 2, and outer dispatch carry the same
reference. Tests cover missing, relative, stale, swapped, symlinked,
permission-incompatible, traversal, and installed-outside-checkout use.

## Findings closed

1. The initial schema-4 branch omitted installed-tool identity semantics. It
   now applies the same copied-versus-target-built checks as schemas 2 and 3.
2. Individually valid but swapped roots were initially possible across
   documents. Bootstrap, target plan, execution instance, attempt index, and
   outer dispatch now require exact reference equality.
3. The host test environment exposed a symlinked `/var` component. Tests now
   use the canonical real path; production validation continues to reject all
   symlink components rather than normalizing them silently.

The qualification root is retained as the immutable evidence and document
container. Existing attempt-owned staging cleanup rules remain responsible for
their exact subpaths; neither interruption recovery nor ordinary cleanup may
remove or replace the root marker.

Two deterministic development builds from source commit
`7753692dd63cfa5fdda3f0a4d89dbd63161da719` were byte-identical. The frozen
archive SHA-256 is
`8754f0490987ec9bf0eeccd8cdeaa60747116ac73f53fcc099f0af5a3c66efce`.
