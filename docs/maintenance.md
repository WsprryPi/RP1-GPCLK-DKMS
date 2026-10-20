<!-- SPDX-License-Identifier: MIT -->

# Maintenance and recovery

Use WsprryPi's owning installer and update workflow for a managed installation.
Keep exact predecessor software and recovery inputs until an update has
completed successfully. Do not install a package or development tree over
an unexplained provider state.

## Update WsprryPi or the provider

1. Stop transmission and wait for cleanup and route transactions to finish.
2. Record the current application/provider versions and retain the previous
   installation inputs.
3. Follow your WsprryPi version's installation/update procedure. It verifies
   owned state, prepares the runtime for replacement, then validates or
   installs the selected provider and restores neutral administration.
4. Check the complete installer result. An explicitly saved RP1 route may
   be restored with transmission disabled.
5. Confirm the route and status before resuming operation deliberately.

Foreign or modified files and mixed ownership are preserved through refusal.
Direct package upgrade/downgrade is not a rollback procedure. Development to
release migration and incompatible transitions require owning cleanup,
verified absence, then installation of the selected exact software.

## After a kernel update

DKMS builds against eligible installed header trees. A module built for the
old kernel is not automatically usable with the new one.

1. Compare the running kernel with the installed module build using the
   [read-only inventory commands](command-line.md#system-and-module-inventory).
2. If headers or builds are missing, retain the install/build error and use
   the owning installation procedure to repair the exact prerequisite.
3. Let WsprryPi's startup workflow reconcile the new boot before using the
   saved route. An old journal alone does not prove current-boot ownership.

Do not manually load a mismatched module, bypass signing policy or force a
route to restore output. Build success does not establish timing or RF quality.

## When service restoration fails

The route transaction and restoration of WsprryPi are separately verified.
Correct the reported service prerequisite before retrying restoration.

- After a successful route selection, the installed client's
  `restore --execute` retries application restoration without repeating
  route effects.
- After **Route removed; service unavailable**, repeat removal for the route
  that was removed once the service error is corrected.
- A previously stopped or administrator-masked service stays stopped or
  masked; restoration does not override that administrator choice.

See the [administrative command reference](command-line.md#administrative-recovery)
for exact commands. A missing manager, ownership conflict or cleanup fault
requires investigation before retrying an effect.

## Recover an interrupted transaction

Recovery is different from normal route removal. **Recovery returns to no
route and intentionally leaves WsprryPi inhibited.** It may stop the application
and does not automatically resume operation.

Preserve the failing response and collect a support bundle before making
further changes when possible. An administrator should confirm that the exact
installed runtime owns the transaction, then use the owning recovery action.
After recovery, a new route selection and application readiness check are
separate steps. Do not delete journals or installation records to bypass a
refusal.

## Uninstall

Use WsprryPi's normal uninstall workflow for installer-owned RP1 support. It
prepares the exact owned runtime for removal before application teardown.
A preparation failure stops the uninstall; keep its error and records.

Standalone removal requires prior owning route/deployment cleanup and verified
absence of active modules and endpoints. Follow the
[package lifecycle procedure](https://github.com/WsprryPi/RP1-GPCLK-DKMS/blob/devel/engineering/operations/package-lifecycle.md).
Administrator signing keys, trust entries, shared configuration and unrelated
files are retained. Removing a GPIO route alone is sufficient if you simply
want to stop using that output while keeping the software installed.
