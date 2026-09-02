<!-- SPDX-License-Identifier: MIT -->

# Runtime manager software workflow

The opt-in runtime manager uses contract
`rp1-gpclk-route-manager-runtime` on the existing privileged Unix socket.
It supports rebootless `GPIO4`/`GPIO20` switching and explicit recovery to `none`.
Successful switching restores a previously running WsprryPi in idle state through
[application restoration](../contracts/runtime-application-restoration.md).
It never resumes transmission. This is an `Experimental` development profile;
the packaged manager and passive source-development profile are separate.

Profile discovery accepts only `query`; reboot and reconciliation requests from
other manager profiles are not translated into switching. WsprryPi owns browser
integration and operator confirmation. A disconnected request means completion
unknown: query the durable result with the operator client instead of repeating
an uncertain effect.

## Build and review offline

Install the exact source through `development-install --runtime-controller`; DKMS
must own exactly one consumer and one controller artifact for the running kernel.
Then point the bundle builder at that DKMS installation directory:

```sh
python3 scripts/build_runtime_bundle.py COMPILED_MODULE_DIRECTORY NEW_BUNDLE_DIRECTORY \
  --application-companion /usr/local/lib/wsprrypi/route_application.py
```

The builder reads compressed or uncompressed DKMS artifacts, checks ELF64/kernel identity, the consumer interlock marker and
controller dependency, build notes, and the exact canonical DTBO bytes embedded
in the controller. The binding covers the exact source commit, product and route
compatibility identities, both modules, private copies of both UAPIs and DTBOs,
all manager/admin/client/deployment/layout/readiness Python files, the readiness
schema, the socket/service units, runtime drop-in, and exact WsprryPi companion.
Private copies do not replace the package's canonical UAPI or overlays, and the
DKMS deployment does not install the application-owned companion.
The socket/service units are deployment payloads rather than unbound host
prerequisites. The application-owned companion is the only external file and is
bound by digest. The bundle is a local review artifact, not a signed or
published release. Review and checksum the entire bundle, including its
self-contained bootstrap Python import closure, before transferring or executing
it with privilege.

## Separately authorized deployment window

Explicit authorization must name the target, exact bundle,
module/UAPI/kernel identities, intended route, application downtime and recovery
plan. Keep clocks and transmission disabled throughout.

1. Establish a neutral window with **neither module loaded**. The installer does
   not unload modules, modify firmware configuration, or reboot. A firmware route
   may require one separately reviewed migration reboot before controller
   activation. Do not equate current-boot adoption with removable ownership.
2. Review the existing socket/service installation. The reviewed filesystem plan installs or updates
   the exact bound socket/service unit bytes, preserves conflicting packaged
   executables and the source-development drop-in, and does not enable or start
   the socket before neutral activation.
3. From the reviewed bundle, run `python3 runtime_provider.py plan --bundle .`.
   Review the classification, old/new hashes, destinations and `planSha256`.
   Existing files must be ordinary,
   root-owned 0644 files. Modules are external prerequisites: the plan never
   writes `/lib/modules`, and duplicate or mismatched module resolution fails
   closed rather than creating a shadow artifact.
4. Execute that exact plan with
   `python3 runtime_provider.py ensure --bundle . --plan-sha256 DIGEST`.
   Only after the supplied digest matches the reviewed plan, the tool creates
   missing fixed root-owned state ancestors and private mode-0700
   `/var/lib/rp1-gpclk-dkms/runtime-admin`. Existing symlinks, unsafe ownership,
   or group/world-writable directories fail closed. Planning never creates this
   hierarchy. The tool then journals old/new bytes, masks/stops WsprryPi, writes files atomically,
   refreshes depmod/systemd, and leaves the application masked. It never activates
   a module. A pending deployment blocks all runtime-manager requests.
5. Review and execute neutral activation. This loads only the bound controller,
   starts the exact manager socket infrastructure, verifies route zero and
   restores WsprryPi according to the service state captured before deployment:

   ```sh
   python3 /usr/lib/rp1-gpclk-dkms/runtime_provider.py activation-plan
   python3 /usr/lib/rp1-gpclk-dkms/runtime_provider.py activation-ensure \
     --plan-sha256 REVIEWED_ACTIVATION_PLAN_SHA256
   python3 /usr/lib/rp1-gpclk-dkms/runtime_provider.py inspect
   ```

   A reviewed bundle may also be supplied to `activation-plan` and
   `activation-ensure`; it must match the installed binding exactly. Successful
   inspection reports `neutral_ready`, `administrationCompatible=true`,
   `administrationEligible=true`, `routeSelected=false`, and
   `transmissionEligible=false`. The consumer stays unloaded, its endpoint stays
   absent, no overlay is applied and no reboot or output authorization occurs.
