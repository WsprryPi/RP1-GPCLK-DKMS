<!-- SPDX-License-Identifier: MIT -->

# Release 1.0.0 final-artifact reproduction review

Result: **the Debian product and separate qualification artifact reproduce
byte-identically from commit `a20abc828ec300ad3227a34be7572f4fa28525b2`**.

Two clean detached worktrees independently built the complete artifact set in
the pinned arm64 Debian Trixie builder. The resulting product package is
`951289ee5d0e44cff41b59756f00161aba16f43f1450715ba57c4a3679a2e6b8`; the
qualification archive is
`fa11f86c8a5f1443560d71720e44a4fa1e3d209d64542c0d416e00debc9dea5e`.
The two complete output directories and two 290-line repository-check
transcripts were byte-identical. Literal product and qualification member
inventories, sidecars, installed UAPI and both overlay identities were checked.
The archived probe also compiled against the UAPI extracted from the product.

Adversarial review rejected earlier draft outputs before evidence acceptance:
the first builder lacked required packages, the first target plan named
conceptual helpers that did not exist, and an intermediate transfer plan printed
a digest without enforcing it. The accepted controls contain their invoked
paths, enforce `SHA256SUMS`, require fresh physical-safety confirmation, and
deny mutating target actions unless `--execute` is supplied.

Claim ceiling: reproducible, inventory-verified release artifacts only. No
target was contacted; no module, overlay, GPIO, clock, DMA, transmission, or RF
operation occurred. No tag was created and nothing was published. The next
separate gate is exact-candidate target verification.
