<!-- SPDX-License-Identifier: MIT -->

# Phase 5.46 Gate D control-set construction and validation prompt

Construct and independently validate the complete output-disabled Phase 5.46
Gate D control set for frozen source commit
`b43e2744b212f5bc53ad40584254f52310af4684`, release archive SHA-256
`0e0debdd96560602bd61457afc59782cfad2a4fb1b6f9b54e0d2505453e6c8f2`,
representative module SHA-256
`c1203555194b6d7983ca4bde978709f09588878022ea58df8fc90adda23ce6e7`,
and attempt namespace `phase5.46-b43e2744b212`.

First capture a fresh canonical, read-only snapshot on `wspr5` using the
reviewed capture and independent validation tools. Require the terminal-complete
Phase 5.45 administrator ledger, all 28 measured installed paths, the exact
stock-kernel identity used by the representative build, all six reviewed
services inactive, and no module, endpoint, route overlay, test DKMS version,
or live output. Bind the physical declarations that the separate I2C Si5351
path is disconnected and unused, the SDR is unused, and no antenna is
connected. Stop if capture or independent validation fails.

Generate deterministically the schema-5 route decision, target plan,
qualification bootstrap, execution instance, pre-root envelope, qualification
identity, predecessor inventory, attempt index, and all 38 attempt documents.
Retain ten ready rows and five deferred environmental rows. Every attempt-owned
path must be unique, strictly below the new namespace, and disjoint from all
retained Phase 5.42, Phase 5.43, and Phase 5.45 paths.

Close the complete qualification-root trust graph. Every referenced control,
matrix policy, attempt index, attempt document, and Python module used by the
installed executor must be an authenticated pre-root transition input and a
sealed-root destination. Require every transition source to appear in the
envelope input inventory. Reconstruct a root only from those transitions and
validate the instance from it. Extract all eight Python modules from the exact
frozen archive and require their bytes to match both the plan identities and
the root transitions. Validate the final pre-root envelope with the archived
pre-root and outer executor bytes.

Generate twice in isolated trees and require byte equality. Run the complete
offline suite with all available archive-bound regressions. Perform a separate
adversarial review and correct every actionable finding before committing.
The offline-construction approval may be recorded, but
`targetExecutionApproved` and `executionReady` must remain false.

Do not stage lifecycle inputs, request or bind lifecycle authorization, stop or
start services, administer DKMS, load or bind the module, apply an overlay,
change boot state, access GPIO or I2C, operate the Si5351 or SDR, enable a
clock, submit DMA, connect an antenna, transmit, or produce RF. Commit and push
only the complete deterministic control set and its validation evidence.
