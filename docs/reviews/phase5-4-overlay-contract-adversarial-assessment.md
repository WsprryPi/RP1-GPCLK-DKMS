<!-- SPDX-License-Identifier: MIT -->

# Phase 5.4 overlay contract adversarial assessment

## Scope and evidence class

This is a separate offline assessment of the Phase 5.4 execution prompt,
machine-readable overlay contract, frozen release/install integration,
read-only route-change planner, deterministic DTBO compilation, and simulated
failure checks. It performed no system, boot, DKMS, module, overlay, target,
GPIO, clock, DMA, transmission, or RF operation and made no qualification or
publication claim.

## Findings and reinjection

The first pass found that the compiled-artifact test checked useful names but
did not independently assert the decompiled numeric route, pin, resource,
clock, and DMA cells. It also found that generic conflict flags could conceal
missing tests for duplicate persistent markers, runtime-overlay conflict,
endpoint busy state, and unknown configuration ownership. Finally, route
evidence non-transfer was documented but not machine-readable.

Those findings were reinjected into the execution prompt. The implementation
now checks exact decompiled numeric identities, models each named conflict as a
separate fail-closed input, requires known configuration ownership, and records
both directions of GPIO4/GPIO20 evidence independence. Every affected test was
invalidated and rerun.

The final pass attempted to falsify exactly-one selection, arbitrary GPIO and
combined-overlay exclusion, source/DTBO checksum binding, deterministic bytes,
compiled semantic identity, safe default pinctrl, unselected-pin isolation,
conflict-before-persistence ordering, bound-route immutability, both-pin safety,
cleanup-path proof, enrollment renewal, cross-route evidence separation,
unknown snapshot rejection, automatic substitution, and absence of external
commands. No unresolved objective finding remains in the offline Phase 5.4
model.

## Claim boundary

The result defines and verifies the offline overlay and administrative
transition contract only. It does not prove boot configuration atomicity,
runtime conflict discovery, actual unbind/cleanup, pin safety, signing,
representative-target route switching, reboot recovery, or complete removal.
Those remain separately authorized Phase 5 target lifecycle evidence. Neither
route receives new compatibility, enrollment, timing, transmission, or RF
qualification from this slice.
