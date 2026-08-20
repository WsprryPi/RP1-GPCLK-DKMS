<!-- SPDX-License-Identifier: MIT -->

# Phase 5.51 attempt 3 prior-kernel downgrade GPIO4 execution prompt

Execute only the third indexed Phase 5.51 attempt,
`gd-prior-supported-kernel-downgrade-gpio4`, SHA-256
`e4002b4b21f2fdbacfbdc4d7180b0b037bae6344e17ef3148edd5680af0f4fe7`,
through authorization commit `f25ecb5f57cec4f255861e8f790aea11e4e804eb`,
successful pre-root evidence commit
`81e2a93ab6438d8715f74dbe3cbd48f261640a0c`, successful attempt-1 evidence
commit `3f4e1c907dbff8708a62807c40e2f358dd03015a`, and successful attempt-2
evidence commit `f1f0bca089d99d5117cf5fc4b10cf0490cc3d257`.

Use only the installed permanent executor at
`/usr/libexec/rp1-gpclk-dkms/gate-d-executor`, SHA-256
`33b5cb5ec1e50e7f2206873fe537a7d34e3237d6157d54f4cafebece5d84cd01`.
Invoke its `validate`, `plan`, and `execute` CLI directly. Do not substitute
the control-set copy, archived pre-root executor, or
`/usr/libexec/rp1-gpclk-dkms/gate_d_outer.py`. If an independent Python import
of the extensionless permanent executor is required, use
`importlib.machinery.SourceFileLoader`.

Before execution, require the exact schema-6 instance SHA-256
`3e3dadb4a553b2e9f083e05301a711b28d3b1e287082080d3f5437109607c532`,
attempt index SHA-256
`a1d547226090dbcb58375774983ebe7a0fa3cd05e30963b58d7dc2e5524f2960`,
terminal pre-root journal SHA-256
`2f7b94973dff0a6b093436400bcafb2a66b6dd515576983fad2410508e99e615`,
and successful sealed attempt-2 journal SHA-256
`fbc9657f9d3f825a8893a8449f112b4f25b0029c27f411d2bbc64db383ca6f98`.
Require absent attempt-3 evidence and staging paths, the normal kernel
`6.18.34+rpt-rpi-2712`, inactive runtime and all six services, no candidate or
predecessor DKMS test version, zero forbidden files and extended attributes
inside Phase 5.51 namespaces, authenticated recovery, and unchanged physical
safety.

Execute the sealed 27-step output-disabled downgrade lifecycle exactly once.
Its two document-bound reboots are authorized: first select and reboot into
the installed prior stock kernel `6.12.75+rpt-rpi-2712`, then restore the exact
normal boot configuration and reboot into `6.18.34+rpt-rpi-2712`. At each
durable `reboot-required` checkpoint, wait no more than 600 seconds for SSH,
verify the expected kernel and exact unsealed journal identity, then invoke
the same executor, attempt, index, and instance with `--resume --execute`.
The original 1,800-second attempt deadline spans both reboots.

Stop on the first identity, boot, kernel, journal, state, service, timeout,
recovery, residue, cleanup, or safety discrepancy. Do not improvise boot edits,
select another kernel, retry from scratch, or run recovery outside the sealed
journal contract. On success require all 27 records accepted, terminal
`complete`, `sealed=true`, `recoveryRequired=false`, exact restoration of the
normal boot configuration, and verification of the canonical schema-2
evidence set through its own `SHA256SUMS`.

Reject AppleDouble and other forbidden content inside Phase 5.51-owned paths.
Preserved historical namespaces remain outside the mutation scope: do not
import from, modify, remove, or misclassify their legacy files.

Output remains disabled. GPIO output, active pinctrl, clock enablement, DMA
submission, Si5351 or SDR operation, antenna connection, transmission, RF,
`/dev/mem`, forced removal, general upgrade, any unsealed persistent boot
mutation, and every other indexed attempt remain prohibited.
