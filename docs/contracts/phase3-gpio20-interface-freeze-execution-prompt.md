<!-- SPDX-License-Identifier: MIT -->

# Phase 3 GPIO20 injection and interface-freeze execution prompt

## Outcome

Act as the RP1 kernel-module maintainer and adversarial reviewer for
`WsprryPi/RP1-GPCLK-DKMS`. Independently establish GPIO20's RP1 GPCLK0 route,
pinmux, electrical capability, safe state, and device-tree representation;
add it as the second administrative route through the existing route-neutral
module machinery; test route mismatch, conflicts, cleanup, and repeated
administrative route changes; then freeze the first public UAPI, overlay names,
overlay properties, device/module names, and compatibility-manifest contract.

GPIO20 is a separate route. No GPIO4 build, bind, clock-disabled, timing, live,
or RF evidence transfers to GPIO20.

## Authority and safety boundary

Follow `AGENTS.md`, the module engineering contract, phased plan, licensing
policy, accepted decisions, and the Phase 2 evidence boundary. Preserve the
stock `clk-rp1` provider and the clock-disabled implementation boundary.

Repository editing, offline builds, static analysis, deterministic host tests,
and target-test preparation are authorized by this prompt. Target installation,
module load/bind, overlay application/removal, or other target administration
requires an exact named-target authorization before execution. Even with that
authorization, Phase 3 forbids active pinctrl selection, clock prepare/enable
or rate changes, DMA descriptor submission, GPIO output, transmission, RF,
boot changes, reboot, and service changes. GPIO4 and GPIO20 must remain inputs;
GPCLK0 prepare and enable counts must remain zero.

## Independent route evidence

1. Pin the upstream source identity used for the decision. Verify in the
   Raspberry Pi kernel's RP1 pinctrl table that GPIO20 exposes `gpclk0`, and
   distinguish its selector position from GPIO4 rather than copying a legacy
   BCM assumption.
2. Verify GPIO20 is an RP1 GPIO group represented by the generic RP1 pinctrl
   binding with `pins = "gpio20"` and `function = "gpclk0"`.
3. Confirm the header mapping and electrical boundary: GPIO20 is the BCM GPIO20
   header signal, the overlay requests only the minimum 2 mA drive for its
   unselected future active state, and both `default` and `safe` are input with
   bias disabled. This is representation evidence, not electrical or RF
   qualification.
4. Record exact upstream URLs, branch/revision, relevant lines, what each source
   proves, and what still requires target observation.

## Required implementation

- Accept only stable routes `GPIO4 = 1` and `GPIO20 = 2`; reject invalid and
  arbitrary values.
- Require an explicit route pin identity and reject inconsistent route/pin
  pairs (`GPIO4/4`, `GPIO20/20` are the only valid pairs).
- Add `rp1-gpclk-gpio20.dts` beside `rp1-gpclk-gpio4.dts`. Both overlays use the
  same compatible, node name, GPCLK0 clock, RP1 DMA TICK0 request, pinctrl state
  names, device name, UAPI, and module implementation. Only the route identity,
  pin identity, labels, and selected pin differ.
- Each overlay claims exactly one route. Neither overlay may mention or reserve
  the other pin. Simultaneous endpoints remain rejected because both represent
  the same GPCLK0/DMA endpoint.
- Add deterministic negative fixtures for unsupported route and route/pin
  mismatch. Preserve existing GPIO4 conflict and partial-probe coverage.
- Keep all output ioctls unsupported and do not add live capabilities.

## Offline test matrix

1. Compile and decompile both production overlays against identified Raspberry
   Pi DT bindings when available; structurally validate them everywhere.
2. Prove exact route/pin allowlisting and rejection of `0`, `3`, arbitrary
   values, `GPIO4/20`, and `GPIO20/4` through a host-testable policy helper.
3. Prove both overlays are mechanically symmetric for all shared endpoint
   properties and differ only in their route-specific fields.
4. Prove default/safe states are input, bias-disabled, and reference the same
   route's safe node; active is never default or safe.
5. Prove neither production overlay names the other route's pin.
6. Prove UAPI route mismatch still returns `EINVAL` before ownership mutation,
   invalid routes remain rejected, and GPIO20 query/acquire uses the same
   route-neutral structure and ioctl values.
7. Prove endpoint conflict exclusion is shared across routes, release is
   ordered after cleanup, and repeated modeled sequences
   `GPIO4 -> absent -> GPIO20 -> absent -> GPIO4` and the reverse leave no
   owner, selected pin, clock, DMA, or fault state.
