<!-- SPDX-License-Identifier: MIT -->

# Runtime route reconciliation for application output

The runtime manager completes application restoration as specified in
[Runtime application restoration](runtime-application-restoration.md). Its successful switch path
restores a previously running application in idle mode. `restore --execute`
retries application completion after a successful route transaction.

The runtime controller continues to own its overlay and exclude removal while
the consumer is attached. Neither its UAPI nor its consumer interlock changes.
The consumer remains loaded with `live_output=0`.

The canonical UAPI supports operation-scoped live acquisition on this consumer.
The load parameter blocks the global output path;
it does not disable operation-scoped authorization. No new permit, duration cap, or mode
restriction is introduced here.

The runtime manager supports `idle` and `reconcile-output`, each with an explicit `gpio4` or `gpio20`
route. Both are observational and return `executionAuthorized=false`. They require
a current boot/session/binding, a completed route journal agreeing with controller
readback, and a passive module snapshot reporting the selected route, eligible
compatibility, no owner/lease/live gate, no cleanup fault, and stable GPIO/clock/DMA
quiescence. Busy and unknown observations fail; kernel errors remain available.
The existing module acquisition closes the observation-to-acquisition race.

WsprryPi uses `idle` during startup without clearing its output inhibit. Its
existing development-operation path uses `reconcile-output` before checking the
operator confirmation and consuming its existing one-use application authorization.
The existing UAPI lease, finite request, cancellation, owner-close cleanup and
terminal observation remain responsible for execution. Route reconciliation is
not itself output authorization or RF qualification.

The low-level `resume gpio4|gpio20 --execute` checks the idle route and releases
owned inhibition without starting the service or authorizing output. It is not
the application-restoration handshake. Normal runtime switching performs that
handshake itself; use `restore --execute` if application completion fails.
An open consumer file blocks unload. Removal errors and unresolved transactions
remain visible, and no previous transmission is resumed automatically.

## Coherent update procedure

Use the [runtime deployment workflow](../operator/runtime-manager-workflow.md)
with a complete newly bound bundle and matching WsprryPi companion. Keep module,
manager, UAPI, overlay and application identities coherent; do not swap scripts
under an old binding. The [application restoration contract](runtime-application-restoration.md)
defines startup readiness and preservation of service/configuration state.

A failed update uses the existing deployment journal recovery while modules are
unloaded. A failed route operation keeps its ID/error and requires explicit
recovery. Preserve target evidence, including any failed operation, and do not
claim output success from compilation or idle reconciliation alone.

After a reboot, load the reviewed controller and use explicit `recover --execute`
before switching. If its new state is completely empty, recovery archives the
previous boot's journal and establishes a current neutral record. A nonempty or
faulted controller is not adopted through this path. Recovery leaves output
disabled and the application masked.
