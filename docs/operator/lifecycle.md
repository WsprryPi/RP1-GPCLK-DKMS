<!-- SPDX-License-Identifier: MIT -->

# Output-disabled DKMS lifecycle

## Frozen Phase 5.3 installation model

`release/installation-model-v1.json` is authoritative for installed paths,
ownership, modes, replacement rules, transaction order, and implicit-action
prohibitions. Frozen `0.0.0-phase5.2` is the predecessor; changed
blocker-resolution source has the distinct `0.0.0-phase5.18` successor
identity. Neither identity is published.

`rp1-gpclk-admin plan` is read-only. Installation requires the explicit
`install --execute --release-directory RELEASE --route gpio4|gpio20` form and
a publishable, checksum-valid release. It writes a private transaction journal
before dispatching any DKMS command. A failure remains
`inactive-recovery-required`, with module loading and overlay activation not
performed and live output false. `status` does not repair or mutate state.
`recover` deliberately refuses generic automatic repair: recovery must first
classify the recorded checkpoint and verify every package-owned byte.

Installation copies only the selected DTBO; it does not activate it or edit
boot configuration. It never creates `/etc/rp1-gpclk-dkms/enrollment.json`.
Key enrollment, overlay activation, and reboot are separately reported
administrator actions. Existing configuration, enrollment, keys,
certificates, overlays, and unmarked boot entries remain administrator- or
third-party-owned.

## Administrative route changes

`release/overlay-contract-v1.json` freezes the two distinct production overlay
identities. Exactly one may be selected at a time. There is no arbitrary GPIO
parameter, combined overlay, hot mutation of a bound route, or automatic route
substitution. Conflict inspection occurs before any persistent write.

`rp1-gpclk-admin route-change-plan --snapshot SNAPSHOT --route gpio4|gpio20`
is read-only. It accepts only a complete fail-closed snapshot and emits the
seven controlled gates: prove idle; disable live eligibility; remove the old
binding through the proven cleanup path; verify both pins safe; select the new
overlay; revalidate the complete compatibility identity; and renew enrollment
when policy requires it. It does not edit boot configuration or operate an
overlay. GPIO4 qualification and enrollment never transfer to GPIO20, or vice
versa.

Phase 5.2 packages the module for representative lifecycle validation. It does
not make an operator release, enable output, or qualify another target. The
only supported lifecycle gate in this phase is `live_output=0`.

## Permissions, enrollment, and live eligibility

`release/permissions-enrollment-policy-v1.json` freezes five independent
states: installed, available, enrolled, live eligible, and active. The device
node remains a root-owned `0600` character device. No udev group grant or other
non-root shortcut is installed; such access requires a separate reviewed
authorization design.

Experimental enrollment is an explicit root-administrator record for one exact
release, UAPI, module, kernel, DT, firmware, overlay, signer, compatibility
manifest entry, and route. Any identity change makes it stale, and revocation
is explicit and durable. A previous custom-kernel installation is not an
enrollment source. Qualified identities do not require Experimental-risk
acceptance, but still require deliberate route selection and ordinary operator
authorization. Enrollment, availability, and live eligibility do not acquire
the device; active means exactly one current owner.

## Preconditions

Use a stock Raspberry Pi kernel, its exact running-kernel headers, DKMS,
`device-tree-compiler`, OpenSSL when local signing is required, and root only
for registration, installation, loading, overlay installation, and removal.
Verify the complete release directory and its checksum/provenance sidecars
before extraction:

```sh
scripts/validate_release.py RELEASE_DIRECTORY
```

Development output is intentionally non-publishable and requires the explicit
`--allow-development` validation flag. Never use that flag for installation.

The archive contains no signing private key. Keep an administrator signing key
outside the source tree with restrictive permissions. A valid signature proves
provenance and load eligibility, not behavioral safety or qualification.

## Lifecycle

Run `scripts/rp1-gpclk-lifecycle.sh preflight SOURCE`. Then use the explicit
`add`, `build`, `install`, and `load-disabled` actions. `load-disabled` always
passes `live_output=0` and verifies the immutable parameter. `status` reports
the exact package/version and gate state. The optional `sign` action signs only
the installed module using explicit key and certificate paths and then reports
its signature metadata.

Build overlays into a new disposable directory with `overlay-build`. Install
only `gpio4` or `gpio20` with `overlay-install`; the tool refuses arbitrary
routes and will not overwrite a different artifact. It never edits boot
configuration, enables an overlay, or reboots. Runtime application/removal and
boot configuration remain separately reviewed target procedures.

For upgrades and downgrades, retain the current source/package until the new
version has passed add, build, signing-policy checks, install, output-disabled
load/status, unload, and cleanup. Version ordering does not imply compatibility
or qualification. On successor failure, remove only the failed successor and
reinstall the retained prior version. Do not weaken identity or signing policy
to make an update succeed.

## Recovery and removal

Rollback, recovery, and complete removal are separate operations. Rollback
restores the immediately prior recorded complete release after a failed
successor, but only while its targets and administrator bytes remain unchanged.
Recovery classifies one interrupted transaction and either resumes a proven
checkpoint or converges to an inactive state. Complete removal removes all and
only exclusively package-owned state and then audits absence, restored hardware
baselines, dependency metadata, key ownership, and preserved unrelated bytes.

