<!-- SPDX-License-Identifier: MIT -->

# Roadmap

The current [development identity and migration contract](contracts/development-identity.md)
is authoritative for installation transitions and version relationships.

This roadmap records deferred engineering work. An item here is not an
implemented capability, compatibility promise, or qualification claim.

## Rebootless route switching through runtime overlays

An opt-in [clock-disabled controller implementation](contracts/runtime-controller-v1.md)
now provides kernel-owned overlay results, consumer exclusion, persistent service
inhibition and same-boot recovery. It is separate from the PR #6 foundation and
default packaging. The [deployment and target test gate](operator/runtime-controller-target-plan.md)
is still closed; actual rebootless switching and cleanup remain unproven.

PR #6 is the completed research/tooling foundation for this work, not the
runtime-switching implementation. Its delivered scope is source-backed
feasibility research, a bounded read-only inventory collector, curated target
observations, and a synthetic transaction model with offline tests. Finalizing
that scope does not establish route readiness or authorize target changes.

The [wspr5 source/target review](contracts/runtime-route-target-review.md)
records actual read-only inventory, matching kernel/tool source, and a concrete
configfs removal-error blocker. The original synthetic atomic adapter model is
rejected for hardware use. A read-only collector is implemented; a real write
adapter still needs a result-preserving ownership interface. The installed
GPIO4 overlay also differs from the current source build.

An [offline v2 reference model](contracts/runtime-route-v2.md) models
switching, durable journaling, and recovery with deterministic failure tests.
Its synthetic atomic effects are not a contract for a Linux adapter. The
separate public v2 entry point blocks every mutation. No deployment is supplied.

PR #6 did not implement a result-preserving overlay ownership interface, concrete
route effects, application inhibition or crash recovery. Those are delivered by
the later opt-in controller above; they still require coherent deployment and
independent target evidence before the runtime-switching feature is usable.

The [feasibility review and execution plan](contracts/rebootless-route-feasibility.md)
records current code capabilities, primary-source findings, migration needs,
and the separate implementation and target-validation gates. Firmware-applied
routes cannot be removed by the runtime overlay utility; the proposed runtime
overlay design requires migration to a route-neutral boot first when such a
route is present. No runtime switch operation is implemented by that review.

Backlog safe application and removal of the GPIO4 and GPIO20 device-tree
overlays at runtime so an administrator may change the active RP1 GPCLK0 route
without rebooting. The current supported route-manager contract continues to
require an attributable boot-block update and reboot.

The future design must preserve zero-or-exactly-one route ownership and must
never bind GPIO4 and GPIO20 simultaneously, even transiently. Before runtime
switching can replace the reboot boundary, implementation and target evidence
must cover:

- fixed GPIO4/GPIO20 choices with no caller-selected overlay, path, device,
  service, command, or shell interface;
- output-disabled preflight and application execution/scheduling idleness;
- endpoint closure, exclusive ownership, and completed generation cleanup;
- bounded driver unbind, module lifetime, DMA drain, clock disable, and pin
  return to the defined safe state;
- removal of the old overlay before application and binding of the new one;
- rejection and recovery for zero-route, duplicate-route, partial-transition,
  stale-device, busy-resource, and cleanup-fault states;
- attributable journaling, atomic state transitions, readback, rollback, and
  process-death recovery;
- configured-versus-active route reporting without relying on a new boot ID;
- fixed-service quiescence and restoration through the restricted route-manager
  protocol; and
- independent GPIO4 and GPIO20 hardware validation, including repeated
  switching and failure injection with output inhibited before any separately
  authorized live testing.

Until those requirements are implemented and validated, routine operation on
an already active route requires no reboot, but changing routes does.
