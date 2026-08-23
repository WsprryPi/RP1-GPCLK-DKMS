<!-- SPDX-License-Identifier: MIT -->

# Application route manager contract v1

Beginning with 1.1.1, `/usr/sbin/rp1-gpclk-route-manager` is the stable application-facing executor. The 1.1.2 package preserves that contract. It accepts one JSON object on standard input, no command-line arguments, and writes one JSON object to standard output. Both directions use schema version 1 and `schema/rp1-gpclk-route-manager-v1.schema.json`; the contract identifier is `rp1-gpclk-route-manager-v1`.

Requests contain `schemaVersion: 1` and one operation. `query` has no other fields. `preflight` requires `route` (`gpio4` or `gpio20`). `apply-and-reboot` requires `route`, `execute: true`, an 8--64-character `requestId`, and an attributable `actor`. `rollback` and `reconcile` require the same mutation fields except `route`. Unknown or operation-inappropriate fields fail closed.

Responses contain `schemaVersion`, `contract`, `operation`, `status`, and either `state` or `error`. State keeps `configuredRoute` (the package-owned boot block) separate from `activeRoute` (the enabled post-boot device-tree endpoint). A configured route never establishes active or live-eligible state. Consumers require successful post-boot reconciliation and their own exact-build compatibility decision.

`query` is passive. `preflight` is read-only and needs no physical-topology confirmation. It validates exact 1.1.2 package, module, UAPI and both overlay identities, route ownership syntax, journals, endpoint ownership and closure, and `live_output=0`. It observes and reports each fixed service state but deliberately accepts an active `wsprrypi.service`, allowing the running UI to present the result before confirmation. Application execution, scheduling, drain, and commitment idleness remain WsprryPi policy. Preflight does not open the endpoint, stop a service, or operate GPIO.

Mutations require UID 0 and `execute: true`. They accept no paths, overlays, commands, sudo arguments, or shell fragments. Before any boot write, the executor records the observed fixed service states in its root-only attributable journal, owns a bounded stop of only `wsprrypi.service` and `soapyremote-server.service`, and verifies both are inactive or failed. A partial quiescence or later pre-reboot failure restores every service that was active and retains explicit recovery state. Only after verified quiescence may it atomically replace and read back the boot configuration and invoke `/usr/bin/systemctl reboot`. Rollback uses the same ownership protocol and restores only exact journaled bytes. Reconciliation is an attributable root mutation and completes only after the boot ID changes and configured and active routes agree.

The package ships disabled-by-default `rp1-gpclk-route-manager.socket` and `rp1-gpclk-route-manager@.service` units. The Unix socket is mode 0660, owned by root and group `rp1-gpclk-route`. An explicitly enrolled WsprryPi service account can send the same closed JSON request over that fixed socket. Systemd runs the executor as root in a separate service cgroup, so stopping WsprryPi cannot terminate the transaction. Enrollment and enabling the socket are explicit WsprryPi/operator policy; neither occurs silently. This is the supported interactive mutation transport and requires no sudo command, wrapper, arguments, or shell.

Package installation installs the executor, schema, document, disabled units, restricted group, and empty state parent but creates no route block or journal, starts no socket, selects no route, loads no module, and performs no reboot or output activity. WsprryPi retains application policy, scheduling, operator confirmation, topology ownership, enrollment, and qualification. Qualification-only `release_candidate_transaction.py`, plans, and evidence archives are not installed runtime dependencies. The route manager does not expose live-output or carrier execution; the unreleased 1.1.2 GPIO4 and GPIO20 r2 development entries belong to the module compatibility gate only and are not present in a successor package yet.

Completed schema-1 qualification journals created by the historical 1.1.1
package executor remain in place byte-for-byte. The manager recognizes them
only when their closed field set, attribution, hashes, terminal `complete`
status, `reconciled: true`, and `rebootRequired: false` validate; it reports
their names and SHA-256 identities as historical and never treats them as a
current pending transaction. Unknown, altered, incomplete, or nonterminal
historical journals still block all operation. The exact earlier package-owned
`# version=1.1.1 route=gpio4|gpio20` block and the exact 1.1.1 contract marker
`# contract=rp1-gpclk-route-manager-v1 package=1.1.1-1 route=gpio4|gpio20`
are accepted as
`historical-package-owned` and are replaced in place by the current contract
format only inside a journaled, quiesced route mutation. No evidence is moved,
renamed, deleted, or rewritten merely to permit operation.

Any future 1.1.2 executor-bearing package will be a new artifact. Output-inhibited evidence bound to predecessor package SHA-256 `247bd7da35e4ad812a13828668fe03673da127bad7ed2b3e970876f3f21c002d` establishes only that predecessor's GPIO4/GPIO20/restored-GPIO4 route-manager lifecycle and cleanup. It does not validate future package bytes or transfer completed live eligibility. The r2 source evidence is independently route-bound development execution and cleanup evidence, not package, waveform-integrity, decode, product-live, or RF qualification.
