<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 product-only target reset/install authorization prompt

## Objective

Permit one bounded replacement of the inactive Phase 5.52/earlier Phase 5.53
development installation on `wspr5` with the rebuilt Phase 5.53 product-only
candidate. This decision is non-authorizing until the operator supplies the
exact phrase below.

## Exact identities

- repaired product source commit: `40b2ffd2fa944511b549737bcf6eb1a199125971`;
- product archive SHA-256:
  `c46cec7641fc7e0aae31a86ce2e9ec78948deb8f22fe55cdfdde34636b2e4d3b`;
- GPIO4 DTBO SHA-256:
  `c3e17a685694928468bb18c24f5bb4e25454745d6989e6c9d2c2acf447b908d6`;
- GPIO20 DTBO SHA-256:
  `8eaa8afae7f88a665fc9bec6da1b013be049b2a32c909c729caeff9181bcf3aa`;
- release metadata SHA-256:
  `6d0be0c91315299fc9e93d8d40e9d48910f570da5fa099965df7c69593d76a7b`;
- checksums SHA-256:
  `484eb6c4c5eccc33c3ca72345051e2d08ed1f743ea80bc351b370841f4cb8c9c`;
- predecessor ledger SHA-256:
  `0261c25f785458a0ee3cd270e4a7afcb606f5a86fdb99fc019aae231388c78f1`;
- predecessor live-closure SHA-256:
  `1eb341e9198a67eb116f4407e9f20c3d68a5258c1c04fbfb7b676ed2d9535eb5`.

The qualification archive is explicitly excluded from staging and deployment.

## Authorized work only after the exact phrase

1. Require the repository to remain clean, synchronized, and at the exact
   decision commit. Rebuild or locate the exact candidate and verify every
   identity above before target contact.
2. Perform one final read-only recapture on `wspr5`. Require the module and
   endpoint absent, no RP1 GPCLK overlay applied or selected in boot
   configuration, terminal output-disabled installation ledger intact, DKMS
   state internally consistent, all controlled services inactive, Si5351 and
   SDR unused, and antenna disconnected. Any mismatch exhausts authorization.
3. Transfer only the product release files needed by the administrator, with
   the qualification archive absent. Reject metadata, links, special files,
   extended attributes, traversal, duplicate names, or any hash mismatch.
4. Extract the exact 54-file product archive into a new target staging path and
   invoke its packaged administrator—not an older installed copy.
5. Run exactly one `remove --execute` against the terminal ledger. It may issue
   only exact-version DKMS uninstall/remove and delete only ledger-authenticated
   installed successors. Stop on any ownership, identity, DKMS, or removal
   discrepancy; do not improvise cleanup.
6. Run exactly one product-only development install using
   `install --execute --allow-development --route gpio4`. It may perform the
   ordinary DKMS add/build/install lifecycle and install both inactive DTBOs.
   It must not use a qualification identity or archive.
7. Verify the terminal ledger, DKMS/module identities, both installed DTBO
   hashes, product files, absence of Gate D tools, absent loaded module and
   endpoint, no applied overlay, inactive services, and removal of transfer
   residue. Record durable evidence and an independent review, then stop.

## Prohibited work and claim ceiling

Do not load or bind the module, apply an overlay, edit boot configuration,
reboot, change GPIO or pinctrl state, enable a clock, submit DMA, operate the
Si5351 or SDR, connect an antenna, transmit, or produce RF. Do not begin any
Gate D lifecycle attempt. Success establishes only an inactive product install;
GPIO4 and GPIO20 remain separately unactivated and unqualified by this slice.

## Exact authorization phrase

> I explicitly authorize the exact Phase 5.53 product-only target reset and
> inactive installation on wspr5 bound to repaired source commit
> 40b2ffd2fa944511b549737bcf6eb1a199125971, predecessor ledger
> 0261c25f785458a0ee3cd270e4a7afcb606f5a86fdb99fc019aae231388c78f1,
> and product archive
> c46cec7641fc7e0aae31a86ce2e9ec78948deb8f22fe55cdfdde34636b2e4d3b,
> beginning with final read-only recapture and, only if it passes, exactly one
> ledger-bound removal and one product-only development installation with both
> inactive overlays. I do not authorize qualification tooling, module load,
> overlay activation, reboot, GPIO/clock/DMA activity, transmission, or RF.

Until that exact phrase is supplied, do not contact or mutate the target.
