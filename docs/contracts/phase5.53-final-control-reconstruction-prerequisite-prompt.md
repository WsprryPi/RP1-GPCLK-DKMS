<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 final control reconstruction prerequisite prompt

## Objective

Close the executable-consumer gap discovered while reconstructing final
unauthorized lifecycle controls. Provide a qualification-owned executable that
consumes the sealed same-version plan, then reproduce and independently
validate the qualification successor before any control generation.

## Bound identities

- Product source: `4e7a64a0ca353d2fcab6e25891f5254746e2b91a`
- Product archive: `032a0ca214427ebb6115b933042e7135f03c2ed6ce4f5c399686b2cf61395a76`
- Retained target snapshot: `cbaed5a7972bb317a9dc27cabead9419ffde2db474df4de493373b6aa474524f`
- Predecessor qualification archive: `e5614893f61fba63bc76dafa9d4d9ebab0e37437c3a7a8b2b997fa72891ffc59`

## Requirements

1. Add one qualification-only executable consumer for the same-version state
   machine; bind its probe and all mutation commands as argv arrays in the
   sealed plan.
2. Fail closed for an existing or symlinked journal, non-real plan, unsafe
   argv, inherited authority, output-enabled state, malformed probe output,
   and ambiguous recovery state.
3. Exercise the consumer's read-only validation entrypoint and every library
   command-failure and interruption boundary with a fake system.
4. Include the consumer in the qualification layout only. Do not change the
   product layout or product archive.
5. Commit the clean qualification source closure, generate the successor
   twice, require complete byte identity, and validate both independently.
6. Perform a separate adversarial review. Stop before constructing controls
   from a historical package inventory or path graph.

## Non-goals

Do not contact a target; stage artifacts; execute removal, installation,
pre-root, or lifecycle operations; load a module; apply an overlay; reboot;
access GPIO; enable clocks; submit DMA; transmit; or produce RF.

## Exit criteria

The executable is present in the qualification archive at its declared path,
the corrected successor is deterministic and independently valid, the product
artifact is byte-identical, and the next slice can reconstruct every
path-bearing control from the corrected artifact closure.
