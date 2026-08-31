<!-- SPDX-License-Identifier: MIT -->

# Runtime integration adversarial review

Scope: schema-3 manager, exact inventory binding, deployment journal, operator
client, and companion WsprryPi application/browser workflow. Kernel module source
and transmission UAPI are unchanged from the already reviewed PR #7 baseline.

The first assessment identified and repaired:

- Administration/deployment races: acquire the shared lock before binding reads;
  reject every request while a durable deployment barrier exists.
- Constructor failures leaking descriptors: explicit close-on-failure and manager
  context cleanup now cover lock/endpoint descriptors.
- Replayed success across changed boot/binding/inhibition: require identical
  controller/boot/binding and current inhibition before returning recorded success.
- Unsupported library-path assumptions: accept only root-owned `/lib` aliases
  resolving exactly to `/usr/lib`; reject other symlink targets.
- Misleading output-disabled query: verify the loaded consumer build note and
  output gate as well as installed module bytes.
- Lost recovery controls and HTTP success confusion: retain runtime profile on
  errors, expose pending/fault recovery, reject unsuccessful preflight even on HTTP
  200, and latch unknown completion against switch retries after a disconnect.
- Lost filesystem provenance: preserve all old/new bytes in the durable plan,
  reject any foreign destination before restoration, and retain journals across
  refresh failures. Update requires neutral modules and recovered route state.
- Stale documentation: distinguish the new opt-in socket profile from unchanged
  packaged/source-development interfaces and the earlier standalone CLI phase.

The subsequent assessment checked exact inventory paths, input bounds, duplicate
fields, explicit mutation intent, stale tokens/generations, removal ID/errno
preservation, no automatic retries, persistent masks, crash boundaries, foreign
file protection, and legacy request rejection. No remaining actionable issue was
identified in this bounded offline software scope. This is an in-thread review,
not independent human approval or hardware evidence.

Validation: the full module `make check` suite passes, including nine new manager /
deployment methods and the existing 15 controller/admin methods. The actual
controller C ioctl fixture still passes. The new checks inject every durable
installation-write crash boundary and verify rollback; a separate temporary-root
check exercises actual atomic file writes/fsync/rename/unlink with privilege checks
substituted. They do not run host installation or systemd effects. Bundle creation
passes with the previously built exact-kernel opt-in module pair and canonical
embedded overlays. No new kernel build is claimed for these Python/docs changes.

The companion application's route-service and runtime-wiring C++ tests pass in the
existing Debian aarch64/GCC 14.2 container with networking disabled and sources
mounted read-only. UI static and executable behavior tests pass. The actual panel
was rendered with its existing theme at 1280px desktop and 390px mobile; both were
visually inspected with no horizontal overflow. Failed preflight and disconnected
requests were exercised. The Impeccable mechanical detector reported no findings
on the changed JavaScript. These are isolated panel fixtures, not a live appliance.

Remaining gates: neutral firmware migration, approved installation/activation,
module signing/resolution and systemd sandbox behavior on the exact target,
clock-disabled GPIO4/GPIO20 switching and recovery, and any later restoration of
application/output operation. Browser administration is unavailable after the
manager masks/stops WsprryPi; the operator client is the documented continuation.
No target, service, module, GPIO, DMA, reboot, transmission or RF effects were run.
