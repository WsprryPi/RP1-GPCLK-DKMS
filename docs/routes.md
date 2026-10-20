<!-- SPDX-License-Identifier: MIT -->

# Select or remove a route

WsprryPi manages one RP1 GPIO route at a time. Use its **Setup > Transmitter**
controls for normal changes. Keep the physical wiring consistent with the
route you select.

| Selection | GPIO number | Physical header pin | Result |
| --- | --- | --- | --- |
| GPIO4 | 4 | 7 | Uses the GPIO4 output path |
| GPIO20 | 20 | 38 | Uses the GPIO20 output path |
| None | No output GPIO | No output pin | Returns the controller to neutral administration |

Both GPIO routes use GPCLK0 and have separate overlays and compatibility
identities. There is no arbitrary-pin selection or automatic substitution.

## Choose or change the route

1. Stop transmission in WsprryPi. Wait for committed work, cancellation,
   cleanup and any provider transaction to finish.
2. Verify the RF setup and the header connection. Follow the
   [electrical precautions](safety.md) before moving wiring.
3. Open **Setup > Transmitter** and select RP1 as the transmitter backend
   when needed. Review the requested route and the reported active route.
4. Select **GPIO4** or **GPIO20**, then choose **Switch route**. **Cancel**
   discards an uncommitted draft selection.
5. Keep the status dialog open. WsprryPi may briefly disconnect while the
   manager performs the change and restores the application service.
6. Confirm the selected route is reported as **Active** and no recovery or
   cleanup error remains. Leave transmission disabled until you deliberately
   start an eligible operation through WsprryPi.

Runtime switching occurs in the current boot and does not require a reboot.
Saving a selection alone is not evidence that the route became active. If
the dialog reports failure or never confirms completion, refresh status and
follow [troubleshooting](troubleshooting.md).

## Remove the route

1. Stop transmission and wait for cleanup.
2. In **Setup > Transmitter**, select **None** and choose **Remove route**.
3. Wait for **Route removed**. The controller remains available for
   administration, but `/dev/rp1-gpclk` is absent and output is disabled.

If WsprryPi was running, successful removal restores it online and idle.
A service that was already stopped or administrator-masked remains in that
state. Removing a route does not uninstall the provider.

**Route removed; service unavailable** means the route reached neutral but
application restoration failed. Keep transmission disabled and follow
[service restoration](maintenance.md#when-service-restoration-fails).

## After a reboot

The owning WsprryPi startup workflow must validate the new boot and restore
managed administration before a saved RP1 route can be used. A saved setting
or a previous boot's successful status is insufficient. If startup reports
recovery required, preserve the records and follow the reported procedure.

An older packaged route manager can instead use boot-selected overlays and
reboot/reconciliation. Do not mix that profile with the managed runtime
workflow described here. Ask for support if you cannot identify which profile
owns an existing installation.
