<!-- SPDX-License-Identifier: MIT -->

# Roadmap

This roadmap records deferred engineering work. An item here is not an
implemented capability, compatibility promise, or qualification claim.

## Rebootless route switching through runtime overlays

The [wspr5 source/target review](contracts/runtime-route-target-review.md)
records actual read-only inventory, matching kernel/tool source, and a concrete
configfs removal-error blocker. The original synthetic atomic adapter model is
rejected for hardware use. A read-only collector is implemented; a real write
adapter still needs a result-preserving ownership interface. The installed
GPIO4 overlay also differs from the current source build.

An [offline v2 transaction engine](contracts/runtime-route-v2.md) now models
switching, durable journaling, and recovery with deterministic failure tests.
The target adapter, persistent administrative admission, runtime-overlay
ownership mechanism and post-unload attestation remain unimplemented; the
separate public v2 entry point blocks every mutation. No deployment is supplied.

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
