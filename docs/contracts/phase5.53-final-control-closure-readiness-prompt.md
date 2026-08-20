<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 final control closure-readiness prompt

## Objective

Before generating final controls, reconstruct the complete executable path from
the product-only installed state through same-version removal and authenticated
pre-root qualification installation. Repair every missing qualification-owned
consumer or contract discovered by that reconstruction, reproduce the artifact,
and stop unless the full command graph is representable without cycles.

## Requirements

1. Bind a read-only probe executable that distinguishes product-only, absent,
   and qualified states and rejects any active runtime state.
2. Bind qualification installation to the staged authenticated
   `gate_d_outer.py pre-root-bootstrap` entrypoint.
3. Add an additive pre-root schema accepting an exact terminal `removed`
   predecessor ledger only for the new same-version path. Preserve schemas 1–6.
4. Keep all authority fields false. Do not generate or patch historical
   controls while any executable path is unresolved.
5. Exercise probe states, malformed state rejection, schema-7 acceptance and
   rejection, all transition interruption boundaries, and artifact validation.
6. Commit clean source closures and reproduce each resulting qualification
   successor twice before relying on its identity.

## Non-goals

No target contact, staging, pre-root execution, removal, installation,
lifecycle attempt, module or overlay operation, GPIO, clock, DMA, transmission,
or RF activity.

## Exit criteria

The corrected qualification closure contains the driver, probe, pre-root
consumer, and schema needed to express a non-cyclic final control graph. The
product archive remains unchanged. Final control generation remains a separate
offline slice using only the final identities recorded here.
