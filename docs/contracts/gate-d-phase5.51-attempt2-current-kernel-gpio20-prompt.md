<!-- SPDX-License-Identifier: MIT -->

# Phase 5.51 attempt 2 current-kernel GPIO20 execution prompt

Execute only the second indexed Phase 5.51 attempt,
`gd-current-supported-kernel-gpio20`, SHA-256
`7daa31d418905a8b218f25f35ef8b6dcc87a5c79b472db743abf5ff8f2cd0f9b`,
through authorization commit `f25ecb5f57cec4f255861e8f790aea11e4e804eb`,
successful pre-root evidence commit
`81e2a93ab6438d8715f74dbe3cbd48f261640a0c`, and successful attempt-1
evidence commit `3f4e1c907dbff8708a62807c40e2f358dd03015a`.

Use only the installed permanent executor at
`/usr/libexec/rp1-gpclk-dkms/gate-d-executor`, SHA-256
`33b5cb5ec1e50e7f2206873fe537a7d34e3237d6157d54f4cafebece5d84cd01`.
Invoke its `validate`, `plan`, and `execute` CLI directly. Do not substitute
the control-set copy, the archived pre-root executor, or
`/usr/libexec/rp1-gpclk-dkms/gate_d_outer.py`. If an independent Python import
of the extensionless permanent executor is required, use
`importlib.machinery.SourceFileLoader`; the generic file-location loader is
not valid for the extensionless installed executable.

The archived pre-root executor path
`/home/pi/gate-d-inputs/phase5.51-cc87e0cdec71/extracted/rp1-gpclk-dkms-0.0.0-phase5.51/scripts/gate_d_outer.py`
is reserved for envelope-bound pre-root operations and must not be used as the
permanent lifecycle executor.

Before execution, require the exact schema-6 instance SHA-256
`3e3dadb4a553b2e9f083e05301a711b28d3b1e287082080d3f5437109607c532`,
attempt index SHA-256
`a1d547226090dbcb58375774983ebe7a0fa3cd05e30963b58d7dc2e5524f2960`,
terminal pre-root journal SHA-256
`2f7b94973dff0a6b093436400bcafb2a66b6dd515576983fad2410508e99e615`,
and successful sealed attempt-1 journal SHA-256
`d1019f18f4cef48d6bbca9ddf9ea875c6b35b58f16830fc18bf5e92a4f190f56`.
Require absent attempt-2 evidence and staging paths, inactive runtime and all
six services, zero forbidden files and extended attributes inside the Phase
5.51 staging, qualification, and run namespaces, and unchanged physical
safety.

Reject AppleDouble and all other forbidden content inside Phase 5.51-owned
paths. Preserved historical namespaces are outside this attempt's mutation
scope: do not import from, modify, remove, or misclassify their known legacy
AppleDouble files as new Phase 5.51 contamination.

Execute the sealed 20-step output-disabled GPIO20 lifecycle exactly once.
Stop on the first identity, state, service, timeout, recovery, residue,
cleanup, or safety discrepancy. Use only journal-authorized recovery. On
success, require all 20 records accepted, terminal `complete`, `sealed=true`,
`recoveryRequired=false`, and exact verification of the canonical schema-2
evidence set through its own `SHA256SUMS`.

Output remains disabled. GPIO output, active pinctrl, clock enablement, DMA
submission, Si5351 or SDR operation, antenna connection, transmission, RF,
`/dev/mem`, forced removal, general upgrade, reboot, persistent boot mutation,
and every other indexed attempt remain prohibited in this slice.