6. Only after a separate operator route decision, inspect and plan the exact route:

   ```sh
   python3 /usr/lib/rp1-gpclk-dkms/runtime_provider.py inspect \
     --requested-route gpio4 --configured-route gpio4 --persisted-route gpio4
   python3 /usr/lib/rp1-gpclk-dkms/runtime_provider.py route-plan --route gpio4 \
     --requested-route gpio4 --configured-route gpio4 --persisted-route gpio4
   python3 /usr/lib/rp1-gpclk-dkms/runtime_provider.py route-ensure --route gpio4 \
     --plan-sha256 REVIEWED_ROUTE_PLAN_SHA256 \
     --requested-route gpio4 --configured-route gpio4 --persisted-route gpio4
   ```

   `route-ensure` re-runs preflight and delegates the exact switch to the existing
   runtime manager. It neither authorizes output nor creates a parallel route path.

Before an update, use explicit controller recovery to reach no route, then use
neutral activation recovery to unload the exact controller and restore the
post-deployment inhibited state. Only recovered journals with zero overlay ID are
eligible for update. The deployment journal retains prior evidence while
clearing current route/manager/activation journals for the new binding. It never
adopts an old session into a new controller session.

For an interrupted or deliberately reversed neutral activation, retain the
inhibitor and journal, then run:

```sh
python3 /usr/lib/rp1-gpclk-dkms/runtime_provider.py activation-recover-plan
python3 /usr/lib/rp1-gpclk-dkms/runtime_provider.py activation-recover \
  --plan-sha256 REVIEWED_ACTIVATION_RECOVERY_SHA256
```

Recovery unloads only an exact neutral controller and stops the socket only when
the activation transaction started it. It does not remove an overlay, consumer,
foreign socket or administrator state. Boot change, a nonzero controller route,
fault, consumer presence or uncertain unload retains `recovery_required`.

For an interrupted filesystem deployment, first run
`python3 runtime_deployment.py recover` to obtain the recovery digest, then repeat
with `--plan-sha256 DIGEST`. Recovery restores the exact recorded old bytes only
if every destination still equals its recorded old or new content. Foreign changes
block the entire restoration. The application remains masked. This does not undo
kernel effects or clear a controller fault. Preserve deployment records and failed
controller observations for investigation; never delete them to bypass a check.

## Installer-facing readiness contract

`runtime_provider.py inspect` reserves stdout for one JSON document and sends
diagnostic failures to stderr. The schema is installed at
`/usr/lib/rp1-gpclk-dkms/schema/rp1-gpclk-runtime-readiness-v1.schema.json`.
The JSON document identifies the contract as
`rp1-gpclk-runtime-readiness-v1`.
Stable classifications and exit statuses are:

| Result | Exit | Meaning |
| --- | ---: | --- |
| `exact_ready` | 0 | Exact owned profile, one aligned route, restored or known-idle application, closed endpoint, disabled output and quiescent passive state |
| `absent` | 10 | No runtime binding, artifact, journal, module, endpoint or socket residue |
| `deployment_required` | 11 | The exact filesystem deployment is incomplete |
| `recovery_required` | 12 | A retained deployment, controller, route or restoration record requires its explicit recovery verb |
| `conflict` | 13 | Foreign, changed, mixed, unsafe, open, ambiguous or contradictory state requires reviewed remediation |
| `activation_required` | 14 | Exact runtime files are deployed and inhibited; explicit neutral activation remains |
| `neutral_ready` | 0 | Exact controller and manager administration are ready at route zero; no consumer or transmission eligibility exists |

The result includes installed and requested binding identities, source commit,
product/compatibility/kernel/UAPI/artifact hashes, deployment digest and journal,
requested/configured/persisted/active routes, module and endpoint observations,
socket and service state, application restoration, and passive live-output,
owner, lease, GPIO, clock and DMA state. Omitted consumer route inputs remain
`null`; callers should supply all three when deciding application eligibility.
An exact repeated `ensure`, `activation-ensure`, or `route-ensure` reports
idempotent readiness without repeating effects. Neutral idempotency does not
reload the controller, restart systemd, rewrite a journal, change the application
or allocate a new request/generation. Any identity drift is not the same
installation.

Systemd observations parse named `key=value` properties rather than depending
on output order. The manager service template is inspected through the fixed
inactive `rp1-gpclk-route-manager@runtime-inspect.service` instance name; this
does not start or enable an instance. Process identity is requested only for
the WsprryPi application service, whose restoration proof requires `MainPID`;
socket and template units are not required to expose a process identifier.

The low-level `runtime_deployment.py` and `runtime_route_client.py` commands remain
supported recovery/operator tools. Existing verbs are not renamed or removed.

## Application-installer integration

An application installer resolves the exact DKMS source or release and proves
its own ownership before recording runtime ownership. It then builds or selects
the bound bundle, calls `inspect`, reviews and executes `plan`/`ensure`, reviews
and executes `activation-plan`/`activation-ensure`, and requires a final
`neutral_ready` response. Installation can then finish with WsprryPi and its web
service available while no GPIO route or consumer exists. The route API should
render the DKMS readiness evidence directly and wait for a later operator choice;
only that confirmation permits `route-plan` and `route-ensure` for one route.

