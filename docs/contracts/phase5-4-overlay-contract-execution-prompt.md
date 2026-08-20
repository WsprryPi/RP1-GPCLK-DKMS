<!-- SPDX-License-Identifier: MIT -->

# Phase 5.4 overlay contract execution prompt

## Authority and exit condition

Execute only the overlay-contract portion of Phase 5A through Phase 5C in
`phase5-packaging-operator-enablement-execution-prompt.md`. Repository changes
and deterministic, offline validation are authorized. Runtime overlay changes,
boot-configuration changes, module load/bind/unbind/unload, DKMS mutation,
target access, reboot, GPIO, clock, DMA, transmission, RF, tagging, release
publication, and changes to consuming repositories are not authorized.

Phase 5.4 closes when the two production overlays remain distinct,
route-specific administrative choices; their complete source and compiled
identities are frozen and machine-checked; route conflicts fail before any
persistent change; a route-transition planner enforces the controlled
lifecycle below without mutating a system; the complete offline suite passes
twice; and a separate adversarial assessment has no unresolved objective
finding.

## Frozen overlay identities

Exactly one of `rp1-gpclk-gpio4` or `rp1-gpclk-gpio20` may be selected in
persistent configuration. There is no arbitrary GPIO parameter, `__overrides__`
route parameter, combined production overlay, automatic route substitution, or
fallback. Both overlays bind endpoint label `rp1_gpclk_dkms`, compatible
`wsprrypi,rp1-gpclk-dkms-v1`, stock provider clock `rp1_clocks` / `RP1_CLK_GP0`,
and DMA provider `rp1_dma` / `RP1_DMA_DMA_TICK_TICK0`, with exact existing
`reg` and `reg-names` values. GPIO4 is route 1/pin 4; GPIO20 is route 2/pin 20.

Each overlay's `default` and `safe` pinctrl states select only that route's
GPIO input with bias disabled. `active` selects only that route's `gpclk0` at
2 mA. The unselected pin is never named or claimed. A source or DTBO checksum,
compatible, endpoint, route, pin, clock, DMA, resource, or pinctrl mismatch is
`Unavailable`; a known conflict or unsafe state is `Rejected`.

Compile each source twice in new output locations with the frozen preprocessor,
`dtc` identity, options, and input bytes. The DTBO bytes must match. Record and
verify SHA-256 for both sources and DTBOs. Decompile and independently verify
the semantic identities; checksum agreement alone is insufficient.

## Conflict and persistence contract

Before any persistent configuration write, reject duplicate package markers,
both route markers, another route's marker, an already applied conflicting
runtime overlay, a bound/busy/open/running/draining endpoint, non-idle clock or
DMA state, an unsafe pin, unknown ownership, a stale cleanup latch, an artifact
or compatibility-identity mismatch, or an externally changed configuration.
Conflict inspection is read-only and occurs before backup or temporary output
is created. The eventual persistent writer must use one exact package-owned
marker and atomic compare-and-replace with preserved metadata; this slice does
not implement or execute that writer.

No bound route may be mutated in place. Selecting the already selected exact
route is an idempotent no-change result only after the identity and conflict
checks pass. A request for another route never substitutes the current route or
silently falls back after failure.

## Controlled route-change lifecycle

Changing GPIO4 to GPIO20, or GPIO20 to GPIO4, requires all seven gates in
order:

1. prove the module and endpoint idle, with no owner, open descriptor, active
   generation, callback, DMA, prepared/enabled clock, or cleanup fault;
2. disable live eligibility durably before removal;
3. remove the old binding only through the previously proven bounded cleanup
   path, with no hot mutation;
4. verify GPIO4 and GPIO20 are both in the defined safe input state;
5. select exactly one allowlisted new overlay through a separately authorized
   persistent transaction;
6. revalidate the complete hardware, kernel, DT, firmware, module, UAPI,
   compatible, endpoint, route, pin, clock, DMA, resource, overlay source,
   DTBO, signing, cleanup, and compatibility-manifest identity; and
7. require renewed administrator enrollment whenever policy binds enrollment
   to any changed identity.

Every gate records its evidence identity. Failure stops before the next gate,
keeps live output disabled, and requires explicit recovery. GPIO4 evidence and
enrollment never authorizes GPIO20, and GPIO20 evidence and enrollment never
authorizes GPIO4.

## Offline implementation and tests

Add a machine-readable overlay contract and a read-only route-change planner.
The planner consumes an explicit snapshot, rejects missing or unknown fields,
requires the old and new routes to be different allowlisted routes, requires
all idle/cleanup/pin/conflict and artifact identity assertions, and emits the
seven ordered gates with `liveOutput=false`, `persistentMutation=false`, and
`renewedEnrollmentRequired=true`. It must dispatch no external command.

Test deterministic compilation, source/DTBO checksums, decompiled identities,
route symmetry and isolation, safe default states, arbitrary parameter and
combined-overlay rejection, every conflict and lifecycle precondition,
same-route behavior, missing/unknown input, cross-route qualification
non-transfer, and absence of mutation commands. Inspect all tests before
running them. Run SPDX, whitespace, documentation links, release checks, and
the complete offline suite twice.

The decompiled-identity test must assert the numeric route and pin, exact
resource cells, and resolved clock and DMA binding cells, not merely search for
names. Conflict cases remain distinct assertions for duplicate markers,
runtime-overlay conflicts, endpoint busy state, and unknown persistent-file
ownership; generic conflict booleans do not replace those cases. The
machine-readable contract also records both directions of route evidence
non-transfer.

## Adversarial reinjection loop

Separately attempt to falsify route exclusivity, exact identity coverage,
determinism, checksum-to-semantics binding, conflict-before-write ordering,
both-pin safety, bound-route immutability, enrollment invalidation, route-
specific qualification, failure stop behavior, and the absence of automatic
substitution or system mutation. Add every objective finding to this prompt,
correct the implementation, invalidate affected results, and repeat. Stop if a
finding requires target administration, a frozen-interface change, external
coordination, GPIO/clock/DMA activity, or RF authorization.
