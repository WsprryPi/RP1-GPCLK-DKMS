<!-- SPDX-License-Identifier: MIT -->

# Phase 5.43 target execution review

Status: STOPPED SAFE before lifecycle attempt step 1. Phase 5.43 target
execution is blocked by immutable Phase 5.42 evidence residue and must not
advance to attempt 2.

The execution slice used authorization commit
`18c4d0cf3c98b0258533c857468728364ea9e228`, frozen source
`aa92b0550acd66671fe1988510cf93987cd61c0a`, archive SHA-256
`a8a200d069ad433353a8812ef6a9a4c585b75a9f6af3d6501ac3672e90c997c3`,
schema-5 envelope SHA-256
`8fcd182d92c1ce9d29ba0cd0a78218345d20f9ec887a30a164d966ab179b9a4b`,
execution-instance SHA-256
`9b5b6657ef750b4b082e830426fd8db9fe0cd3edb1d50a46dcb97f64831de5c8`,
and attempt-index SHA-256
`7aea0b0842788831da229bfb9a28e42c98a96034e25da137819e170c3db4a6fc`.

Immediately before staging, a fresh read-only capture was independently
validated and was byte-identical to the 7,057-byte canonical snapshot, SHA-256
`d228a5fe8eaa52a2fa44d003947d51b2a3a6798e4535c0570c3836ab5b283b9a`.
All 67 envelope-bound staged inputs passed target-side SHA-256 verification.
The separately sealed envelope document was then staged and the exact archived
outer executor passed read-only pre-root validation.

The authenticated pre-root transition completed at
`2026-08-17T00:44:07.024349+00:00` with `status: complete` and
`liveOutput: false`. It installed and verified the exact permanent tools,
created the qualification root, and removed the temporary candidate DKMS test
state. It did not load the module or activate an overlay. The installed
executor, root marker, attempt index, and execution instance matched their
sealed hashes.

Attempt 1, `gd-current-supported-kernel-gpio4`, then failed closed before any
attempt step because its evidence directory already existed:

`/var/lib/rp1-gpclk-dkms/gate-d/current-supported-kernel/gd-current-supported-kernel-gpio4`

That root-owned directory contains sealed Phase 5.42 evidence dated
`2026-08-16T21:26:39Z`. Its journal is
`inactive-recovery-required`, but its document, index, and executor hashes are
respectively
`173ceac3d8d85953572f8e718fd021fb7986ffcd2d0fd0d3171309e11335429e`,
`71a8432178d639d5181bfe1da6e7b1bdf6c6e66dc4a1cec660424d2371619010`,
and `d81824ab0454ecb298714e07c08ff9d81255d216152631e5285e51e08ac1d43f`.
Those identities do not match Phase 5.43, so the Phase 5.43 executor cannot
resume, overwrite, delete, or reuse the evidence. No recovery was invoked and
no later attempt was started.

Post-stop inspection found kernel `6.18.34+rpt-rpi-2712`, module absent,
endpoint absent, no active overlay, and no candidate DKMS test version. No GPIO
output, clock enablement, DMA submission, Si5351 operation, SDR operation,
transmitter keying, antenna connection, transmission, or RF occurred.

The next gated slice is an independently reviewed retirement or archival
contract for the exact Phase 5.42 inactive-recovery-required evidence. It must
preserve the immutable journal and `SHA256SUMS`, prove that no live or owned
runtime state remains, choose a collision-free retained location, and then
produce a new frozen successor whose evidence paths cannot collide with prior
phases. Phase 5.43 attempts must not be retried under the current paths.
