<!-- SPDX-License-Identifier: MIT -->

# Experimental clock-disabled runtime route controller

This is the implementation follow-up to PR #6, not a replacement for the
packaged v1 route manager or the synthetic v2 model. It uses the reviewed stock
kernel's exported OF APIs. It remains a development implementation pending
separately authorized target testing, not supported product route switching.
The [execution prompt](runtime-controller-execution-prompt.md) defines scope;
the [target gate](../operator/runtime-controller-target-plan.md) remains closed.

## Build and identity

Run `python3 scripts/build_runtime_controller.py`, then build with
`make KERNEL_BUILD=/path/to/headers RP1_RUNTIME_CONTROLLER=1`. The Make target
regenerates the embedded overlays before compilation. The generated header and
identity JSON under `build/runtime-controller` come only from the two canonical
DTS files, through the existing deterministic overlay builder. Neither controller
ioctl nor userspace administration accepts an arbitrary overlay or path.

The opt-in build produces `rp1_route_controller.ko` (experimental admin version
0.1.0) plus `rp1_gpclk_dkms.ko` with the `rp1_runtime_controller=1` modinfo marker
and a link-time dependency on the controller. The consumer remains version
1.1.2, with changed bytes and no inherited qualification. Output-enabled consumer
loads are unconditionally rejected by the interlock. Default builds do not link
the controller or change their administration interface. No DKMS or package
installation path is added. Changing build modes requires clean isolated build
directories; never reuse an opt-in object as a default artifact.

The controller admits only the reviewed Pi 5 Model B / aarch64 /
6.18.34+rpt-rpi-2712 combination and requires a neutral live tree at initialization.
Existing compatible endpoints or canonical endpoint/pinctrl node names reject
admission, including disabled/foreign nodes. It never adopts a firmware overlay.
These checks do not replace coherent deployment or target firmware/resource
validation. Module signing/loading remains an independent prerequisite.

## Kernel ownership and admission

The root-only `/dev/rp1-route-admin` endpoint has the separate 64-byte ABI in
`include/uapi/linux/rp1_route_admin.h`. The transmission UAPI is unchanged.
STATUS takes zero session/generation and returns a random controller-instance
session, monotonic generation, owned overlay ID, active route, last kernel error
and flags for fault, consumer presence and lifetime pinning. APPLY permits only
route 1 (GPIO4) or 2 (GPIO20); REMOVE accepts no route or arbitrary ID. Effects
require the exact session/generation and one controller mutex. Busy operations
reject immediately; status is not an electrical observation.

Every accepted effect advances generation exactly once. The handler records the
actual return code and mutated ID from `of_overlay_fdt_apply` or
`of_overlay_remove`. The ioctl return code indicates delivery or request
rejection; **a delivered response with last_error != 0 is a failed effect**.
The result survives caller death and copy-to-user failure. There is no fabricated
whole-system atomic snapshot or prediction substituted for a syscall result.

An apply failure may retain an ID for explicit cleanup. A removal failure may
retain its ID or clear it after a notification error; both cases latch a fault.
An error never permits another apply. Explicit removal of a retained overlay ID
is allowed after an overlay error, but successful cleanup does not clear the
fault. A no-ID fault remains pinned and requires separately reviewed recovery,
possibly reboot. Never force unload to erase this evidence.

A self-reference retains the controller while an overlay or fault is held,
including after every userspace descriptor closes. Ordinary module exit occurs
only without that ownership; its void callback never tries to remove an overlay
or discard an error. Open controller files and the linked consumer also retain
module references.

The consumer attaches before topology discovery/driver registration and detaches
only after complete device/driver/notifier teardown, including init failures.
Controller mutations reject while attached; consumer admission uses trylock to
avoid a recursive wait from synchronous OF work. Admission refuses live_output=1,
no route, existing consumer or fault. Open transmission files already pin the
consumer, so ordinary non-forced removal cannot outrun their lifetime.

Failed consumer initialization or observed cleanup faults latch a separate
consumer fault. That fault blocks **all** overlay effects, including cleanup
removal, because resource quiescence is not established. No GPIO/clock/DMA
operation is introduced by the controller; consumer binding still selects safe
pinctrl and acquires resources, which is why it requires target authorization.
A userspace timeout cannot bound a blocked kernel teardown.

