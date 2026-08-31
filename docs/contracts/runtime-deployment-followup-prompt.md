<!-- SPDX-License-Identifier: MIT -->

# Runtime deployment follow-up execution prompt

Review the current PR #7 runtime integration and the separately pushed application
branch. Preserve existing work, exact artifact/route identities, package and
source-development compatibility boundaries, overlay ownership/error reporting,
application inhibition, and the separation of software from hardware evidence.

Inspect the concrete installer and its recovery paths before target deployment.
Fix actionable problems in precondition ordering, bounded bundle reads, consistent
binding snapshots, and durable journal limits. A known-loaded module must reject
an installation before a pending marker is written. After an effect begins,
failures must preserve the recovery barrier. Recheck neutral module state after
application quiescence, without claiming isolation from administrator interference.
Every journal the writer accepts must remain readable by recovery. Reject malformed
or oversized plans before filesystem/service mutation. Read bundle metadata once
and bind exactly those bytes to the verified payloads.

Add deterministic offline regressions for these failures, plus the existing
switch/recovery, ownership, replay and crash-boundary cases. Inspect all test
implementations before running them. Run the full offline suite and documentation,
SPDX and whitespace checks. Perform a separate adversarial assessment; repair every
actionable finding and repeat the affected checks until clean in this software
scope. Commit and push only attributable changes and update PR #7 evidence without
merging or publishing a release.

Do not install, load/unload/bind modules, alter target services or boot settings,
apply/remove overlays, change GPIO, reboot, or transmit. Produce a concrete next
authorization gate: exact target and boot inventory, reviewed bundle digest,
module/kernel/UAPI/signing identities, neutral-firmware migration plan, application
downtime, and clock-disabled GPIO4/GPIO20 tests with stop/recovery criteria. An
initial migration reboot needs its own reviewed boot diff and explicit approval.
Subsequent rebootless switching remains unproven until target testing. Report
checks, Git state, residual limitations and any still-required authorization.
