<!-- SPDX-License-Identifier: MIT -->

# Authorized wspr5 runtime deployment and clock-disabled test prompt

The user authorizes exact-target deployment review, clock-disabled hardware tests
and necessary reboots in this task. This supersedes the earlier not-authorized
status for those operations; it does not authorize transmission, RF qualification,
output-enabled loads, automatic application restart, or unrelated hardware work.

Use `ssh wspr5` exactly. The reviewed starting point is Pi 5 Model B Rev 1.0,
aarch64, kernel `6.18.34+rpt-rpi-2712`, boot
`28d025ed-0dcf-4a0b-b299-7819eed0ce6d`, firmware-owned GPIO20, a loaded version
1.1.2 predecessor with disabled output and no endpoint holder. Revalidate this
snapshot before mutation. The exact inventory and bundle hashes are recorded in
[review.json](../evidence/runtime-target-a0f2794/review.json).

Use source commit `a0f2794d532ed237644ed67086261cc3e3f626c7` and the reviewed opt-in
pair: consumer SHA-256
`11bd0cdbf0d75b1d258c680e20b80deb18f88cba12124370d80949ae014ccf96`, controller
`bf73b32861b9bc7de3f44b1da23d6247e55bc57a68b4671865ff8d82b772472d`.
The freshly assembled binding SHA-256 is
`ee3b1b88b716a3b9e08a61d29c33e8ae1fc5912508358fb8c475a773f2c2ee71`.
Verify all bundle members before privileged execution. Do not substitute older
three-file bindings or a moving branch. The application companion commit remains
`24bd2b11ef50f59fbfd5ca950eca44d8d3767892`; this gate uses the installed operator
client and leaves the application stopped, without installing a new app binary.

## Preconditions and migration

1. Confirm the output is disconnected from antennas/active transmit chains or
   appropriately terminated, and other signal sources sharing the path are
   disabled. Do not infer this from software clock state. The user confirmed this physical detail before the first target mutation.
2. Verify no competing administrator, updater, overlay consumer or transmitter
   activity; confirm live_output=N, no endpoint holder and zero GPCLK enable count.
   Check module signing, exact module resolution and actual service fragments.
3. Before modification, preserve root-owned, checksummed backups of the boot file,
   real `/etc/systemd/system/wsprrypi.service`, predecessor compressed module,
   source-development records/drop-in and affected runtime destinations. Record
   exact paths and state before every action. Existing user/application checkout
   changes are not deployment inputs and must not be overwritten.
4. The service fragment is a real file, so the generic administrator cannot mask
   it by overwriting it. Explicitly preserve the exact reviewed fragment (hash in
   review.json), replace only that attributable fragment with a persistent
   `/dev/null` mask, daemon-reload and stop the service. Verify inactive and masked.
5. Review and apply only the
   [owned-route removal diff](../evidence/runtime-target-a0f2794/migration.diff),
   preserving the actual boot file's bytes outside that block and its trailing
   newline. The initial config hash is
   `ac38ecc7261283b45db523e11b754606474b0e4894db0ee36feaec8bb9d423d6`.
   Do not repair unrelated formatting, change kernel/initramfs selection or remove
   another overlay. Reboot is already authorized for this reviewed migration.
6. After reboot, reconnect through the same alias and verify a new boot ID, the
   same kernel, no canonical RP1 GPCLK endpoint/pinctrl nodes, no loaded consumer
   or controller, and the persistent application mask. Stop on any mismatch.
7. Preserve and move the attributable predecessor `.ko.xz` outside module lookup;
   do not leave ambiguous compressed/uncompressed providers. Provision the private
   root-owned state directory. Run the reviewed installer plan, inspect its exact
   old/new hashes, then execute that digest. Confirm depmod resolution, installed
   hashes and the new runtime profile while preserving the package executable and
   old source-development drop-in. No automatic updates are permitted during tests.

## Clock-disabled execution and cleanup

Load only the bound controller using its fixed absolute path after neutral-tree
verification. Verify root-only endpoint identity, module note and clean initial
session/generation/ID/flags. Query through the installed runtime socket/client.

Execute one GPIO4 switch, one GPIO20 switch, then GPIO4 again, explicitly and
serially. At each step capture the request/result, journal, boot/session/generation,
overlay ID, last errno, consumer/controller build notes, actual DT route/pin,
platform binding, live_output=N, no transmission endpoint owner, GPCLK enable
count zero and read-only pin observations. Do not transmit or submit DMA work.
The three switches must share a boot ID to demonstrate the limited rebootless
route-transition observation. GPIO4 and GPIO20 evidence remain separate.

Execute explicit cleanup recovery to no route. Verify no consumer/endpoint/owned
DT route, no retained ID/fault, no GPCLK enable and no pending effect. A clean
neutral controller may then be unloaded using ordinary, non-forced removal.
The user subsequently requested GPIO20 as the final state. After proving cleanup,
reapply GPIO20 and leave the controller/consumer loaded with output disabled.
Leave WsprryPi masked and stopped. Preserve the backups, journals and evidence;
do not automatically restore the firmware route or enable output.

STOP on unexpected active output, fault, retained removal error, ownership
ambiguity, module mismatch, busy result, timeout or unknown cleanup. Do not retry
an effect, clear a journal, force-unload, or reboot to erase evidence. Review a
specific recovery action first; necessary reboots are authorized but must have a
safe-state rationale. Destructive fault injection and forced kernel teardown are
not part of this smoke sequence. Report such fault/crash coverage as offline only
unless an additional bounded test implementation is reviewed and safely executed.

## Assessment and reporting

Perform an adversarial review of the actual deployment and evidence. Repair
software issues offline and rerun affected checks before deploying changed bytes;
regenerate and record exact bindings when needed. Repeat assessment until clean
within the executed scope. Record each target effect and actual result, skipped
tests, residual risks and clean-up state. Commit/push attributable code/docs/test
evidence; do not merge PR #7 or publish a release. Clock-disabled observations are
not electrical silence measurements, transmission readiness or RF qualification.

## Repaired artifact amendment

The first target pass found kernel allocation warnings from exported overlay
symbols. The user-authorized repair/retest loop produced controller SHA-256
`59b3ae00e8a504fe82109ea80f5753831ff92608043e8c206f7adadf4b92b4c8` and binding
`66e3bda60fa91c4ec8035d9af4471f070edb8b4a48a485e5f6c2ce032548f16d`; consumer
bytes were unchanged. These supersede the initial artifacts for the final run.
See [build identities](../evidence/runtime-target-a0f2794/symbolfix-build.json) and
[executed results](../evidence/runtime-target-a0f2794/results.json).
