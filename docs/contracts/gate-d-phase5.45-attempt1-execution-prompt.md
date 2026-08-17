<!-- SPDX-License-Identifier: MIT -->

# Phase 5.45 bounded lifecycle attempt 1 prompt

Execute only indexed Phase 5.45 attempt 1 on `wspr5`, using the authorization
recorded at `362c469175578154aecfe159a25d3db8e6a91fe9` and the successful
pre-root transition recorded at `e29708f179cd89c23d61525196fbf7489a32d75c`.
Bind execution to installed permanent executor SHA-256
`33f711e89d104fe3bced29723f0a1b868cd9a4a82e91911a206c65be8c59e42f`,
root marker SHA-256
`b082c7aebf46dd98058ff8b818cae085b9130c7e672a67e4d999ce27485f1ed3`,
authorized instance SHA-256
`0a4e2b88263262d408aa30c39e4843aa1204735333cedf6bb472dfc1a50ef228`,
and index SHA-256
`3375c809dd699949f991742716628016a680bcf7253fc30ba8f3de52c294f020`.

The only authorized attempt is index entry 1,
`gd-current-supported-kernel-gpio4`, document SHA-256
`581d3e83e06ce804f373561ceff2f29ccb0b38d4b8782e55ed701e101ab6b4db`.
Its evidence directory is
`/var/lib/rp1-gpclk-dkms/gate-d/runs/phase5.45-4b50db7868b7/current-supported-kernel/gd-current-supported-kernel-gpio4`.

Before execution, require the immutable pre-root journal to be terminal
`complete` at checkpoint `commit` with `liveOutput: false`; require the exact
root-bound identities; require the attempt evidence and staging paths to be
absent; require kernel `6.18.34+rpt-rpi-2712`, inactive runtime, no candidate
DKMS test version, no active overlay, and all six reviewed services inactive.
The separate I2C Si5351 path remains disconnected and unused, the SDR remains
unused, no antenna is connected, and recovery remains available.

Invoke only `/usr/libexec/rp1-gpclk-dkms/gate-d-executor execute` with the exact
root-bound attempt document, index, and execution instance, root privileges,
and `--execute`. Do not use development-worktree or staged executors. Permit
only the attempt's 19 sealed operations and its owned paths. Never skip,
substitute, or begin another indexed attempt.

Stop on the first identity, baseline, state, timeout, service, recovery,
residue, cleanup, transition, or safety discrepancy. If and only if the
attempt's authenticated journal reports recovery-required and authorizes
recovery, invoke the same permanent executor with the exact document, index,
instance, journal path, and sealed resume mode. Terminal recovery must return
without beginning any attempt.

Output remains disabled. Active pinctrl, clock enablement, DMA submission,
GPIO output, Si5351 operation, transmitter keying, SDR operation, antenna
connection, RF, `/dev/mem`, custom-kernel qualification, forced removal,
general upgrade, and unreviewed persistent boot mutation remain prohibited.

After the attempt or terminal recovery, require inactive runtime, no candidate
DKMS test version, no overlay, no endpoint, `liveOutput: false`, restored
services, sealed evidence, and exact owned-path cleanup. Preserve all evidence,
independently review the outcome, stop before attempt 2, and commit and push
documentation only.
