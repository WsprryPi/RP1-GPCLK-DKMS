<!-- SPDX-License-Identifier: MIT -->

# Rebootless route switching: feasibility and execution plan

Status: research completed on 2026-08-31; runtime switching is not implemented
or target-validated. This document proposes work; it does not change the
[route-manager contract](route-manager-v1.md) or authorize target operations.

## Executed research prompt

Review current route-manager and development-lifecycle code, module discovery
and teardown, and recent changes against the module contract. Use primary
sources to determine whether firmware-applied overlays support runtime removal.
Identify the smallest supported migration and switching design, distinguish
source conclusions from target evidence, and specify identity, ownership,
cleanup, recovery, and validation gates. Preserve the passive development
binding and all package checks. Make only research/documentation changes in
this phase; run applicable offline checks, adversarially assess the result,
repair findings, reassess, and commit/push attributable changes when authorized.
Do not install, load, unload, bind, change overlays or boot configuration,
operate GPIO, reboot, or transmit.

## Source review

Reviewed baseline: `c6d4da8fca36484df4f87079d35f52cc8e3fcdb5`.

| Area | Current capability | Consequence for runtime switching |
| --- | --- | --- |
| `scripts/rp1-gpclk-route-manager.py`, `dispatch` | Source-development permits query only; package operations retain exact identity checks. | Removing the guard would expose the old reboot transaction, not implement switching. |
| Same file, `apply`, `rollback`, `reconcile` | Journals boot-file changes, quiesces fixed services, requests reboot, reconciles after boot-ID change. | A separate transaction and same-boot reconciliation are required. |
| Same file, `source_development_identity`, `source_development_ownership` | Binding and adoption identify one route and one current boot. | Authenticate both destination artifacts and replace current-route proof only after verified transition. |
| Same file, `source_development_passive_safety` | Observes service states, endpoint file descriptors, and immutable module parameter. | Observation is neither an admission lock nor proof that ABI-v4 operation authorization is absent. |
| `scripts/development_workflow.py`, `route_action`, `overlay_action` | Changes boot selection or builds/installs overlay files. | Neither implements a runtime overlay transaction. |
| `src/rp1_gpclk_main.c`, initialization and bootstrap | Requires exactly one endpoint; fallback platform-device creation runs during module initialization. | Do not assume a replacement runtime node will automatically get a working endpoint while the module stays loaded. |
| Same file, remove/exit and platform-bus notifier | Marks dead, quiesces execution, releases resources, and tracks deletion of owned devices. | These are useful mechanisms, not proof of dynamic-overlay lifetime safety. |

Recent changes reviewed: `e7a6b2b` added passive development safety observations;
`1f64c8b` preserved rollback evidence; `0509909` added operation-scoped ABI-v4
live authorization; `4a51061` selected PLL_SYS; `d9acd18` added bounded clock
parent/rate restoration; `c6d4da8` fixed nearest-rate retry cycles. None adds a
runtime route-switch operation. Changed execution bytes require fresh identity
bindings; these improvements do not transfer earlier route qualification.

## Research result

