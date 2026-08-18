<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 product-only target reset/install authorization prompt

## Objective

Permit one bounded replacement of the inactive Phase 5.52/earlier Phase 5.53
development installation on `wspr5` with the rebuilt Phase 5.53 product-only
candidate. This decision is non-authorizing until the operator supplies the
exact phrase below.

## Exact identities

- decision commit: `f293955585d3b95efd893dec2c1d376fde4fc7ea`;
- product source commit: `83b1de0e82c30ab4c2781dc941eef0556d6bfede`;
- product archive SHA-256:
  `d014e60f7a76d6c5b178ff5bec4caa1d4978f4a9fd0a2a6a5552614c7d6b2276`;
- GPIO4 DTBO SHA-256:
  `c3e17a685694928468bb18c24f5bb4e25454745d6989e6c9d2c2acf447b908d6`;
- GPIO20 DTBO SHA-256:
  `8eaa8afae7f88a665fc9bec6da1b013be049b2a32c909c729caeff9181bcf3aa`;
- release metadata SHA-256:
  `3801b1a7079c241dc85078dc07dbb740feb0548d136c62d4cc5567967bbbcb27`;
- checksums SHA-256:
  `3b9582a105b2218a9a6d16d0829c1e78d33d9ee8e083a3064549fda1e5c3548d`.

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
> inactive installation on wspr5 bound to decision commit
> f293955585d3b95efd893dec2c1d376fde4fc7ea and product archive
> d014e60f7a76d6c5b178ff5bec4caa1d4978f4a9fd0a2a6a5552614c7d6b2276,
> beginning with final read-only recapture and, only if it passes, exactly one
> ledger-bound removal and one product-only development installation with both
> inactive overlays. I do not authorize qualification tooling, module load,
> overlay activation, reboot, GPIO/clock/DMA activity, transmission, or RF.

Until that exact phrase is supplied, do not contact or mutate the target.
