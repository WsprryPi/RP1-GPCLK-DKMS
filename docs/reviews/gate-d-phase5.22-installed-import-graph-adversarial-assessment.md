<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.22 installed-import-graph adversarial assessment

## Scope and claim ceiling

This offline assessment covers the Phase 5.22 permanent-executor import graph,
installation layout, release inventory, schema bindings, and deterministic
filesystem tests. It does not constitute a representative build, target
installation, module lifecycle result, GPIO qualification, or RF evidence.

## Assertions tested

- The hyphenated command entry points and separately named underscore Python
  modules install in `/usr/libexec/rp1-gpclk-dkms`, so Python resolution does
  not depend on a source checkout or an ambient working directory.
- Target-plan schema 5 names exactly the seven local Gate D modules and binds
  source path, installed path, source hash, installed hash, copy semantics,
  and archive membership for each one.
- Qualification-bootstrap schema 3 retains the same seven installed module
  identities, and the target-plan validator cross-checks every retained hash.
- The executor authenticates the qualification root, target plan, complete
  module set, ownership, modes, paths, and bytes before executing any module.
- The executor parses every verified payload and rejects any `gate_d_*` import
  outside the closed graph. It executes the already-read bytes, avoiding a
  verify-then-reopen interval.
- Missing modules across the full set, swapped bytes, stale or substituted
  bytes, symlinks, group/world-writable files, extra graph members, wrong
  paths, wrong hashes, and unbound local imports all fail closed.
- Module initialization failure restores prior `sys.modules` entries rather
  than leaving a partial authenticated graph.

## Findings and reinjection

1. **Closed:** placing import modules in a nested `python` directory left
   directly invoked installed commands and recovery paths without a normal
   import route. The modules now install beside the entry points, while their
   underscore filenames remain distinct from the hyphenated commands.
2. **Closed:** a fixed module list alone did not prove that a future trusted
   source edit had not added another local import. The bootstrap now derives
   local import edges from each verified payload and rejects imports outside
   the bound set.
3. **Closed:** a module initialization exception removed names that may have
   existed before bootstrap. Loading now records and transactionally restores
   prior module objects on failure.
4. **Closed:** the first negative test exercised a single subordinate module.
   Missing-file rejection now covers all seven modules, with distinct swapped,
   stale/substituted, symlink, writable, extra-member, and unbound-import cases.

## Result

No open software finding remains in this offline slice. Candidate freeze still
requires a clean source commit, two byte-identical deterministic release
builds, frozen identity metadata, and two complete post-freeze offline-suite
runs. A representative build and any Gate D target execution remain later,
separately authorized gates.
