<!-- SPDX-License-Identifier: MIT -->

# Application route manager contract v1

`/usr/sbin/rp1-gpclk-route-manager` is the stable application-facing executor installed by `rp1-gpclk-dkms` 1.1.1. It accepts one JSON object on standard input, no command-line arguments, and writes one JSON object to standard output. Both directions use schema version 1 and `schema/rp1-gpclk-route-manager-v1.schema.json`; the contract identifier is `rp1-gpclk-route-manager-v1`.

Requests contain `schemaVersion: 1` and one operation. `query` and `reconcile` have no other fields. `preflight` requires `route` (`gpio4` or `gpio20`). `apply-and-reboot` requires `route`, `execute: true`, an 8--64-character `requestId`, and an attributable `actor`. `rollback` requires the same mutation fields except `route`. Unknown or operation-inappropriate fields fail closed.

Responses contain `schemaVersion`, `contract`, `operation`, `status`, and either `state` or `error`. State keeps `configuredRoute` (the package-owned boot block) separate from `activeRoute` (the enabled post-boot device-tree endpoint). A configured route never establishes active or live-eligible state. Consumers require successful post-boot reconciliation and their own exact-build compatibility decision.

`query` and `preflight` are read-only and need no physical-topology confirmation. Preflight validates exact 1.1.1 package, module, UAPI and both overlay identities, route ownership syntax, journals, fixed service idleness, endpoint closure, and `live_output=0`; it does not open the endpoint or operate GPIO.

Mutations require UID 0 and `execute: true`. They accept no paths, overlays, commands, sudo arguments, or shell fragments. The executor owns only the single delimited route block and rejects foreign, duplicate, malformed, or ambiguous state. It writes a root-only attributable journal below `/var/lib/rp1-gpclk-dkms/route-transactions`, atomically replaces and reads back the boot configuration, then invokes only `/usr/bin/systemctl reboot`. Interrupted changes remain recovery-required. Rollback restores only exact journaled bytes when the current file still equals the transaction result. Reconciliation completes only after the boot ID changes and configured and active routes agree.

Package installation installs the executor, schema, and document but creates no route block or journal, selects no route, loads no module, and performs no reboot or output activity. WsprryPi retains application policy, scheduling, operator confirmation, topology ownership, and qualification. Qualification-only `release_candidate_transaction.py`, plans, and evidence archives are not installed runtime dependencies.
