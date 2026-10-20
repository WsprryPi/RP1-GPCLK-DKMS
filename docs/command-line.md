<!-- SPDX-License-Identifier: MIT -->

# Command-line reference

The WsprryPi web interface is the normal route-control workflow. The commands
below help an administrator inspect an installed system or recover a known
managed transaction. Run them on the Pi; do not run developer test clients
or submit a signal merely to inspect status.

## System and module inventory

These commands read system/package metadata. They do not load a module,
select a route or open the execution endpoint:

```sh
uname -r
uname -m
dpkg-query -W -f='${Status} ${Version}\n' rp1-gpclk-dkms
dkms status -m rp1-gpclk-dkms
modinfo -k "$(uname -r)" -F version rp1_gpclk_dkms
modinfo -k "$(uname -r)" -F vermagic rp1_gpclk_dkms
modinfo -k "$(uname -r)" -F version rp1_route_controller
modinfo -k "$(uname -r)" -F vermagic rp1_route_controller
```

Source-development installations may have DKMS records without an installed
Debian package. `modinfo` describes an installed module file, not proof that
it is loaded or that the route is active. A missing result is useful evidence.

## Managed runtime inspection

When WsprryPi has installed the runtime tools, inspect their state with:

```sh
sudo python3 /usr/lib/rp1-gpclk-dkms/runtime_provider.py inspect
sudo python3 /usr/lib/rp1-gpclk-dkms/runtime_route_client.py query
```

These are observational commands: they do not install, switch routes, submit
output or repair state. They can perform passive endpoint queries. Avoid
concurrent route changes while gathering a consistent report. `inspect`
prints one JSON document and returns the [classified exit code](status.md).
`query` returns the managed route service's response and exits 2 on a reported
service error. A missing client or socket can mean deployment is incomplete;
do not substitute a different manager profile.

For installed scoped evidence status, use WsprryPi's maintained helper:

```sh
sudo python3 /usr/local/lib/wsprrypi/rp1_qualification.py status --route gpio4
```

Use `gpio20` for that route. This checks the installed evidence cache and
performs bounded passive inspection; it does not download evidence or authorize
output. The old diagnostic tool frozen in package 1.0.0-1 cannot interpret the
separate qualification supplement. Its aggregate summary is insufficient for
current qualification or output-inhibition conclusions.

## Service and kernel messages

```sh
systemctl status --no-pager rp1-gpclk-route-manager.socket
sudo journalctl -k -b --no-pager -g 'rp1[_-]gpclk'
```

`status` can return nonzero for an inactive service. Retain that result and
the actual message. Review logs before posting them publicly.

## Administrative recovery

The following commands **change the installed runtime or application service**.
Use them only for the described known state after transmission has stopped,
cleanup is complete and the owning runtime has been identified. Preserve the
failure response first. They are not a general repair script.

To retry application restoration after a successful route switch:

```sh
sudo python3 /usr/lib/rp1-gpclk-dkms/runtime_route_client.py restore --execute
```

To remove GPIO4 normally, or retry its removal after application restoration
failed:

```sh
sudo python3 /usr/lib/rp1-gpclk-dkms/runtime_route_client.py remove gpio4 --execute
```

Use `gpio20` only when GPIO20 is the route being removed. Successful removal
returns to no route and restores a previously running application online and
idle. Previously stopped or administrator-masked services retain that intent.

For reviewed recovery of an interrupted route transaction:

```sh
sudo python3 /usr/lib/rp1-gpclk-dkms/runtime_route_client.py recover --execute
```

Recovery returns to no route and **keeps the application inhibited**. It does
not resume transmission or complete every deployment/update recovery. If the
command refuses ownership, reports a cleanup fault or cannot prove completion,
stop and request support. Do not delete journals or force unload.

Routine selection and switching belong in [WsprryPi's route controls](routes.md).
Lower-level deployment plans, signing and package operations are described in
the repository's engineering procedures for administrators maintaining those
specific profiles.
