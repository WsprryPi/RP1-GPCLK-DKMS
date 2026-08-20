<!-- SPDX-License-Identifier: MIT -->

# Phase 5.45 Gate D control-set generation and validation prompt

Construct and independently validate the complete output-disabled Phase 5.45
Gate D control set for frozen source commit
`4b50db7868b7fe5ca9d830f51cd404c250192188`, release archive SHA-256
`21d05675e9d12ddb4c051868578c410737b733786357cee20eb2b0ce03f63356`,
representative module SHA-256
`977c6997fd87dfb68c61ab4b82db904e86310083741d3a41c0405a417aa36d95`,
and attempt-path namespace `phase5.45-4b50db7868b7`.

Before generation, use the reviewed read-only capture tool on `wspr5` to
derive a fresh canonical snapshot from the current terminal-complete
administrator ledger and measured installed package paths. Require the module,
endpoint, overlays, test DKMS versions, live output, and all six reviewed
services—including `wsprrypi.service`—to be inactive. Bind the operator's
physical declarations that the separate I2C Si5351 path is disconnected and
unused, the SDR is unused, and no antenna is connected. Independently validate
the canonical snapshot. Stop without generating controls if capture or
validation fails; do not combine a current ledger with an older snapshot.

Generate all schema-5 controls, the 38 indexed attempt documents, ten ready
rows, five deferred environmental rows, predecessor and successor package
inventories, qualification identity, target plan, bootstrap plan, execution
instance, and pre-root envelope. Every attempt-owned path must be unique and
strictly below
`/var/lib/rp1-gpclk-dkms/gate-d/runs/phase5.45-4b50db7868b7/`, with no
intersection with Phase 5.42, Phase 5.43, or retained historical evidence.
Authorization fields and `executionReady` must remain false.

Generate twice into clean isolated trees and require byte equality. Validate
all schema, hash, release-input, representative-build, target-snapshot,
package-transition, retained-tool, terminal-ledger, path-closure, attempt-count,
row-state, safety, recovery, and cross-document edges. Validate the final
envelope using only the exact frozen Phase 5.45 archived tool bytes, never
development-worktree imports. Run the complete archive-bound offline suite and
perform a separate adversarial review, correcting every actionable finding and
repeating affected validation until clean.

Do not stop or start services, stage lifecycle inputs, bind authorization,
install or administer DKMS, load or bind the module, apply an overlay, change
boot state, access GPIO or I2C, operate the Si5351 or SDR, enable a clock,
submit DMA, connect an antenna, transmit, or produce RF. Target mutation and
lifecycle execution require later, separately bounded authorization.

Commit and push only a complete, deterministic, independently validated
control set. If any prerequisite fails, preserve a blocking assessment instead
and report the exact prerequisite and next required authorization.
