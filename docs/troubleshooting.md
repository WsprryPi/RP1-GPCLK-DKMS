<!-- SPDX-License-Identifier: MIT -->

# Troubleshooting

Keep transmission disabled while investigating an installation or route
failure. Record the exact message, the action that produced it and whether
output state is confirmed. Start with WsprryPi status and the
[read-only inventory](command-line.md); do not try successive module or overlay
commands to make an error disappear.

| Symptom | Likely checks and next action |
| --- | --- |
| `/dev/rp1-gpclk` is missing | This is expected with no route. If a route should be active, check route status, installer result and the manager. Never create the device node by hand. |
| Provider files exist but no route can be selected | Check for `activation_required` or incomplete runtime deployment. Package installation alone is insufficient. Use the owning installer/startup workflow. |
| Requested and Active differ | Wait for the current transaction. If it failed, preserve the response and investigate before another switch. |
| Kernel update left no usable module | Compare `uname -r`, headers, DKMS status and kernel-specific module metadata. Repair the exact prerequisite through the owning installer. |
| Signing or trust was rejected | Review the certificate and target kernel policy with the administrator. A nonempty signer name does not prove trust. Do not disable enforcement. |
| Permission denied | Execution and administrative tools require the installed ownership and access policy. Use administrator inspection when appropriate; do not broaden device permissions. |
| Manager socket is unavailable | Collect service/socket state and installer diagnostics. Do not start an unrelated service profile or apply a second overlay. |
| `recovery_required` or an incomplete transaction | Preserve journals and installation records. Use owning recovery after reviewing the cause. |
| `conflict`, mixed identity or changed files | Stop. Identify who owns the files and current runtime. A reinstall must not overwrite foreign or modified state. |
| Route removed but service unavailable | Keep output disabled, fix the service error, then retry the same removal. See [maintenance](maintenance.md#when-service-restoration-fails). |
| Cleanup fault, owner/lease still present or output unknown | Do not resume or force unload. Make the physical RF setup safe and request reviewed recovery. |
| Evidence missing, invalid or unverified | Check the matching application helper/cache and exact identity. Evidence state is separate from runtime readiness and application band policy. |
| No received signal despite healthy software status | Check the selected physical route, RF path, filtering, load, receiver settings and WsprryPi's band/mode limits. A build or status result does not establish RF performance. |

## Collect a useful failure report

1. Note whether the failure followed installation, an update, reboot, route
   switch, removal or a transmission request.
2. Record the WsprryPi version, provider source/release, kernel and selected
   GPIO. Distinguish requested, saved and active routes where available.
3. Preserve the complete error and its exit code. `inspect` exit codes
   10 through 14 describe classified states; [status](status.md) explains them.
4. Collect a WsprryPi support bundle if the application is available, or
   retain read-only command results if it is not.
5. Review logs and archives before sharing. Use the [support procedure](support.md).

If a command or file is absent or inaccessible, report that fact. Do not
install another tool, clear evidence or perform a test transmission just to
complete a diagnostic report.
