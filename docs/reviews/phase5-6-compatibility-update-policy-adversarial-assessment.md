<!-- SPDX-License-Identifier: MIT -->

# Phase 5.6 compatibility and update policy adversarial assessment

Date: 2026-08-15
Disposition: no unresolved objective finding

## Scope

This separate offline review attempted to falsify manifest identity and
evidence completeness, route/mode isolation, schema strictness, state/live
combinations, rebuild qualification ceilings, failure transitions, cleanup
latching, enrollment invalidation, prior-bootable retention, fallback
prohibition, and absence of system or hardware action.

## Findings and reinjection

1. The initial entries linked Phase 3B clock-disabled evidence to all modes,
   although Phase 3B did not exercise modes. That link was removed. Each entry
   now links only its exact Phase 4 route archive for mode/timing/cleanup scope.
2. GPIO4 and GPIO20 used distinct disposable signing keys. Direct inspection of
   preserved route archives found GPIO4 fingerprint
   `68:12:74:6D:03:F8:60:79:F1:87:E4:DA:C7:34:CD:3B:35:DA:84:E9` and GPIO20
   fingerprint `41:48:F0:52:DF:C2:2D:62:68:AE:4F:06:C1:2A:33:A2:C1:E7:C5:70`.
   The manifest now records them separately.
3. The first evaluator admitted impossible prior state/live combinations and
   allowed load after explicitly preserving an unavailable identity. Strict
   prior invariants and state-dependent load permission were added with
   negative regression tests.

## Final assessment

The populated entries remain `Unavailable` and non-live because their module,
DTBO, firmware, and calibration boundary does not match a positive Phase 5.2
release decision. Compilation has no automatic path to `Qualified`. Every
specified failure is non-live; cleanup failure remains rejected until explicit
recovery, after which full identity validation is still required. No evaluator
path permits fallback, discovery, target mutation, module loading, overlay
binding, GPIO, DMA, transmission, or RF. No objective finding remains.
