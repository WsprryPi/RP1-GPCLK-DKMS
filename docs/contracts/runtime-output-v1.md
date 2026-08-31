<!-- SPDX-License-Identifier: MIT -->

# Runtime route reconciliation for application output

The current schema-3 manager completes application restoration as specified in
[Runtime application restoration](runtime-application-restoration-v1.md). Its successful switch path
restores a previously running application in idle mode. Descriptions below of
unconditional manual mask release describe the earlier low-level workflow;
`restore --execute` is now the recovery command for application completion.

The runtime controller continues to own its overlay and exclude removal while
the consumer is attached. Neither its UAPI nor its consumer interlock changes.
The consumer remains loaded with `live_output=0`.

ABI v4 already supports operation-scoped live acquisition on this consumer.
Earlier documentation incorrectly described a disabled load parameter as a
technical prohibition on all output. The parameter blocks the global output path;
it does not disable ABI-v4 authorization. No new permit, duration cap, or mode
restriction is introduced here.

Schema 3 adds `idle` and `reconcile-output`, each with an explicit gpio4 or gpio20
route. Both are observational and return `executionAuthorized=false`. They require
a current boot/session/binding, a completed route journal agreeing with controller
readback, and a passive module snapshot reporting the selected route, eligible
compatibility, no owner/lease/live gate, no cleanup fault, and stable GPIO/clock/DMA
quiescence. Busy and unknown observations fail; kernel errors remain available.
The existing module acquisition closes the observation-to-acquisition race.

WsprryPi uses `idle` during startup without clearing its output inhibit. Its
existing development-operation path uses `reconcile-output` before checking the
operator confirmation and consuming its existing one-use application authorization.
The existing ABI-v4 lease, finite request, cancellation, owner-close cleanup and
terminal observation remain responsible for execution. Route reconciliation is
not itself output authorization or RF qualification.

`resume gpio20 --execute` verifies the same idle route and explicitly removes the
persistent application mask. It does not start the service or enable output.
The operator starts the application after the manager request has returned; this
avoids startup reconciliation waiting on a manager lock held by its own starter.
A failed reload attempts to restore inhibition. Switching and recovery still stop
and mask the application, use non-forced consumer unload, and preserve overlay
removal errors. An open consumer file blocks unload. No previous transmission is
resumed automatically.

## Coherent update procedure

Build WsprryPi from the reviewed companion commit. Build a runtime bundle using
`scripts/build_runtime_bundle.py` and the exact existing interlocked modules
when their code and embedded overlays are unchanged; otherwise rebuild them.
Preserve installed application/module/manager bytes and route/deployment journals.
Use the existing manager to recover to no route, unload the neutral controller,
and use the new bundle's `runtime_deployment.py plan/install` workflow. Its digest
binds every installed manager/module/UAPI/overlay byte; do not swap only one script.
Load the checked controller, select GPIO20 through the runtime client, and verify
`idle gpio20`. Install the companion binary using WsprryPi's existing
`scripts/copy_exe.py`, preserving the stopped service state. Update the served UI
from the same source if that deployment still predates the companion UI changes.
Then explicitly resume the application mask and start the service.

A failed update uses the existing deployment journal recovery while modules are
unloaded. A failed route operation keeps its ID/error and requires explicit
recovery. Preserve target evidence, including any failed operation, and do not
claim output success from compilation or idle reconciliation alone.

After a reboot, load the reviewed controller and use explicit `recover --execute`
before switching. If its new state is completely empty, recovery archives the
previous boot's journal and establishes a current neutral record. A nonempty or
faulted controller is not adopted through this path. Recovery leaves output
disabled and the application masked.
