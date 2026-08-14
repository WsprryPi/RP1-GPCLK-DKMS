<!-- SPDX-License-Identifier: MIT -->

# Phase 3 GPIO20 and interface-freeze adversarial assessment

Date: 2026-08-14
Scope: Phase 3 prompt, offline implementation, tests, and interface freeze
Result: offline pass after three reinjected findings; target gate open

## Method

The review attempted to falsify the upstream pinmux evidence, GPIO20's
independence from GPIO4, route/pin allowlisting, overlay symmetry and safe
states, mismatch and shared-endpoint conflict policy, repeated administrative
cleanup, UAPI byte identity, manifest evidence isolation, clock-disabled
inertness, licensing, documentation, and compatibility claims. Findings were
added to the prompt before corrections and full-suite reruns.

## Reinjected findings and resolutions

1. Accepting route 2 alone did not prove the overlay declared the matching pin.
   The implementation now requires `wsprrypi,pin`, accepts only GPIO4/4 and
   GPIO20/20, and has deterministic invalid-route and mismatch fixtures.
2. The first symmetry test rewrote the shared 2 mA cell while normalizing route
   2. Normalization is property-specific, leaving shared electrical cells under
   exact comparison.
3. The host-tested route helper included the canonical UAPI but its compile
   command omitted the UAPI include root. The runner now supplies it and the
   warnings-fatal resource-policy test passes twice.

## Passing offline assertions

The Raspberry Pi `rpi-6.18.y` RP1 pinctrl source independently maps GPIO20 to
the generic `gpclk0` function and shows that its mux slot differs from GPIO4.
Both production overlays are identical outside route-specific names, route,
and pin; default/safe remain input with bias disabled, active remains
unselected, and neither overlay references the other pin. The driver rejects
invalid and mismatched route/pin declarations before resource acquisition.

The canonical UAPI hash remains unchanged, ABI/route/ioctl/layout tests pass,
and the manifest validator rejects GPIO4-only evidence for a GPIO20 entry. The
shared endpoint still has one ordered-release ownership gate, so simultaneous
route endpoints fail closed. Deterministic repeated-route models finish absent
in both directions. No clock, pinctrl, DMA-execution, GPIO, transmission, or RF
path was added.

The complete offline suite passed twice, including SPDX, UAPI identity,
manifest, Phase 2C/2D/2E regressions, Phase 3 contracts, dmesg fixtures, links,
ShellCheck, warnings-fatal UAPI/lifecycle/resource tests, sanitizers, negative
UAPI identity, and whitespace.

## Unresolved target gate

No exact target was named and no separate authorization was supplied for
Phase 3 module installation/loading, overlay application/removal, binding, or
clock-disabled administration. Therefore target pinctrl acceptance, route
mismatch/conflict behavior, open/unbind/process cleanup, other-pin safety, and
three-cycle administrative route changes were not executed. GPIO20 remains
`Unavailable` absent a matching manifest entry and has no inherited GPIO4
qualification.

This is a deliberate phase-gate result, not an objective defect in the offline
slice. Phase 3 cannot be described as fully closed until the target matrix in
the execution prompt passes on an exactly authorized identity.