## Concrete userspace transaction and recovery

`scripts/runtime_controller_admin.py` is a separate opt-in root CLI with only
`switch gpio4`, `switch gpio20`, `recover`, and `status`. STATUS reads the
controller without a route or service effect; it still opens the admin endpoint
and may create the private lock file. It does not claim application inhibition.
The tool is not wired into the packaged
manager, its socket, or WsprryPi. Provisioning must first supply the exact root-owned
binding at `/etc/rp1-gpclk-dkms/runtime-controller.json` and a root-owned private
state directory at `/var/lib/rp1-gpclk-dkms/runtime-admin`. The local-only
`build_runtime_binding.py` renders a review candidate from compiled modules;
it is not an installer or a claim about loaded target memory.

The binding fixes the kernel, both uncompressed installed module paths, their
SHA-256 values, loaded GNU build-note hashes and the installed administration
script hash. The tool checks module resolution, the consumer interlock marker,
loaded controller note and character-device identity before effects. Build-note
agreement corroborates identity; it is not a full hash of executing memory.
Only a coherent controlled deployment may enroll those observations.

A private nonblocking flock serializes cooperating tool instances. A durable
journal is written with file fsync, atomic replacement and directory fsync before
each effect. It binds boot, controller session, exact binding digest, request UUID,
target route, phase and observed state. A malformed, foreign, stale-session or
cross-boot journal stops administration. Existing controller ownership without a
journal is not silently adopted. Recovery never authorizes a successor.

Before route or consumer effects, the tool creates and fsyncs the persistent
`/etc/systemd/system/wsprrypi.service -> /dev/null` mask, reloads systemd, stops
the service and verifies inactivity. A foreign existing unit file is not
replaced. Failures and crashes keep the mask; it blocks ordinary systemd service
starts, restart-on-failure and boot starts. The tool never unmasks or restarts the
application. This covers the named service only, not arbitrary root-launched
processes, alternate units or other applications. Operators must exclude those
entry points. Independently, the instrumented consumer cannot enable output.

The tool unloads only the exact checked consumer with non-forced rmmod, checks
absence and controller detachment, removes the owned overlay, then applies the
new fixed overlay and loads the checked consumer with `live_output=0` using its
fixed absolute module path. No modprobe install/remove hook or dependency removal
is used for effects. Each stage rechecks inhibition and boot identity. Completion
requires actual controller readback and successful consumer initialization;
the application remains inhibited even on success.

After a crash, ordinary switch refuses a pending journal. Explicit `recover`
accepts only the same boot/session/binding and an attributable generation (the
recorded generation or the single pending overlay effect). It inhibits again,
unloads the matching consumer and attempts only removal of a retained ID. A
clean recovery ends route-neutral and inhibited. Latched faults, ambiguous state,
identity mismatches and failures stop without restart, automatic reboot or
rollback to an unproven route. Interrupted kernel calls may still be pending;
busy status stops recovery instead of assuming completion.

## Boundaries and validation

Cooperative privileged administration is a requirement. Root can load an old
uninstrumented consumer, edit device tree, alter a mask or force-remove modules;
this design does not isolate itself from unrestricted root. Do not operate
configfs/dtoverlay, install alternate modules, bind other drivers or load dependent
overlays during a transaction. Such interference invalidates the campaign.

The public v2 model entry point remains blocked. The source-development v1 manager
remains query-only. No existing compatibility or release identity is promoted.
Kernel/controller code uses `GPL-2.0-only OR MIT`, declares Dual MIT/GPL, and uses
exported GPL-compatible APIs. Independent tooling and tests use MIT; the separate
administrative UAPI uses the project's syscall-note dual license. No upstream
implementation is vendored.

Offline tests exercise the real controller ioctl handler with mocked Linux APIs,
not the rejected synthetic transaction adapter. Fault injection covers partial
apply, both removal-error ID outcomes, retained module references, stale requests,
consumer exclusion, cleanup faults and response-copy failure. Userspace tests
cover actual transaction logic, command construction, persistent inhibition and
journal crash boundaries. These do not prove OF notification, kernel scheduling,
pinctrl state, timing, cleanup, coexistence, rebootless switching or RF safety.
