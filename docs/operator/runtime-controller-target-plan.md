<!-- SPDX-License-Identifier: MIT -->

# Separate authorization gate: runtime controller target validation

**Historical approval plan.** The user subsequently authorized and executed one
bounded wspr5 campaign; see the
[execution assessment](../evidence/runtime-target-a0f2794/assessment.md). That
authorization is not transferable to other targets or output-enabled work.
This plan records the original next gate after offline
review of the [controller contract](../contracts/runtime-controller-v1.md).
AGENTS.md requires separate approval for installation, service state changes,
module/overlay operations, GPIO administration and reboot. No previous RF or
route qualification authorizes these changed artifacts. Output must remain
inhibited throughout; there is no transmission test or application restart here.

## Artifacts and preconditions for an approval request

Use only the exact reviewed commit and locally compiled pair in the
[offline build evidence](../evidence/runtime-controller-build-20260831.json).
The evidence records compiler, headers, configuration and module hashes; it is
build evidence, not deployment evidence. Regeneration or changing module bytes
requires refreshed binding, review and approval. Retain the locally generated
`runtime-controller.json` with both module hashes, build-note hashes and the
administration script hash. No moving branch or predecessor module may substitute.

Before requesting mutation approval, refresh a bounded read-only inventory via
`ssh wspr5` exactly. Bind boot ID, kernel/configuration, signing policy, board and
firmware, current boot config/adoption, module and overlay identities, service
units and physical connections. Verify an appropriate safe termination/isolation
arrangement; a software gate alone is not an electrical silence measurement.
The last observation was firmware-selected GPIO20 with an inconsistent installed
GPIO4 overlay. Neither fact may be assumed unchanged.

The approval must identify these separate stages and their effects:

1. Persistently inhibit the named WsprryPi service and stop it. Exclude other
   transmitters, manual application launches, conflicting root administrators,
   configfs/dtoverlay operations, automatic module updates and competing overlay
   consumers. Record the original unit/configuration for manual recovery. Do not
   overwrite an administrator-owned unit file to create the mask.
2. Preserve exact predecessor modules, manifests, boot config and overlays in an
   attributable backup. Stage the approved pair as uncompressed `.ko` files at
   `/lib/modules/6.18.34+rpt-rpi-2712/updates/dkms/rp1_route_controller.ko` and
   `rp1_gpclk_dkms.ko`, removing no foreign files and accounting for any preceding
   compressed `.ko.xz` and module resolution. Install the checked admin script at
   `/usr/lib/rp1-gpclk-dkms/runtime_controller_admin.py`, its root-owned binding
   at `/etc/rp1-gpclk-dkms/runtime-controller.json`, and private 0700 state directory
   `/var/lib/rp1-gpclk-dkms/runtime-admin`. Run approved depmod only after preserving
   rollback artifacts. Revalidate hashes and modinfo resolution. The development
   source manager and Debian-owned manager must remain preserved and query-only.
3. If firmware still owns the active route, prepare and review an exact boot-config
   diff removing only its attributable route selection. Preserve unrelated boot
   settings and conditions. **Approve the reboot separately after that diff is
   available.** Keep the service mask across boot. Do not attempt runtime removal
   of the firmware route. Verify zero matching endpoint/pinctrl nodes, no consumer
   loaded, unchanged kernel and a new recorded boot ID after migration.
4. Load only the approved controller with a fixed absolute insmod path. Its
   initialization must reject non-neutral trees. Verify its loaded note and the
   root-only admin endpoint. No route is selected by this load. Do not enable an
   automatic controller service or use the packaged v1 manager to perform tests.

These are approval-stage descriptions, not a blind installation script. The
installed predecessor ownership and actual config diff must be reviewed before
finalizing target-changing commands; no generic `rm`, overwrite, forced module
removal or reboot command is authorized by this document.

## Clock-disabled test sequence after approved deployment

After verifying all stage identities and the immutable output inhibition:

- Run the installed script with `switch gpio4`. It masks/stops WsprryPi, applies
  only its embedded GPIO4 overlay and loads the instrumented consumer with
  `live_output=0`. Record journal, returned overlay ID/session/generation, actual
  DT route/pin, bound platform device, module/build-note identity and output gate.
  Verify GPIO/clock/DMA safe state using separately reviewed read-only methods.
  STATUS alone is not that electrical/resource evidence.
  The installed tool's `status` command exposes the actual controller ID, error,
  generation and flags even after a failed effect; preserve that result.
- Run `switch gpio20` and then `switch gpio4`, collecting the same independent
  evidence at each step. The boot ID must stay fixed. Prove removal completion,
  zero-or-one endpoint ownership and correct binding; never infer GPIO4 evidence
  from GPIO20. A successful command is not sufficient for qualification.
- Run `recover` to unload the consumer and remove the owned overlay, retaining
  the application mask. Confirm no route, no endpoint, no consumer, clean
  controller flags and safe resource state. Only then may a separately approved
  controller unload be considered. Do not unmask/restart WsprryPi in this gate.

STOP on any mismatch, error, fault, timeout, busy result, unexpected node or
unknown cleanup. Retain journals and kernel observations. No automatic retry,
rollback to the former route, reboot, force unload or inhibit release is allowed.
Explicit same-boot `recover` is cleanup only; it cannot clear a controller fault.
Consumer-cleanup faults block even overlay removal and require an individually
reviewed recovery plan.

## Failure tests need an additional reviewed test implementation

Offline crash and injected-kernel-error cases already exercise the implementation.
Do not inject kernel faults or kill target processes merely from this plan.
Before target failure testing, inspect a bounded helper with exact interruption
points and authorize its commands. Prove an interrupted admin retains inhibition,
pending calls are not assumed finished, stale-session recovery fails closed,
busy consumer removal refuses to proceed, and retained-ID cleanup never permits
an unproven successor. Kernel overlay errors that require dependent overlays or
notifier injection need their own ownership/lifetime review before target use.

Until those tests pass, report successful target switches only as limited
clock-disabled observations, not completed crash-recovery or production support.
RF, transmission, product qualification, release and normal application restart
remain outside every stage above.

The later [runtime manager workflow](runtime-manager-workflow.md) supplies the
complete software inventory and journaled deployment procedure. Use it instead of
manual three-file provisioning; all hardware authorization gates above still apply.