`lifecycle-policy rollback-plan SNAPSHOT`, `recovery-plan SNAPSHOT`, and
`removal-audit SNAPSHOT` are read-only. Their exact input and acceptance fields
are frozen in `release/lifecycle-removal-contract-v1.json`. They do not invoke
DKMS, change boot files, unload a module, repair state, or remove files. A false,
unknown, missing, or extra assertion fails closed.

Unload before DKMS uninstall. Use `uninstall`, then `remove`, and remove
`/usr/src/rp1-gpclk-dkms-VERSION` only after `dkms status` proves the version is
absent. Remove an installed overlay only when its hash matches the retained
package artifact and it is neither applied nor referenced by marked boot
configuration. Repeated absence is success; a mismatched file is an operator
decision, not tool-owned residue.

After recovery or removal verify: no loaded module, device node, bound platform
device, runtime overlay, package/version DKMS row, or unexpected dmesg warning;
GPCLK0 prepare and enable counts are zero; GPIO4 and GPIO20 are input/none; and
the output gate was never enabled. Cleanup failure leaves the combination
`Rejected` or `Unavailable` until investigated.

Complete removal additionally proves no open endpoint or owner, active work,
callback or DMA; the selected pin is safe; clock prepare/enable counts and
parent match the recorded baseline; no production overlay or owned boot marker
remains; all DKMS registrations, builds and installed module files are absent;
package udev, systemd, manifest, configuration, diagnostic and other residue is
absent; dependency metadata and initramfs are current where applicable; and
unrelated bytes are preserved. Administrator/shared signing keys are retained.
An exclusively package-created private key is removable only with an explicit
nonshared ownership record. An open descriptor, active work, cleanup latch, or
unproven state rejects removal; no forced teardown is permitted.

## Gate D lifecycle coordinator

`gate-d-instance` validates the concrete
`release/gate-d-execution-instance-v1.json` against the frozen 15-row matrix.
The checked-in instance records the approved `wspr5` output-disabled mutation
envelope, its two installed stock kernels, both independent routes, deadlines,
and the validated `wspr5-rescue` SD-before-NVMe recovery path. Successor
`0.0.0-phase5.18` is selected but not yet frozen. The single-Pi execution policy
keeps five unavailable environmental rows explicitly deferred rather than
simulated. Read-only route discovery plus the exact predecessor/current,
predecessor/prior, and successor/prior builds supply all ten
required-executable identities, but the target plan lacks executable command
arrays and per-attempt operation documents. `inputsReady: false` and
`executionReady: false`; fresh authorization remains recorded. Deferred rows
also continue to block complete environmental coverage and publication.

`inputsReady` and `executionReady` are separate. The former covers exact
required-executable inputs; the latter additionally requires a fresh explicit
target-execution release. The target-operation plan and exact execution-tool
identities are hash-bound by the execution instance; a difference is not
authority to improvise a replacement command.

The execution instance is repository evidence, not package content. It is
excluded from the candidate source archive and installation because it contains
host-specific authorization and can name the sealed archive only after that
archive exists. The generic schema, validator, coordinator, and probes are
package artifacts; the separately sealed instance is supplied at execution.

`gate-d-lifecycle validate OPERATION` and `plan OPERATION` are offline and
read-only. Actual dispatch requires root plus all of `execute --execute`, a
fresh journal path, and a fully ready execution instance. Before dispatch the
coordinator binds the operation to the exact matrix row, host, kernel, route,
deadline, unique attempt evidence directory, and frozen successor version.
Existing journals are immutable. The explicit `recover` operation reads a
matching failed journal but writes a distinct recovery-attempt journal, so the
failed evidence is never replaced.

The coordinator implements output-disabled load, parameter verification,
UAPI QUERY/ACQUIRE/RELEASE without submission, explicit unbind/rebind, unload,
upgrade, downgrade, rollback, checkpoint recovery, exact-version uninstall,
removal of a declared test-version set, complete removal of only digest-bound
owned paths, repeated removal with exact DKMS absence verification, and
reinstall after proved removal. Every external command has the row deadline.
Interruption leaves `inactive-recovery-required`; a changed owned byte refuses
removal. An ordinary upgrade or downgrade failure automatically removes the
failed successor and restores the retained predecessor; a rollback failure
remains recovery-required. A removal request with an exact open/active blocker
is recorded as `installation-retained` without dispatching a mutation command.
Final removal independently checks every named DKMS version plus runtime,
endpoint, binding, and owned-path absence. Each command record includes its
deadline, UTC and monotonic timing, exit status, and bounded combined output.

`gate-d-uapi-probe` rejects a route, build, ABI, module ID, or
`LIVE_ELIGIBLE` mismatch and never submits work. `gate-d-platform` requires
exactly one bound device and verifies `live_output` disabled both before and
after explicit unbind/rebind. A route must already have been selected through
the separately reviewed inactive overlay procedure; the operation safety
snapshot requires `routeSelectedInactive: true`.

The coordinator is executable tooling, not target evidence. A green offline
test cannot change a row from `blocked-input-required`, freeze a candidate,
authorize target work, or prove installation, cleanup, timing, GPIO, DMA,
transmission, SDR, or RF behavior.

The ordered target procedure and current hard stop are recorded in
`gate-d-target-runbook.md`.

## Persistent prohibitions

There is no custom-kernel, `/dev/mem`, raw userspace MMIO, arbitrary-route, or
alternate-transmitter fallback. Unknown hardware, kernel, DT, signing,
resource, route, UAPI, artifact, or cleanup identities fail closed. Phase 5.1
does not authorize GPIO output, transmission, RF, boot changes, or reboot.
