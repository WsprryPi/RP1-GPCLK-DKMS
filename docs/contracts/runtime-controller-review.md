<!-- SPDX-License-Identifier: MIT -->

# Runtime controller implementation review

Date: 2026-08-31. Scope: the opt-in controller, instrumented consumer, concrete
administration tool and deployment gate. This is a separate implementation after
PR #6's finalized research foundation. No target operation was performed.

## Adversarial pass and repairs

- **Unexported OF traversal:** the first real matching-header modpost rejected
  `__of_find_all_nodes`. Replaced all-node traversal with exported compatible/name
  lookups, covering both canonical endpoint and pinctrl names. Both final module
  builds pass compile, modpost and linking without private symbols.
- **Cleanup snapshot access:** the first compile found the cleanup fault is in
  `core.value`, not the enclosing core. Corrected the access and compiled both
  opt-in and default builds. No stub-only compilation is claimed as kernel proof.
- **Consumer cleanup uncertainty:** a generic fault initially still permitted
  overlay cleanup. Added a separate latched consumer fault that blocks every
  overlay effect, including REMOVE. The real ioctl fixture verifies rejection.
  Consumer teardown also reports residual clock, pin, DMA, parent/tick or worker
  state. Failed consumer initialization similarly blocks administration.
- **Recovery attribution:** strengthened journals with strict fields and primitive
  types, UUID checks, duplicate-JSON rejection, same-boot/session/binding checks
  and exact allowed generation deltas. Recovery cannot adopt unrelated controller
  changes. Unexpected route/generation changes during consumer load or unload stop
  before a successor and cannot be recorded as completion.
- **Concrete effect safety:** use fixed absolute insmod and non-forced rmmod,
  avoiding modprobe install/remove hooks and automatic dependency removal. Bound
  subprocess time/output and distinguish timeout from kernel completion. The
  persistent mask is fsynced before service commands; foreign unit files survive
  rejection. The tool never unsets the mask or starts the application.
- **Error observability:** preserve both errno and returned overlay ID, including
  zero-ID removal failures and lost response delivery. A STATUS command exposes
  the actual controller record after failed commands without claiming inhibition
  or electrical state. Faults remain latched even after retained-ID cleanup.
- **OF autoload race:** the final integration assessment identified that a new
  endpoint's uevent could autoload the consumer before the administrator's fixed
  insmod step. Removed only the opt-in build's autoload alias while retaining its
  explicit driver match table and the default build's aliases. Rebuilt both
  variants and asserted the distinction in their actual compiled modinfo; reran
  the full offline suite. No automatic consumer start is part of this interface.

## Reassessment

The second source assessment followed success, failed apply, pre/post-removal
error, copy-to-user failure, controller/consumer lifetime, stale request, busy
operation, init/unload failure, lost journal write, interrupted load/unload,
reboot and identity substitution paths. No remaining actionable finding was
identified within this offline development scope. Unrestricted root interference,
unknown external overlay consumers and timing/electrical behavior remain explicit
operational exclusions or unvalidated target properties, not passed assertions.
An additional assessment after the autoload correction found no further actionable
finding in the delivered scope. The refreshed evidence supersedes the initial
implementation commit's module hashes.

The full offline suite passed after repairs: 36 registered Python checks, one
parameterized utility classification and nine host C tests. The new controller
check contains 15 test methods and compiles/runs the actual controller ioctl
handler against mocked kernel APIs. It covers both route directions, the
consumer interlock, fault/ID outcomes, retained references, malformed/stale/busy
requests, actual ioctl encoding, persistent mask and journal behavior, and crash
injection at every instrumented userspace journal/effect boundary in initial
selection and route replacement. Existing 21 model methods and 10 read-only
collector methods also pass. Documentation links, SPDX, schemas, shellcheck and
whitespace checks pass. No target test client was run.

Both opt-in modules and the separate clean default consumer build pass against
6.18.34+rpt-rpi-2712 headers on aarch64 with GCC 14.2.0 (Debian 14.2.0-19).
Metadata inspection confirms the opt-in consumer marker and controller dependency
and their absence from the default build. Config/header/source/artifact hashes
are in the [build evidence](../evidence/runtime-controller-build-20260831.json).
The official header archives were downloaded over HTTPS and hashed; signed
repository metadata was not independently verified. Builds ran inside a disposable,
network-disabled local container with no target or hardware devices passed in.
Build compatibility does not qualify target loading or route switching.

## Exit gate

Implementation is ready for review as an opt-in development change, not a product
release. The [target plan](../operator/runtime-controller-target-plan.md) requires
fresh read-only deployment preflight, exact artifact/configuration review,
separate authorization for installation and service changes, and separate approval
of any migration reboot. Actual GPIO4/GPIO20 switching, safe cleanup, crash
recovery under target timing and electrical inhibition remain unproven. Normal
application admission, transmission and RF are outside the gate.

No installation, target endpoint access, target services, modules, overlays,
boot files, GPIO, DMA, reboot, transmission or RF state were changed. No merge,
release or PR #6 scope expansion is part of this implementation. License impact
is documented in the [controller contract](runtime-controller-v1.md).
