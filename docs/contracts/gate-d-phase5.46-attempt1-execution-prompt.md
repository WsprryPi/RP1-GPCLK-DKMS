<!-- SPDX-License-Identifier: MIT -->

# Phase 5.46 bounded lifecycle attempt 1 prompt

Execute only indexed Phase 5.46 attempt 1 on `wspr5`, using the authorization
recorded at `6b3dcc83c817e6c0011e6dde649b146df88abc91` and the successful
authenticated pre-root transition recorded at
`74b9cd0abe2565ea9fa3a8795cc7b100995f3cb7`.

Bind execution to installed permanent executor SHA-256
`1d93c918a57414d379b9bd6af3ae170195687c93d017c55595cb5c0750c57917`,
root marker SHA-256
`feb0d12cf770d241a2740867fa69b20c9e2d44d2d1d6f4c4292053114e781b32`,
authorized instance SHA-256
`cece70ab06d8a3b6de0240851b1ec2d7612e2d699f0f6c97de57a42da0687f2e`,
and attempt-index SHA-256
`e1858c68af8362a3c9ac969b5335317617e8e67491ddc916c3190c2eb6a8243d`.

The only authorized attempt is index entry 1,
`gd-current-supported-kernel-gpio4`, document SHA-256
`3a5271f0e789ef3223d20d2fc3484b73884e07f9587a282b2deb53055d0f3985`.
Its evidence directory is
`/var/lib/rp1-gpclk-dkms/gate-d/runs/phase5.46-b43e2744b212/current-supported-kernel/gd-current-supported-kernel-gpio4`.

Before execution, require the pre-root journal terminal `complete` at
checkpoint `commit` with `liveOutput: false`; exact root-bound identities; the
attempt evidence and staging paths absent; running kernel
`6.18.34+rpt-rpi-2712`; inactive runtime; no Phase 5.46 DKMS test version; no
active overlay; and all six reviewed services inactive. The separate I2C
Si5351 path remains disconnected and unused, the SDR remains unused, no
antenna is connected, and recovery remains available.

Invoke only `/usr/libexec/rp1-gpclk-dkms/gate-d-executor execute` with the
exact root-bound attempt document, index, and execution instance, root
privileges, and `--execute`. Permit only the attempt's 19 sealed operations and
owned paths. Never skip, substitute, or begin another indexed attempt.

Stop on the first identity, baseline, state, timeout, service, recovery,
residue, cleanup, transition, or safety discrepancy. A sealed
`inactive-recovery-required` journal is not resumable: the executor requires a
separately indexed operation identity for recovery and rejects recovery from
the same operation. If no such exact recovery operation is authorized, preserve
the sealed evidence and stop without beginning another attempt.

Output remains disabled. Active pinctrl, clock enablement, DMA submission,
GPIO output, Si5351 operation, transmitter keying, SDR operation, antenna
connection, RF, `/dev/mem`, custom-kernel qualification, forced removal,
general upgrade, and unreviewed persistent boot mutation remain prohibited.

After the attempt or terminal recovery, require inactive runtime, no Phase
5.46 DKMS test version, no overlay, no endpoint, `liveOutput: false`, restored
services, sealed evidence, and exact owned-path cleanup. Preserve all evidence,
independently review the outcome, stop before attempt 2, and commit and push
documentation only.
