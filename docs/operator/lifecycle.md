<!-- SPDX-License-Identifier: MIT -->

# Output-disabled DKMS lifecycle

## Frozen Phase 5.3 installation model

`release/installation-model-v1.json` is authoritative for installed paths,
ownership, modes, replacement rules, transaction order, and implicit-action
prohibitions. The package keeps the exact `0.0.0-phase5.2` candidate identity;
the Phase 5.3 slice number is not a release-version promotion.

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

## Persistent prohibitions

There is no custom-kernel, `/dev/mem`, raw userspace MMIO, arbitrary-route, or
alternate-transmitter fallback. Unknown hardware, kernel, DT, signing,
resource, route, UAPI, artifact, or cleanup identities fail closed. Phase 5.1
does not authorize GPIO output, transmission, RF, boot changes, or reboot.
