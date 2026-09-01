<!-- SPDX-License-Identifier: MIT -->

# Experimental clock-disabled runtime route controller

The runtime manager completes application restoration as specified in
[Runtime application restoration](runtime-application-restoration.md). Its successful switch path
restores a previously running application in idle mode. The low-level controller
transaction ends inhibited; the runtime manager performs the application
handshake afterward. `restore --execute` retries that application completion.

This opt-in development implementation uses exported stock-kernel OF APIs.
It is separate from the packaged route manager.
Deployment, binding and hardware validation require explicit authorization;
software tests do not establish product or RF qualification.

## Build and identity

Run `python3 scripts/build_runtime_controller.py`, then build with
`make KERNEL_BUILD=/path/to/headers RP1_RUNTIME_CONTROLLER=1`. The Make target
regenerates the embedded overlays before compilation. The generated header and
identity JSON under `build/runtime-controller` come only from the two canonical
DTS files, through the existing deterministic overlay builder. Neither controller
ioctl nor userspace administration accepts an arbitrary overlay or path.

The opt-in build produces `rp1_route_controller.ko` (version specified in the
[development identity contract](development-identity.md)) plus `rp1_gpclk_dkms.ko` with the `rp1_runtime_controller=1` modinfo marker
and a link-time dependency on the controller. There is no OF autoload alias in
this opt-in build: the administrator explicitly
loads it after APPLY, avoiding an automatic load racing that step. Its driver
retains the OF match table for explicit binding. The default build retains its
autoload alias. The consumer version follows the same development identity contract;
changed bytes do not inherit qualification. Output-enabled consumer
loads are unconditionally rejected by the interlock. Default builds do not link
the controller or change their administration interface. No default DKMS or package
installation path is added; the explicit runtime bundle has its own reviewed
filesystem deployment workflow. Changing build modes requires clean isolated build
directories; never reuse an opt-in object as a default artifact.

The controller admits only the reviewed Pi 5 Model B / aarch64 /
6.18.34+rpt-rpi-2712 combination and requires a neutral live tree at initialization.
Existing compatible endpoints or canonical endpoint/pinctrl node names reject
admission, including disabled/foreign nodes. It never adopts a firmware overlay.
These checks do not replace coherent deployment or target firmware/resource
validation. Module signing/loading remains an independent prerequisite.

## Kernel ownership and admission

The root-only `/dev/rp1-route-admin` endpoint has the separate 64-byte interface in
`include/uapi/linux/rp1_route_admin.h`. It is separate from the transmission UAPI.
STATUS takes zero session/generation and returns a random controller-instance
session, monotonic generation, owned overlay ID, active route, last kernel error
and flags for fault, consumer presence and lifetime pinning. APPLY permits only
route 1 (`GPIO4`) or 2 (`GPIO20`); REMOVE accepts no route or arbitrary ID. Effects
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
The runtime manager adapter now exposes this transaction on the existing socket
under its own explicit profile; the packaged manager is unchanged. WsprryPi supplies the companion application/browser protocol support. Provisioning must first supply the exact root-owned
binding at `/etc/rp1-gpclk-dkms/runtime-controller.json` and a root-owned private
state directory at `/var/lib/rp1-gpclk-dkms/runtime-admin`. The local-only
`build_runtime_binding.py` renders a review candidate from compiled modules and
the exact installed WsprryPi application companion;
it is not an installer or a claim about loaded target memory.

The version-2 binding fixes the source commit, product and route compatibility
identities, kernel, both uncompressed installed module paths and SHA-256 values,
loaded GNU build-note hashes, both UAPIs, both transformed overlays, every runtime
tool and schema, the base socket/service units, the runtime drop-in, and the exact
WsprryPi application companion. `artifactSetSha256` binds that complete canonical
record. The tool checks module resolution, the consumer interlock marker, loaded
controller note and character-device identity before effects. Build-note agreement
corroborates identity; it is not a full hash of executing memory. Only a coherent
controlled deployment may enroll those observations.

A private nonblocking flock serializes cooperating tool instances. A durable
journal is written with file fsync, atomic replacement and directory fsync before
each effect. It binds boot, controller session, exact binding digest, request UUID,
target route, phase and observed state. A malformed, foreign, stale-session or
cross-boot journal stops administration. Existing controller ownership without a
journal is not silently adopted. Recovery never authorizes a successor.

Before route or consumer effects, the tool persists owned service inhibition,
reloads systemd, stops the service and verifies inactivity. The current owned
`90-rp1-route-inhibit.conf` drop-in and idle restoration handshake are specified
in the [application restoration contract](runtime-application-restoration.md).
Foreign unit files and administrator masks are preserved. Failures and crashes
retain inhibition. The low-level transaction never starts the application; the
runtime manager restores it only after successful route completion. This covers the named service only, not arbitrary root-launched
processes, alternate units or other applications. Operators must exclude those
entry points. The consumer load parameter stays disabled; operation-scoped output
is a separate existing path, as clarified in [runtime output reconciliation](runtime-output.md).

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

The source-development manager remains query-only. No compatibility or release
identity is promoted.
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

## Runtime manager integration

The explicit runtime profile now has an implementation on the existing manager
socket, a bounded operator client, and journaled filesystem deployment tooling.
See [the workflow and its remaining target gates](../operator/runtime-manager-workflow.md).
The runtime profile is distinct from the packaged and source-development
protocols. Exact bindings include the entire runtime software inventory;
incomplete bindings must be regenerated and reviewed. Deployment and
administration share one lock,
and an unfinished deployment blocks administration. The [output reconciliation extension](runtime-output.md) connects application
startup to existing UAPI operation authorization and adds explicit mask resumption.
Route switching never authorizes output. Application restoration releases only
owned inhibition after the required idle-state checks.

`runtime_provider.py` is the single installer facade over these components. Its
read-only `inspect` operation aggregates binding, deployment, controller, route,
application, service, endpoint and passive-output evidence. Its `plan`/`ensure`
and `route-plan`/`route-ensure` pairs require unchanged SHA-256 plan digests.
The latter delegates to the existing preflight-token transaction; it does not
add another overlay or module mutation path. Stable output and exit statuses are
defined in the operator workflow.

### Runtime overlay export policy

Exporting runtime overlay labels adds properties to the base `/__symbols__`
node, whose allocations can leak on removal. Runtime generation uses `fdtput` to
remove only the compiled `/__symbols__` subtree before embedding. The canonical
packaged DTS/DTBO pipeline is unchanged. All route nodes, properties, phandles,
external `__fixups__` and `__local_fixups__` remain byte-for-byte equal as decoded
properties; deterministic regression tests compare both trees. Runtime routes do
not support downstream overlays referencing their labels. This changes controller
and runtime DTBO identities and requires a fresh coherent deployment binding.