WsprryPi should extend its ownership record only after its successful calls with
a nested runtime identity containing the readiness contract, binding SHA-256,
artifact-set SHA-256, source commit, product version, target kernel,
compatibility identities, reviewed deployment and activation plan digests,
activation request ID, controller session/generation, neutral state, null route,
and disabled-output state. These fields record WsprryPi orchestration; they do
not transfer ownership of DKMS files, journals, modules, units or systemd state.

Runtime residue accounting must include `runtime_activation.py`, both character
devices, both loaded-module paths, the manager socket, both application drop-ins,
the complete `/var/lib/rp1-gpclk-dkms/runtime-admin` directory (including current
and prior activation journals and `last-deployment.json`), the binding, runtime
UAPIs/overlays/schema/scripts, runtime controller module artifact, manager unit
drop-in, and the package-owned socket/service units. Removal first uses exact
route recovery when applicable, then activation recovery, then the existing
binding-aware deployment/removal workflow. It never deletes the state directory
or a journal merely to bypass recovery.

For an exact deployment that stopped before neutral activation created any
activation journal, `runtime_provider.py remove-plan` returns the digest and
fixed destination inventory for the retained `last-deployment.json` inverse.
`remove --plan-sha256 DIGEST` is admitted only with absent modules, endpoints,
manager socket, route, and pending transaction. It restores every reviewed
predeployment byte and the captured application state, then removes only empty
fixed runtime directories. Digest drift, stacked deployment, active or foreign
state, and unexpected residue fail closed.

## Operator commands and recovery

Use the installed client after the runtime profile and its socket are deployed:

```sh
python3 /usr/lib/rp1-gpclk-dkms/runtime_route_client.py query
python3 /usr/lib/rp1-gpclk-dkms/runtime_route_client.py preflight gpio4
python3 /usr/lib/rp1-gpclk-dkms/runtime_route_client.py idle gpio4
python3 /usr/lib/rp1-gpclk-dkms/runtime_route_client.py reconcile-output gpio4
```

The following commands mutate target state and require the authorized window:

```sh
python3 /usr/lib/rp1-gpclk-dkms/runtime_route_client.py switch gpio4 --execute
python3 /usr/lib/rp1-gpclk-dkms/runtime_route_client.py switch gpio20 --execute
python3 /usr/lib/rp1-gpclk-dkms/runtime_route_client.py recover --execute
python3 /usr/lib/rp1-gpclk-dkms/runtime_route_client.py restore --execute
```

`switch` performs preflight, selects one route, and attempts application
restoration. `recover` reaches `none` with application inhibition retained;
there is no `switch none` command. Use recovery for an interrupted route change,
then explicitly switch. `restore` retries only application completion for a
successfully selected current route; it does not repeat overlay effects.
Previously stopped services remain stopped and administrator masks are preserved.

After reboot, load the reviewed controller and explicitly recover before
switching. A completely empty new controller can establish a current neutral
record; nonempty or faulted state is not silently adopted. Unknown completion,
removal errors, owner/lease presence, stale identities or cleanup faults are
stop conditions. Preserve the journals and investigate; never force unload,
delete a pending record or add a second overlay to hide uncertainty.

## Validation boundary

Offline tests use injected system effects. Exact-target validation separately
checks coherent module resolution and signing, neutral firmware migration,
both route round trips, removal errors, ownership, consumer exclusion, service
restoration, crash recovery and GPIO/clock/DMA quiescence. Tests of administration
do not establish waveform, timing, interference, product or RF qualification.

## Deployment admission and recovery bounds

Installation and recovery reject known-loaded modules before writing a pending
marker. Module absence is checked again immediately before and after stopping the
application. Once quiescence begins, any failure retains the durable barrier;
this ordering avoids creating a barrier for a known failed prerequisite while
preserving evidence of uncertain effects. These checks do not isolate the process
from independent administrator actions.

Bundle reads reject symlinks and non-regular members and enforce bounds while
reading. The installer validates the complete binding schema and uses the same
single metadata snapshot both to verify payloads and to install the binding.
Deployment journals must fit the 32 MiB recovery-reader limit, including old and
new bytes, before effects are permitted. A larger plan requires a separately
reviewed format/workflow change; it cannot be forced through this installer.

Runtime bundle builds require both `dtc` and `fdtput` from device-tree-compiler.
The runtime-private DTBOs retain canonical route content and fixups but omit
exported symbols; packaged firmware DTBOs are unchanged. This avoids
stock-kernel `/__symbols__` allocation warnings during runtime removal. Exact
transformed bytes remain embedded in and authenticated against the controller.

## Application output

Successful runtime switching uses the application-restoration contract above.
If only application readiness fails, use `restore --execute`. The low-level
`resume` operation is not a substitute for that configuration/startup handshake.
[Output reconciliation](../contracts/runtime-output.md) is observational;
UAPI acquisition and WsprryPi operator authorization remain separate gates.
The global load-time output gate stays disabled.
