<!-- SPDX-License-Identifier: MIT -->

# Phase 5.52 attempt 3 prior-kernel downgrade GPIO4 execution prompt

Execute only the third indexed Phase 5.52 attempt,
`gd-prior-supported-kernel-downgrade-gpio4`, SHA-256
`37d60b9903eb224e3654786c3181fbbfa3e925b0544763bc7ff0ede34ffd29b1`,
through authorization commit `8e8cdbe5d573d9c1744003c173c47463060d7f31`,
successful pre-root evidence commit
`08db08f4aa18bd471bb6424b23f80b8d745c42ba`, and successful attempt-2
evidence commit `d7f29ed0236a4f8fbe7667fbc9310f95deb49b08`.

Use only `/usr/libexec/rp1-gpclk-dkms/gate-d-executor`, SHA-256
`70f845be52c2cc7993a53aa2d7e7258319e261854903fd7a2c6d5dce29fa4061`,
through its direct `validate`, `plan`, and `execute` CLI. Do not substitute any
control-set, archived pre-root, or underscore-named executor.

Before execution require schema-6 instance SHA-256
`8f53fa6c41153965d49f11a4da7b139c3aa0e17cd1e9a2a77f8157c21cf43bd2`,
index SHA-256
`744427cc21988c73558dd7a2c89fdbf97915288bf539941e67a8cf080c0e90d8`,
pre-root journal SHA-256
`9cd462085a3c86d2d8992197470a600aff6ec256526a5c30e49d62239fde403a`,
and sealed attempt-2 journal SHA-256
`4abe76ce12cc5091c3b38fff5128efd09dd61978dcc6afd0728ce9ffdef862a1`.
Require absent attempt-3 evidence and staging, normal kernel
`6.18.34+rpt-rpi-2712`, inactive runtime/services, no candidate or predecessor
DKMS test state, clean Phase 5.52 namespaces, recovery availability, and
unchanged physical safety.

Execute the sealed 27-step output-disabled lifecycle exactly once. Its two
document-bound reboots are authorized only if execution reaches their sealed
checkpoints: first into installed stock kernel `6.12.75+rpt-rpi-2712`, then
back to `6.18.34+rpt-rpi-2712`. After each reboot, verify the expected kernel
and exact journal, then resume the same attempt with `--resume --execute` within
its original deadline. Do not improvise boot edits or retry from scratch.

Stop on the first discrepancy. If the known ordering condition recurs and
preflight rejects the normal kernel before boot selection, preserve its sealed
failure evidence; do not resume, recover, reboot, or bypass the gate. Require
proof that only evidence creation occurred and all runtime, boot, DKMS,
service, overlay, module, GPIO, clock, DMA, transmission, and RF state stayed
unchanged.

Output remains disabled. GPIO output, active pinctrl, clock enablement, DMA,
Si5351/SDR operation, antenna connection, transmission, RF, `/dev/mem`, forced
removal, general upgrade, unsealed boot mutation, and every later attempt are
prohibited.
