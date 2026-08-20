<!-- SPDX-License-Identifier: MIT -->

# Phase 5.38 freeze and representative-build adversarial assessment

Status: accepted for Phase 5.38 control-set construction; target lifecycle
execution is not ready or authorized by this evidence

The active development candidate is consistently `0.0.0-phase5.38` at freeze
commit `639a4667f081886c6bc068f5eb87ab3373130baf`. Phase 5.37 controls,
authorization, staging, failure, recovery, and review evidence remain
unchanged. Two isolated release units were generated using the freeze commit
timestamp, validated independently, and matched byte for byte. Their archive
SHA-256 is
`518b90d084c8184ed09b7b8b2bd7ca0b9e1ab607548226df72ad93b3ad2985ff`.

The exact checksummed archive compiled directly and unprivileged on `wspr5`
against canonical stock headers
`/usr/src/linux-headers-6.18.34+rpt-rpi-2712`. Header ownership and mode,
kernel configuration, `Module.symvers`, architecture, and compiler identities
were checked before compilation. Module, UAPI, administrator, diagnostics,
pre-root module, outer executor, and both compiled helper identities are
recorded in the representative-build manifest.

Adversarial review confirmed that the freeze carries schema-3 archive-derived
package-path expansion, rejects duplicate destinations and empty archive-tree
expansions, requires the exact existing package subset before transaction
creation, and distinguishes authenticated regular-file and symlink
transitions. The focused suite covers the observed 28-path closure, complete
omission reporting before external commands, successful transition, and
recovery after a successor mismatch at every replacement boundary. The full
offline suite passed. Linux-only UAPI client compile checks were skipped on
macOS as expected and the equivalent target helpers compiled on AArch64.

Initial and final target baselines agree: no Phase 5.38 DKMS entry, loaded
module, endpoint, or active overlay. No package installation, DKMS
administration, live-ledger mutation, retained-path replacement, service or
boot change, GPIO, clock, DMA, separate I2C Si5351, SDR, transmitter, antenna,
reboot, transmission, or RF effect occurred. The build proves representative
stock-kernel compilation compatibility only; it does not qualify lifecycle,
cleanup, coexistence, routes, timing, or RF behavior.

The next control set must use qualification identity schema 3 and bind the
complete mechanically expanded existing package-path closure, the recovered
Phase 5.37 canonical ledger, retained Phase 5.36 and Phase 5.34 history, and
this exact freeze and build manifest. It must reject any closure, type,
identity, ownership, mode, history, or safety mismatch offline before separate
execution authorization. No actionable finding remains within this build-only
slice.