8. Freeze and machine-check the UAPI bytes/semantic identity, overlay names and
   properties, module/device names, manifest schema/version/enums, and the rule
   that compatibility/evidence records are route-specific.
9. Run SPDX, documentation/link, whitespace, existing lifecycle/resource/UAPI,
   and complete offline regression checks twice.

## Separately authorized clock-disabled target matrix

On an exact authorized target only, capture baseline identity and safety for
both pins, then build the same source and both overlays. For each route:

1. Apply only its production overlay; prove the expected bound route/pin,
   restrictive device, resource identity, queried route, matching acquire and
   release, safe selected pin input, other pin input and unclaimed, and zero
   GPCLK0 prepare/enable counts.
2. Require an acquire naming the other route to fail without ownership change.
3. While bound, attempt the other production overlay and require endpoint
   conflict rejection without disturbing the first route or either safe state.
4. Exercise the invalid-route and route/pin-mismatch overlays; require bind
   rejection before resource ownership and no device or state change.
5. Repeat administrative sequences at least three complete cycles in each
   direction. Each transition is remove-to-absent then apply; hot route mutation
   of a bound node is unsupported. Bound/open/acquired route removal behavior
   must retain Phase 2 lifetime guarantees.
6. Exercise process death, open descriptor across unbind, duplicate endpoint,
   pin conflict, missing state, bad DMA, and cleanup for each applicable route.
7. Capture bounded command status, dmesg suffix by intact-baseline proof,
   artifact hashes, runtime DT, query identity, pre/post invariants, and final
   removal. Unclassified warnings, cleanup faults, a non-input pin, or nonzero
   prepare/enable counts fail the run immediately.

Target evidence may raise only that exact route/identity to the state warranted
by the compatibility contract. GPIO20 remains unqualified for timing, live
output, transmission, and RF after a clock-disabled pass.

## First-public-interface freeze

After the offline matrix and any authorized target matrix pass, freeze:

- UAPI ABI 1 header bytes, enum values, ioctl numbers/directions, structures,
  sizes, offsets, reserved fields, capabilities, state and reason meanings;
- module name `rp1_gpclk_dkms`, compatible
  `wsprrypi,rp1-gpclk-dkms-v1`, device `rp1-gpclk`, and DT properties
  `wsprrypi,route` and `wsprrypi,pin`;
- overlay source names `rp1-gpclk-gpio4.dts` and
  `rp1-gpclk-gpio20.dts`, their one-route-per-overlay model, and pinctrl names
  `default`, `active`, `safe`; and
- compatibility-manifest schema version 1, state/route/mode vocabularies,
  artifact identity fields, default `Unavailable`, and route-specific evidence.

Future changes are additive or require a deliberately new ABI/schema/compatible
identity. The freeze does not claim release readiness, packaging completion,
installer integration, WsprryPi integration, or qualification.

## Adversarial exit loop

Use a separate assessment pass to falsify: upstream route evidence; GPIO20
independence; route/pin validation; other-pin non-ownership; overlay symmetry
and safe states; mismatch/conflict behavior; repeated route-change cleanup;
UAPI and manifest identity; clock-disabled inertness; licensing; claimed
compatibility ceiling; target authorization/evidence boundaries; and final Git
state. Append every objective finding below, correct the prompt, code, tests,
or evidence, rerun all affected checks plus the complete offline suite, and
repeat until no objective finding remains. A missing mandatory target result
keeps the Phase 3 target gate open; it must not be converted into an offline
pass.

## Exit statement

Report the offline implementation/freeze gate and target clock-disabled gate
separately. Phase 3 is fully closed only when both routes have independent
clock-disabled target evidence under exact authorization. Never describe an
offline implementation pass as GPIO20 hardware qualification.

## Reinjectable findings log

1. Initial design accepted route 2 without proving that the overlay pin matched
   the declared route. The contract now requires `wsprrypi,pin` and exact
   route/pin-pair validation, with mismatch fixtures and tests.
2. The first overlay-symmetry check normalized every `<2>` cell and therefore
   mistook GPIO20's shared 2 mA drive cell for its route value. Normalization is
   now property-specific so shared electrical settings remain compared exactly.
3. Moving route validation into the host-tested resource policy introduced a
   canonical-UAPI include without adding the UAPI include root to that test's
   compile command. The offline runner now supplies both project include roots.
