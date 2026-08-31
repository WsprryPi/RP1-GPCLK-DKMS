<!-- SPDX-License-Identifier: MIT -->

# Runtime controller implementation prompt

Implement the next offline development slice on a separate branch based on the
PR #6 research/tooling foundation. Preserve that PR's scope and all existing
work. Read the module, lifecycle, route and source-review contracts first.

Deliver an opt-in controller using exported stock-kernel overlay APIs, never
configfs deletion, broad dtoverlay replay, raw MMIO or arbitrary caller DTBOs.
Embed only the two canonical source-built overlays. Keep overlay IDs and actual
apply/remove errors in kernel-owned state, including partial apply and removal
errors after the kernel has cleared the ID. Refuse a successor after uncertainty;
retain retryable removal ownership and latch faults without inventing success.
Retain controller lifetime while ownership or unresolved faults exist.

Provide a bounded versioned root-only administration interface with session and
generation checks, observational status, and fixed route choices. Interlock the
matching opt-in consumer for its complete module lifetime. Reject output-enabled
consumer loads and removal while the consumer is present. Preserve the existing
default build, canonical transmission UAPI, package manager and release path.
No default installation, firmware-route adoption or transmission is authorized.

Implement concrete userspace administration with fixed effects, persistent
application inhibition before effects, journal-before-effect ordering, explicit
same-boot recovery, and actual controller readback. Never auto-resume after reboot,
automatically release inhibition, force unload, or hide uncertain results behind
rollback. Failures leave application admission inhibited. Document the cooperative
root-administration boundary and the supported application service entry points.

Validate real implementation paths offline, including malformed requests,
concurrency/admission rejection, partial apply, retained-ID removal failures,
cleared-ID errors, stale sessions/generations, journal crashes, inhibition and
command construction. Compile against identified Linux headers if available;
record compiler/configuration/build identity and distinguish compilation from
hardware evidence. Run the repository suite, documentation/link and whitespace
checks. Conduct a separate adversarial assessment, repair actionable findings,
and repeat affected tests and assessment until clean within the delivered scope.

Prepare a separate exact-artifact deployment and clock-disabled validation plan.
Do not execute it: installation, service changes, module/overlay operations,
GPIO, migration reboot and target tests require separate user authorization.
Require route-neutral boot migration where firmware owns the current route;
prove both switch directions and failure cleanup independently with output
disabled. No RF or transmission belongs to this gate. If target or build evidence
cannot be obtained, name the limitation rather than promoting offline evidence.

Commit and push only attributable reviewed changes. Do not merge, publish a
release, change PR #6, or imply hardware readiness. Report implementation,
validation, remaining gates, licensing and Git state.
