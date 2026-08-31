<!-- SPDX-License-Identifier: MIT -->

# PR #7 route-manager integration execution prompt

Extend the existing implementation branch and PR #7; preserve the merged PR #6
foundation, packaged files, user work, source-development enrollment and hardware
authorization boundaries. Review both the manager and its application consumers
before changing interfaces. Do not silently reinterpret apply-and-reboot as a
runtime switch or pretend old application clients support a new protocol.

Deliver an explicit runtime protocol through the existing privileged route-manager
socket, with query, preflight, switch and cleanup recovery, and an installed
operator client. Bind mutations to explicit execution, actor/request identity,
current boot/controller session/generation and exact deployment identities.
Preserve structured kernel error and overlay ownership observations, application
inhibition, strict input bounds, stale/replay rejection and fail-closed legacy
behavior. Do not enable output or auto-release the service inhibit. Implement the separately authorized WsprryPi browser adaptation on its own branch,
with explicit runtime controls, preserved legacy behavior, and honest disconnect feedback.

Provide an offline deterministic bundle builder and concrete, opt-in installation,
update and rollback/recovery tooling. Bind the consumer/controller pair, embedded
route overlays, both UAPIs, manager/admin/client tools and service drop-in. Preserve
package executables and the existing source-development drop-in. Require reviewed
plan digests for filesystem changes, maintain durable pre-change backups and
journals, reject foreign or changed files, and retain recoverability through every
partial update. Serialize deployment against route operations. Never replace a
loaded module or silently adopt pending/foreign runtime state. Activation must be
explicit and reject firmware-selected routes; migration/reboot remain separately
reviewed operations. No installer may start transmission or unmask WsprryPi.

Test the actual protocol-to-admin-to-kernel-facing sequence offline with injected
kernel outcomes, plus filesystem staging, installation, update and crash recovery
in isolated temporary roots. Verify systemd socket/ExecStart wiring and sandbox
permissions, binding rejection, complete file inventories, replay/stale requests,
structured failure readback, service inhibition and legacy-request rejection.
Inspect every test before running. Run the existing suite, schema/documentation,
SPDX and whitespace checks. Reassess adversarially, fix actionable findings, and
repeat affected checks until clean within the delivered software scope.

Do not deploy to wspr5, alter services or boot configuration, load/unload modules,
apply/remove overlays, change GPIO, reboot, or transmit. Prepare reviewable tools
and a precise later authorization gate. Report any client/UI integration not
included, rather than claiming the ordinary browser workflow works. Commit and
push attributable changes to PR #7, update its scope/evidence, and report Git
state, actual validation, licensing and outstanding target qualification.
