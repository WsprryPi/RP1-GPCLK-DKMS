<!-- SPDX-License-Identifier: MIT -->

# Phase 5.44 Phase 5.42 evidence-retirement review

Status: PASS. The exact sealed Phase 5.42 attempt-1 evidence was retired from
the live collision path without changing either evidence file. No Phase 5.43
attempt was retried or started.

The executed inputs were frozen at commit
`7b9798a` on branch `codex/phase-5-12-calibrated-review-relationship`.
Target-side SHA-256 verification matched the committed retirement tool
(`7b0f56689baa544b11ac3791a8b77e16ddf83fd908b090b90ebd532fc1db5b99`)
and control document
(`a47e7f36c38a1f699861d47179e868d6013ae2ababe6407727692729710d727d`).
The root read-only preflight returned `status: ready` before mutation.

The bounded executor atomically renamed:

`/var/lib/rp1-gpclk-dkms/gate-d/current-supported-kernel/gd-current-supported-kernel-gpio4`

to:

`/var/lib/rp1-gpclk-dkms/gate-d/history/phase5.42/gd-current-supported-kernel-gpio4`

Independent post-execution inspection found the source absent and the
destination present. The directory and its two files retained filesystem
device `66306` and inode numbers `4819785`, `4819786`, and `4819804`, proving
that their filesystem identities survived the rename. The directory remains
root-owned mode `0500`; `transaction.json` and `SHA256SUMS` remain root-owned
mode `0400`. Their SHA-256 values remain respectively
`02de65dfbe49078b193e7c2f675d8e589d396eb46e4510863c24538a41ef6bf6`
and `bfdc894bc3d9ed8b80f4b8cf7a09965474cd6320f9dcac78b5d64b499414d374`.
No extra file is present.

Post-execution safety checks passed: kernel `6.18.34+rpt-rpi-2712` retained no
loaded module, endpoint, active overlay, or candidate DKMS test version. All
six guarded services remained inactive. No installation, module operation,
overlay operation, boot mutation, GPIO output, clock enablement, DMA,
Si5351 operation, SDR operation, antenna connection, transmission, or RF
occurred.

This result removes the observed collision but does not validate reusing the
phase-independent attempt paths. Phase 5.43 remains retired and must not be
retried. The next slice must construct and independently validate a new frozen
successor whose complete attempt bundle uses phase-scoped evidence, journal,
staging, recovery, and reboot-resume paths, with regression checks proving no
path can collide with retained evidence from an earlier phase.
