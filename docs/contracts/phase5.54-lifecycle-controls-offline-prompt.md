<!-- SPDX-License-Identifier: MIT -->

# Phase 5.54 lifecycle-controls offline prompt

Construct one qualification-only control bundle for output-disabled lifecycle
attempt 1 from the literal Debian-installed closure recorded at commit
`c5f278cccb2398875198e1d7d2e7727aee757a7f`. Do not modify the product
package or reuse and patch the Phase 5.53 archive control graph.

Bind the exact `-2` package digest, running stock kernel, installed UAPI,
canonical GPIO4 overlay, inactive boot copy, module version, and clean inactive
state. Limit attempt 1 to GPIO4: compile the bounded query/acquire/release probe
from the installed UAPI, load the module with `live_output=0`, apply only the
GPIO4 runtime overlay, prove live eligibility remains absent, release the
endpoint, remove only the attempt overlay, unload, and restore the exact
inactive baseline. Capture the runtime overlay identifier rather than guessing
it. Fail closed with overlay removal followed by unload as the recovery order.

The bundle must contain only the plan, a validator/command renderer, and probe
source. Build it twice byte-identically and inspect its literal member list.
Exercise validation and rendering offline. Do not include an execution entry
point or contact `wspr5` in this slice.

Do not install qualification tooling; load a module; apply an overlay; change
boot state; reboot; enable GPIO, clock, or DMA output; transmit; or produce RF.
Target staging and lifecycle attempt 1 require a new digest-bound explicit
authorization after this bundle is committed, rebuilt, and reviewed.
