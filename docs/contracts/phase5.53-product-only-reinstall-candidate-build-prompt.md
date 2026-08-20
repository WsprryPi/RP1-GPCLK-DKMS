<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 product-only reinstall candidate-build prompt

## Objective

Rebuild the development candidate from exact clean commit
`83b1de0e82c30ab4c2781dc941eef0556d6bfede`, which adds ledger-bound complete
removal and product-only same-version reinstall.

## Requirements and exit criteria

- Build twice into new empty directories with `--development`; require complete
  directory byte identity and successful validation of both outputs.
- Extract the product archive and run the installation-model test through its
  packaged administrator while the qualification archive is physically absent.
- Require the test to exercise removal followed by product-only reinstall,
  install both inactive overlays, reject tampered ownership, and install no Gate
  D tool.
- Record exact artifact identities and independently review the result.
- Do not tag, publish, contact a target, run real DKMS, load a module, apply an
  overlay, change GPIO/clock/DMA state, transmit, or perform RF activity.

The next gate is separately authorized target reset and product installation.
