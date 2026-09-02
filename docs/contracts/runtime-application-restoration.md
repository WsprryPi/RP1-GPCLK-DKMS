<!-- SPDX-License-Identifier: MIT -->

# Runtime application restoration

The runtime manager completes application restoration after successful route
switching. The low-level overlay transaction ends at `complete-inhibited`;
it does not itself start an application.

## Ownership and sequence

DKMS owns overlay/consumer lifecycle, its transaction journals, and temporary
service inhibition. WsprryPi supplies the installed companion
`/usr/local/lib/wsprrypi/route_application.py`, configuration semantics, idle
startup handling, and application readiness acknowledgement. The kernel UAPI,
compatibility checks, and release/qualification status are unchanged.

The privileged manager captures prior service state and a unique startup token
in `application.json` before stopping anything. A workflow lock excludes other
mutating manager requests throughout restoration. The existing controller lock
is released before starting WsprryPi so startup queries can acquire it.

Filesystem deployment also captures the pre-inhibition service state and exact
companion observation in its reviewed version-2 deployment plan. The neutral
activation transaction reuses the same owned inhibitor, service observation,
companion validation and administrator-mask rules. It never calls the
route-specific configuration operation, creates an idle-route token or invents
GPIO4/GPIO20. Neutral restoration is admitted only when `Operation.Transmit` was
already false. A previously active service is started and must be active with a
nonzero PID; a stopped service remains stopped, and an administrator mask remains
masked. The companion is rechecked and must still report `transmit=false`.

The route-specific `application-ready` acknowledgement is intentionally not
forged for neutral activation: there is no consumer or selected route to
reconcile. Neutral readiness instead proves controller route zero, consumer and
endpoint absence, exact service intent, and the companion's disabled application
configuration. A later explicit route transaction creates the existing
route-specific token and acknowledgement.

The owned `90-rp1-route-inhibit.conf` service drop-in adds an unsatisfiable
`ConditionPathExists` below `/dev/null`. It prevents normal starts/restarts
without replacing `/etc/systemd/system/wsprrypi.service`. An existing service
unit or administrator mask is never overwritten. This is cooperative systemd
inhibition, not isolation from privileged processes or alternative units.

After normal consumer unload and controller-owned overlay removal/application,
the consumer is loaded with `live_output=0`. A passive snapshot must confirm
the selected route is idle. Only then does the companion atomically update
`GPIO.Transmit Pin` and `Operation.Transmit=false`. It preserves other settings,
including `Enable on Boot`, comments and file mode. The canonical installed
service command/configuration is checked before effects. Missing services,
unsupported commands and old application builds require installation repair;
they are not silently replaced.

An owned `91-rp1-route-idle.conf` supplies the startup-only
`WSPRRYPI_ROUTE_RESTORE_IDLE` token. WsprryPi overrides automatic transmission
for that startup, leaving its saved boot preference unchanged. The manager
removes its inhibition, reloads systemd, closes the controller lock, then starts
only a previously active service. Startup reconciliation and application loop
setup, startup quiescence and network reconciliation must succeed, and any
configured HTTP listener must be bound, before WsprryPi sends `application-ready` with the selected
route, token, PID and `transmit=false`. The manager checks the current service
PID, controller identity and idle snapshot before recording completion.

The normal operator transmission controls remain available after restoration;
no prior transmission or scheduler request is resumed by this workflow. Existing
RP1 operation authorization and cleanup behavior remain unchanged.

## Durable outcomes and recovery

`query` includes the durable application transaction alongside the current
controller observation. Application phases distinguish:

- `restored`: the application acknowledged idle readiness, including a later
  explicit first start of a previously stopped application.
- `stopped`: the application was stopped and was not started.
- `administrator-masked`: an existing administrator mask was preserved.
- `restoration-failed`: the route transaction completed, but application
  configuration, startup or readiness failed.
- `route-failed`: the route transaction failed; its original errno and overlay
  ownership remain available separately from any subsequent inhibition error.
- `route-recovered`: explicit recovery reached a neutral route; a new switch is
  needed before restoring application availability.

Completed records describe the last transaction, not a promise that the service
cannot subsequently stop. A stopped/masked application's idle startup override
remains until its first later startup acknowledges readiness. This avoids an
`Always` boot preference unexpectedly transmitting on that first start.

