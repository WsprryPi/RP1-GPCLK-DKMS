<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.16 tooling-identity adversarial assessment

Status: offline software review passed; target evidence pending

## Scope

This review attacks the Phase 5.16 correction that separates immutable source
identities from installed executable identities. It does not qualify target
lifecycle behavior and authorizes no target mutation.

## Assertions and results

1. **A historical single-digest plan cannot execute.** Passed. Schema version
   1 remains structurally inspectable only; live validation rejects it.
2. **Source and installed identities cannot be omitted or substituted.**
   Passed. Schema version 2 requires both 64-hex digests and rejects missing,
   malformed, or changed source identities.
3. **Installation semantics cannot be relabeled.** Passed. Python tools are
   required to be `copied`; C helper sources are required to be
   `target-built`. Copied identities must be equal.
4. **Installed bytes are independently enforced.** Passed. Target preflight
   compares regular-file installed bytes only with `installedSha256`; changed,
   missing, and symlinked paths fail closed.
5. **Historical evidence cannot silently become current.** Passed. The sealed
   Phase 5.14 attempt index intentionally differs from the advanced executor;
   the superseded instance skips live bundle validation and remains blocked.
6. **The correction expands no output authority.** Passed by static contract
   and the complete offline suite. No live-output, GPIO, clock, DMA, SDR, or RF
   permission changed.

## Remaining gates

The successor is not frozen. Deterministic release identities, a representative
stock-header module build, target-built helper hashes, a Phase 5.16 route
decision, target plan, 38-attempt bundle, and execution instance remain
required. Target lifecycle execution remains prohibited pending a fresh exact
authorization after those documents are sealed.
