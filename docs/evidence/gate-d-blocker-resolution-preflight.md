<!-- SPDX-License-Identifier: MIT -->

# Gate D blocker-resolution preflight

## Sealed version pair

The byte-complete, offline-validated package inputs are frozen in
`release/gate-d-version-pair-v1.json`. `packageComplete` means the exact
package input and ownership model are complete; it does not claim a target
installation or rollback has passed.

Predecessor:

- version `0.0.0-phase5.2`;
- commit `a1aed8cbb3e717758dcf34f1b35a9fb3c781ca2a`;
- archive SHA-256 `f334853d9c94d733ea22e9b7b93961a005e63442ec4efc4edbe2b12d6321aaf4`.

Successor:

- version `0.0.0-phase5.13`;
- commit `61ee2ea592c2551eca56fd0566fef43097b8c682`;
- archive SHA-256 `58cb12864b291380fefd31ea9a203f7ee308767790787e3fce0be352dab19b14`;
- UAPI SHA-256 `1d411644352e61402bd4685a5692070d543ab2ee5b016d394294aa98970bd7fb`;
- manifest SHA-256 `1817bbc56512c0b6adb77bb4d1341eae71615489fd511486229b699b62616eda`;
- GPIO4 DTBO SHA-256 `c3e17a685694928468bb18c24f5bb4e25454745d6989e6c9d2c2acf447b908d6`;
- GPIO20 DTBO SHA-256 `8eaa8afae7f88a665fc9bec6da1b013be049b2a32c909c729caeff9181bcf3aa`;
- release-layout SHA-256 `227ad55b00d1d179d56af0c8e6c6a347a885abfeb523e16f92969572ebb6b557`.

Two independent successor generations were byte-identical and passed release
validation. A read-only copy is retained in ignored local directory
`dist/gate-d-successor-61ee2ea592c2/`; it is neither committed nor published.

## Busy-state injector

The separately sealed, non-package injector identities are:

- source SHA-256 `1bebe7cd10be210a2dcedb9de3db701888f40c38f3210470d777b69bcf5b7582`;
- header SHA-256 `03aaa6a1c1dfd901b54dc6b2434f1913157a6b80e991b56c42a6e1da332f8fd8`;
- macOS fixture-build binary SHA-256
  `f61b0fe71c5059456d96f3ef45ee983ff212f6bed69fca00b5eb37b3b324f767`.

The binary hash is compile evidence only and is not a Linux target artifact.
A future authorized target attempt must compile from the sealed source with the
recorded target compiler and bind that new binary hash before execution.

## Validation and remaining blockers

The complete offline suite passed twice from a detached clean worktree at the
exact successor commit; transcripts are `gate-d-offline-61ee2ea-pass1.txt` and
`gate-d-offline-61ee2ea-pass2.txt`.

Only stale-manifest and corrupted-archive/DTBO inputs are presently ready. The
other 13 rows remain blocked by one or more of:

- no exact positive successor manifest entry;
- no exact positive predecessor entry for the required kernel;
- no genuinely newer installed stock kernel;
- no signature-enforcing representative system;
- no installed representative kernel lacking headers; or
- no identified genuine pre-existing foreign resource conflict.

No matrix row has executed and `--require-ready` correctly fails.
