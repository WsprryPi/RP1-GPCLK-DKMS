<!-- SPDX-License-Identifier: MIT -->

# Phase 5.47 bounded lifecycle attempt 1 prompt

Execute only indexed Phase 5.47 attempt 1 on `wspr5`, using authorization
commit `ecfb65795f8a79a7d60264814c8fea2ac459d15d` and authenticated pre-root
evidence commit `887d5c9449bb0a53fb7a912d23775e336607a946`.

Bind execution to installed executor SHA-256
`6af8b9fe690b5a2bb22930cb77593a46894da77bf9623c3722b9feb66139a004`,
root-marker SHA-256
`9ee2baa5b5bd741251eb2efcf1dfd0da93519b890c6761cfd64ee02f218f4659`,
authorized instance SHA-256
`9e0a1c74f2810670b8fb212b694dca2f9cc36f85259000afcf8d2b852c09fee8`,
attempt-index SHA-256
`dc68030fa86386659f92a93f56a96d05979af2c541d1be7bfc3e3b33c2e4651d`,
and index-entry-1 document
`gd-current-supported-kernel-gpio4`, SHA-256
`d77fe261efd274aec1136392e91c776f486fa6f52b1848ed2b69c0216ae8525f`.

Before creating attempt evidence, independently require the terminal Phase 5.47
pre-root journal, exact root and installed-tool identities, absent attempt
evidence and staging paths, running kernel `6.18.34+rpt-rpi-2712`, inactive
runtime, absent test DKMS version, no overlay, and exact service pre-states.
Compare the live service state both with the canonical snapshot and with every
`requiredPreState` in the sealed attempt document. A disagreement between
those two sealed contracts is a control-set discrepancy: do not start or stop
services to manufacture a match, do not create attempt evidence, and do not
invoke the executor.

Only if every precondition agrees may
`/usr/libexec/rp1-gpclk-dkms/gate-d-executor execute` be invoked with the exact
root-bound document, index, instance, root privileges, and `--execute`. Permit
only the 19 sealed operations and owned paths. Never retry, resume, skip,
substitute, or begin attempt 2.

Stop on the first identity, baseline, state, service, timeout, recovery,
residue, cleanup, transition, or safety discrepancy. Preserve the sealed
staging tree, qualification root, and pre-root journal. Use absolute target
paths, including `/usr/sbin/dkms` and `/usr/sbin/modinfo` when required by a
sealed tool.

Output remains disabled. Active clock output, DMA submission, GPIO output,
Si5351 operation, transmitter keying, SDR operation, antenna connection, RF,
`/dev/mem`, forced removal, general upgrade, and unreviewed persistent boot
mutation remain prohibited.
