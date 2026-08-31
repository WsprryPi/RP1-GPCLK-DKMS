<!-- SPDX-License-Identifier: MIT -->

# Runtime manager software workflow

This is an opt-in, clock-disabled development profile, not a qualified release.
The packaged manager and source-development profile remain unchanged. The new
`95-runtime-controller.conf` selects the runtime manager on the same privileged
socket; schema 3 and contract `rp1-gpclk-route-manager-runtime-v1` distinguish it
from both existing profiles. Only legacy **query** is accepted for discovery.
Legacy reboot and reconciliation requests are never translated into switching.

The companion WsprryPi branch `codex/runtime-route-workflow` discovers this
profile, sends explicit runtime preflight/switch/recover requests, and keeps its
transmission inhibit asserted. The browser warns that switching stops and masks
WsprryPi. A disconnected HTTP request means **completion unknown**, not success.
Use the operator client for subsequent administration while the app is stopped.
No tool here restarts or unmasks the application. This is deliberately not a
continuously available browser-only workflow.

## Build and review offline

Build the opt-in modules using the controller contract's exact-kernel procedure.
Then run:

```sh
python3 scripts/build_runtime_bundle.py COMPILED_MODULE_DIRECTORY NEW_BUNDLE_DIRECTORY
```

The builder checks ELF64/kernel identity, the consumer interlock marker and
controller dependency, build notes, and the exact canonical DTBO bytes embedded
in the controller. The binding covers both modules, private copies of both UAPIs
and DTBOs, manager/admin/client/deployment/layout Python files, and the systemd
drop-in. Private copies do not replace the package's canonical UAPI or overlays.
The bundle is a local review artifact, not a signed or published release. Review
and checksum the entire bundle, including its bootstrap Python files, before
transferring or executing it with privilege.

## Separately authorized deployment window

These steps describe future target operations; they were not executed during
software validation. Explicit authorization must name the target, exact bundle,
module/UAPI/kernel identities, intended route, application downtime and recovery
plan. Keep clocks and transmission disabled throughout.

1. Establish a neutral window with **neither module loaded**. The installer does
   not unload modules, modify firmware configuration, or reboot. A firmware route
   may require one separately reviewed migration reboot before controller
   activation. Do not equate current-boot adoption with removable ownership.
2. Provision root-owned, non-group/world-writable
   `/var/lib/rp1-gpclk-dkms/runtime-admin` and its ancestors. Review the existing
   socket/service installation. The installer preserves packaged executables and
   the source-development drop-in, and does not create or enable the socket.
3. From the reviewed bundle, run `python3 runtime_deployment.py plan --bundle .`.
   Review the old/new hashes and destinations. Existing files must be ordinary,
   root-owned 0644 files; compressed/alternate module resolution is not silently
   replaced. Resolve such a conflict through a separately reviewed migration.
4. Execute that exact plan with
   `python3 runtime_deployment.py install --bundle . --plan-sha256 DIGEST`.
   The tool journals old/new bytes, masks/stops WsprryPi, writes files atomically,
   refreshes depmod/systemd, and leaves the application masked. It never activates
   a module. A pending deployment blocks all runtime-manager requests.
5. Separately authorize controller activation from the bound module path, only
   with a neutral firmware tree. Use the existing socket's operator client:
   `python3 /usr/lib/rp1-gpclk-dkms/runtime_route_client.py query`, then an explicitly
   authorized `switch gpio4 --execute` or `switch gpio20 --execute`.

Before an update, use explicit controller recovery to reach no route, then
separately unload the neutral modules. Only a `recovered-inhibited` journal with
zero overlay ID is eligible for update. The deployment journal retains prior
route/manager journals while clearing them for the new binding. It never adopts
an old session into a new controller session.

For an interrupted filesystem deployment, first run
`python3 runtime_deployment.py recover` to obtain the recovery digest, then repeat
with `--plan-sha256 DIGEST`. Recovery restores the exact recorded old bytes only
if every destination still equals its recorded old or new content. Foreign changes
block the entire restoration. The application remains masked. This does not undo
kernel effects or clear a controller fault. Preserve deployment records and failed
controller observations for investigation; never delete them to bypass a check.

## Remaining proof

Offline tests cover software behavior with injected effects. The target still
requires coherent installation and service-sandbox validation, exact module
resolution and signing checks, firmware migration assessment, clock-disabled
GPIO4 and GPIO20 round trips, removal-error/ownership checks, crash recovery,
consumer exclusion, and independent confirmation that clocks remain disabled.
Subsequent rebootless switching is implemented but not yet proven on hardware.
No GPIO4 readiness, transmission, timing, interference, or RF qualification is
claimed. Restoring application/output operation is a separate gate.

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