`runtime_route_client.py restore --execute` retries only application completion
on the same boot, deployment and successfully installed route. It does not
repeat overlay effects. Interrupted route changes require `recover --execute`,
then a new explicit switch. Recovery preserves the original service intent on
the same boot. Prior-boot restoration never automatically starts an application
or adopts stale overlay ownership; recover and explicitly select a new route.

Failures retain owned inhibition where possible and report inhibition failure
separately. Foreign drop-ins are preserved and reported. Requester disconnects
do not kill the independently systemd-owned manager worker; durable results
remain queryable. No successful application restoration is reported merely
because systemd accepted a start request.

Neutral activation failures retain `activation.json` and re-establish the same
owned inhibitor. Recovery requires its reviewed journal digest. A recovered
transaction remains inhibited but retains the original application intent for a
subsequent reviewed activation or coherent deployment. Prior activation evidence
is archived before a recovered transaction is restarted.

After a clean reboot, a valid terminal neutral journal can be superseded only by
a reviewed post-reboot activation. The current service state and disabled
companion configuration are captured as the new restoration intent. Execution
writes and verifies the owned inhibitor and stops the application before it
archives the old journal or loads the controller. If inhibition is interrupted
after the service stops, the still-terminal prior journal plus exact inhibitor
permits a newly reviewed retry. A running service behind an inhibitor, changed
service intent, or nonterminal prior-boot journal remains a stop condition.

The installer-facing runtime-provider contract classifies a failed restoration
as `recovery_required` and directs the caller to `restore --execute`; it never
converts a route-only success into application readiness.

Runtime-controller removal must reconcile the owned application inhibitor
before discarding the runtime inventory or journals. If an interrupted or older
removal has already left only the exact owned inhibitor, use
`scripts/runtime_inhibitor_cleanup.py inspect` to obtain a reviewed plan. The
cleanup operation is eligible only when the canonical WsprryPi service and all
fixed runtime-controller bindings, tools, journals, loaded modules, and endpoints
are absent. DKMS-installed module files are provider-owned prerequisites rather
than runtime-deployment residue and do not block this orphan-inhibitor cleanup.
Execution requires the unchanged plan digest and
removes only the exact root-owned regular file with the canonical bytes and
mode. Foreign overrides or any ambiguous runtime state remain untouched.

Review and execute the cleanup as two separate operations:

```sh
sudo python3 scripts/runtime_inhibitor_cleanup.py inspect
sudo python3 scripts/runtime_inhibitor_cleanup.py cleanup --execute \
  --plan-sha256 REVIEWED_PLAN_SHA256
```

The second operation re-inspects the machine and refuses cleanup if the
reviewed plan digest no longer describes the current state. It reloads systemd
after removal and restores the exact inhibitor if that reload fails.

## Deployment and validation boundary

Install the companion and matching WsprryPi executable using the application's
installer or `scripts/copy_exe.py`. Deploy a newly bound complete DKMS runtime
bundle: the inventory includes `runtime_application.py` and the manager's
sandbox permits the canonical application configuration directory. Do not swap
individual scripts under an incomplete binding. The application requires
`applicationRestoration: true` from the manager before offering a successful
runtime preflight.

Bundle construction also requires the exact WsprryPi companion path as an input.
The companion remains application-owned and is not installed by DKMS, but its
bytes are bound and reverified before runtime effects. This makes a companion
update a new deployment identity rather than an in-place script substitution.

An old `/dev/null` service mask is not automatically adopted as workflow-owned.
Restore the canonical service installation and intentionally clear that legacy
mask during coherent deployment. The software cannot infer whether that mask
is now an administrator's desired state.

Offline tests exercise public manager dispatch, real temporary journals and
drop-ins, fake systemd/kernel effects, interruption at durable journal boundaries,
error retention, startup lock ordering, stale acknowledgements, configuration
preservation and startup policy. They do not qualify systemd behavior, kernel
overlay removal, GPIO, RF or exact-target deployment.

Separately authorized target validation should start with coherent identities,
`GPIO20` and output disabled. Check running/stopped service restoration, `GPIO20` to
`GPIO4` to `GPIO20` switching with no output, deliberate restart failure and explicit
restoration, service/unit preservation, and final `GPIO20` idle state. Record route,
service PID/readiness, configuration, clock/DMA quiescence and both journals.
Do not resume transmission or infer RF qualification from these tests.
