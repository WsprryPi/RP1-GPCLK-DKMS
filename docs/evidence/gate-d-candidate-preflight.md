<!-- SPDX-License-Identifier: MIT -->

# Gate D candidate and representative-input preflight

## Disposition

Candidate `0.0.0-phase5.2` is frozen for controlled Gate D testing from source
commit `a1aed8cbb3e717758dcf34f1b35a9fb3c781ca2a`. It is not tagged, published,
download-verified, live-qualified, or consumable. The concrete instance remains
`executionReady: false`: five rows have complete declared inputs and ten rows
remain blocked. No target row has executed.

This evidence is intentionally committed after the frozen source commit. That
later evidence commit does not become the candidate and must not be passed to
the release builder as a replacement source identity.

The candidate was generated twice from the clean commit with Python 3.14.7 and
DTC 1.8.1. Both independently generated artifact sets were byte-identical and
both passed release validation. A read-only local sealed copy is retained below
the ignored `dist/gate-d-candidate-a1aed8cbb3e7/` directory; it is not committed
or published.

The complete offline suite then passed twice from a detached clean worktree at
the exact source commit. The durable transcripts are
`gate-d-offline-a1aed8c-pass1.txt` and
`gate-d-offline-a1aed8c-pass2.txt`. The host was macOS, so the three explicitly
Linux-only UAPI-client compile checks were skipped; the portable UAPI contract
and Gate D probe compiled and passed.

## Frozen identities

- archive: `rp1-gpclk-dkms-0.0.0-phase5.2.tar.gz`
- expected future tag: `v0.0.0-phase5.2` (absent)
- archive SHA-256: `f334853d9c94d733ea22e9b7b93961a005e63442ec4efc4edbe2b12d6321aaf4`
- UAPI SHA-256: `1d411644352e61402bd4685a5692070d543ab2ee5b016d394294aa98970bd7fb`
- compatibility manifest SHA-256: `49bb49ecd89fe2f5fe1405215ffe1b0000ebc7226743df2ad111c8eaa73c0bd5`
- GPIO4 source SHA-256: `0860a4c67d6977bbc041725675f8fa602d8aed0cc9a155aabae8f847a12a1cd6`
- GPIO4 DTBO SHA-256: `c3e17a685694928468bb18c24f5bb4e25454745d6989e6c9d2c2acf447b908d6`
- GPIO20 source SHA-256: `fa6fdeef8ca68a6c04123290c50dc5455c8ac685e34f511aee893fd99ecc8098`
- GPIO20 DTBO SHA-256: `8eaa8afae7f88a665fc9bec6da1b013be049b2a32c909c729caeff9181bcf3aa`
- release-layout SHA-256: `e1d07edad9253be7c44b6ae61e0c35b5b773e38f5a8de3240be669f8a2a60087`
- claim ceiling: controlled-test candidate; `Unavailable` for live operation

## Row readiness

Ready inputs, not executed evidence:

- signing-not-enforced;
- stale-manifest;
- corrupted-archive-or-dtbo;
- removal-inactive; and
- reinstall-after-removal.

Blocked inputs and disposition:

- current-supported-kernel: the generated manifest has no exact positive entry;
  a separately accepted representative build decision is required.
- prior-supported-kernel-downgrade, deliberate-build-failure, and
  interrupted-upgrade: a distinct retained predecessor and successor version
  pair is not frozen. This requires a separately designed test predecessor; it
  cannot be invented by relabeling identical bytes.
- newer-unknown-kernel: a genuinely newer installed stock Pi 5 kernel identity
  is unavailable. This requires another real stock-kernel identity.
- signing-enforced-enrolled-key and deliberate-signature-rejection: no stock
  signature-enforcing representative system is available. The non-enforcing
  wspr5 state cannot substitute.
- missing-headers: no installed representative kernel without matching headers
  exists. Removing the known-good headers solely to manufacture the condition
  is not authorized by this preflight.
- overlay-or-resource-conflict: no qualifying pre-existing foreign owner has
  been identified. The row may inspect a real conflict but must not create or
  disturb unrelated ownership merely to obtain a pass.
- removal-open-or-active: the exact output-disabled open-descriptor/busy-owner
  target injector and evidence procedure remain to be frozen.

`wspr4` is not RP1 hardware and cannot satisfy any missing RP1 representative
identity. One wspr5 kernel or signing policy is not counted as a genuinely
different identity.

## Safety and authorization boundary

This preflight performed no SSH, package, DKMS, module, overlay, service, boot,
reboot, GPIO, clock, DMA, transmitter, SDR, antenna, or RF action. It changed no
consuming repository. Candidate tagging, publication, fresh-public-download
verification, and consumer integration remain unauthorized and incomplete.
