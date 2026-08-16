<!-- SPDX-License-Identifier: MIT -->

# Phase 5.39 artifact-grounded control successor prompt

Retire the failed Phase 5.39 authorization recorded at commit
`85d2e5bc4947b50260eee4d94ab44a580e6410e5`. Repair the deterministic control
generator so release-input identities cannot be inherited from a predecessor
control set or validated only through internally generated references.

Capture a read-only inventory of the seven exact release inputs in the
representative-build directory `/home/pi/gate-c-evidence/phase5.39-3768ae9`
on `wspr5`. Bind the inventory to frozen source commit
`3768ae9cdccf0c2ae5809603b9a36e73507f2182`, release
`0.0.0-phase5.39`, host, directory, path, type, size, mode, owner, group, and
SHA-256. Require the exact seven-name set with no omissions, additions, or
duplicates.

Generate every envelope release-input identity and every dependent manifest
identity from that measured inventory. Update the representative-build
manifest to record all seven measured artifacts. Add an independent test that
compares the build manifest, execution instance, pre-root envelope, and every
attempt against the measured inventory rather than another generated control
document. Retain the complete typed 28-path package transition and its existing
negative tests.

Deterministically regenerate the entire hash-closed control set, run focused
and complete offline validation, and correct every actionable finding. Set
`targetExecutionApproved=false` and `executionReady=false`; the failed
authorization must not be inherited. Do not stage target inputs, execute the
pre-root transition, mutate package paths or ledgers, administer DKMS, load or
bind a module, activate an overlay, access GPIO, enable clocks, submit DMA,
operate the separate I2C Si5351 path, use SDR or transmitter equipment, reboot,
transmit, or produce RF. Commit and push the corrected successor bytes. Fresh
explicit authorization is a separate later gate.