Raspberry Pi documents that firmware-applied overlays form part of the base
tree passed to Linux and cannot be unloaded with the runtime overlay utility.
Runtime removal is available for runtime-applied overlays. Consequently, for
the roadmap's remove-old/apply-new design, a firmware-selected RP1 route must
first migrate to a boot with neither route applied by firmware. This needs an
explicit boot-configuration change and reboot. It is not an experiment in
removing a firmware overlay. Target provenance remains uninspected; a host
already using an attributable runtime overlay may not need this migration.
[Raspberry Pi dynamic Device Tree documentation](https://www.raspberrypi.com/documentation/computers/configuration.html#dynamic-device-tree).

That documentation also warns that removing an earlier runtime overlay can
remove and reapply later overlays. The proposed manager must reject that case,
not disturb unrelated overlays to reach its own. Its inventory and removal
identity need protection against concurrent administrative changes. A private
manager lock alone cannot serialize external overlay tools.

Linux documents overlay-memory lifetime restrictions and rejects removal of
an overlay with dependent overlays. Device/node references and successful
module unbind alone must not be treated as permission to free overlay memory.
Review every retained node pointer through completed teardown, against the
exact target kernel source before implementation is promoted to target use.
[Linux overlay notes](https://www.kernel.org/doc/html/v6.11/devicetree/overlay-notes.html).

No masking overlay, arbitrary node rewrite, simultaneous route endpoints,
custom kernel, raw MMIO, or compatibility bypass is proposed.

## Proposed implementation prompt (next phase)

Implement an Experimental, output-inhibited runtime route lifecycle only after
resolving the design gates below. Preserve packaged v1 operation semantics and
historical journals byte-for-byte. Update the module and manager contracts, closed request
and response schemas, source-development binding schema, lifecycle deployment,
operator documentation, and deterministic tests together. Version the new
protocol explicitly; do not reinterpret `apply-and-reboot` or silently make
the query-only development binding mutation-capable. No production release or
WsprryPi qualification follows from this implementation.

1. Establish an exact target inventory using bounded read-only inspection:
   kernel/configuration, firmware, module installed and loaded identities,
   UAPI, both overlay hashes, manager executable and resolved systemd units,
   route manifests/adoption, boot ID, effective boot selection including
   includes/conditionals, active DT nodes, platform bindings, runtime overlay
   inventory and dependencies, and available supported overlay tool/API.
   Record missing or unreadable evidence as unknown. Do not infer runtime
   ownership from a name or from absence in `dtoverlay -l` alone.
2. Design explicit opt-in migration separately from normal switching. Preserve
   unrelated boot bytes and rollback evidence. Remove only attributable boot
   route selection, then require an authorized reboot and prove zero route
   endpoints. Never load the module into that zero-route state merely to test
   discovery: current initialization rejects it. Decide and document whether
   later boots remain route-neutral or use a separately enrolled runtime
   startup service; do not silently install an automatic route activator.
3. Bind manager executable, module source/build/installed bytes, kernel, UAPI,
   and both route overlays and compatibility identities before any mutation.
   Preserve package-owned executables and units. Old single-route adoption is
   not destination authorization. Keep source-development Experimental and
   distinguish desired, boot-configured, runtime-active, and module-reported
   routes throughout the transaction.
4. Require attributable explicit execution through a restricted protocol with
   fixed route choices only. Serialize requests, reject replay conflicts and
   pending recovery, and coordinate application scheduling/idleness with
   WsprryPi. Stop only owned fixed services and prevent automatic restart or
   new endpoint ownership for the entire transaction. Specify how privileged
   competing overlay/module administration is excluded or detected; stop on
   any race or foreign change. Do not claim technical isolation from a root
   administrator merely because a lock exists.
5. Prove no lease, open owner, pending successor, running descriptor, or cleanup
   fault; verify completed generation cleanup and clock/pin safe state through
   supported observations. Account for ABI-v4 operation authorization: the
   immutable `live_output=0` parameter alone is insufficient. Never invoke a
   live acquire or submit command in this administration path. Missing cleanup
   observability is an implementation blocker, not a reason to infer safety.
6. Prefer evaluating explicit module unload while the old overlay still exists,
   followed by verified owned-device teardown, old runtime-overlay removal,
   proof of zero endpoints, new runtime-overlay application, then exact module
   load with `live_output=0`. This reuses initialization-time fallback discovery.
   It is a proposed sequence, not validated behavior. Prevent modalias-driven
   autoload races during application and authenticate any observed module
   before proceeding. If unload is busy or teardown cannot be proved, stop;
   never force unload. Audit kernel-created versus module-created device and
   OF-node lifetimes before selecting this sequence.
7. Journal intent durably before each effect, then read back and journal its
   result. Include transaction ID, actor, source/destination artifact identities,
   boot ID, service ownership, overlay ownership token, and cleanup observations.
   Reconcile by observed transaction generation and identities within the same
   boot; neither unchanged boot ID nor saved route alone establishes success.
   Publish new adoption only after exact endpoint, binding, route, and inhibited
   safety state agree. Old evidence remains historical, not overwritten.
8. Define crash recovery at every boundary, including after an effect but before
   journal completion. Recover by observation, never blind retry or broad
   overlay removal. Restore the old route only after proving a safe zero-route
   state and its original artifact identities. If recovery is uncertain, leave
   services inhibited and report recovery-required; do not automatically reboot
   or resume the transmitter. Restore previously active services only after
   verified terminal safety and application policy prevent unintended output.

The protocol, admission exclusion mechanism, kernel cleanup observability,
runtime-overlay ownership mechanism, and boot-persistence choice are design
gates to close before enabling mutation. If the exact kernel cannot support
safe removal, retain the reboot-based path and report the limitation rather
than emulate safety with userspace bookkeeping.

## Validation and authorization gates

Offline fixtures must cover both directions and same-route requests; malformed
identities; unknown/foreign/firmware overlay origin; stale adoption; duplicate
or missing endpoints; stacked foreign overlays; concurrent requests; endpoint
reopen and external-state races; operation-scoped authorization despite a zero
load gate; busy unload; partial teardown; autoload; failed apply/probe; journal
write interruption at every boundary; process death; failed rollback; service
restoration failure; and reboot during a transaction. Assert effect ordering
and absence of output commands, not just final response text. Unknown state
must never produce a success or readiness claim.

Inspect all test implementations before running. Run applicable existing
manager, development lifecycle, schema, SPDX, whitespace and documentation-link
checks. Any module changes need identified representative header builds and
kernel lifecycle review; fake tests cannot establish overlay memory safety.

Only after a separate explicit authorization may target administration migrate,
reload modules, apply/remove overlays, change GPIO pin state, or reboot. Bind
the exact plan and artifacts, inspect its commands, keep output inhibited,
and validate each route independently with repeated switching and bounded
failure injection. Do not perform unsafe failure injection that deliberately
frees live kernel references. Preserve baseline, intermediate and terminal
evidence, kernel diagnostics, clock/DMA/pin observations and service states.
Output inhibition is not proof of electrical silence; any required electrical
measurement is a separately scoped validation activity. No transmission,
receiver decode, spectral, RF, product, or release qualification is included.

## Research-phase adversarial assessment

First assessment identified three incomplete assumptions in the initial plan:
firmware overlays were treated as potentially runtime-removable; unload alone
was liable to be mistaken for overlay-memory safety; and a zero immutable load
gate was liable to be mistaken for absence of operation-scoped authorization.
The source findings and implementation gates above correct all three. A second
assessment added explicit foreign-overlay stack/race protection, autoload
handling, and a separate boot-persistence decision.

Final research assessment: no unresolved contradiction in this documented
research scope. Runtime implementation and target safety remain unproven and
are explicitly gated, not classified as passed. No target was inspected or
changed during this research. The proposed implementation prompt has not been
executed; the research prompt above has.

Validation: `tests/check_route_manager.py`,
`tests/check_development_route_manager.py`, `tests/check_spdx.py`, and
`tests/check_doc_links.py` all passed with Python 3; `git diff --check` passed.
These are existing offline fixture and documentation checks, not new runtime
switch tests. No kernel build was needed for this documentation-only change.
