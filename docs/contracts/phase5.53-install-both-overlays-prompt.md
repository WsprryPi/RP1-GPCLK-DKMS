<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 install-both-overlays prompt

## Objective

Install both allowlisted inactive overlay artifacts during every product
installation so changing between GPIO4 and GPIO20 never requires rebuilding or
reinstalling the DKMS module.

## Requirements

- Require checksum-valid `rp1-gpclk-gpio4.dtbo` and
  `rp1-gpclk-gpio20.dtbo` artifacts before starting the transaction.
- Install both under `/boot/firmware/overlays` with root ownership semantics
  and mode `0644`, recording each newly installed file in the transaction.
- Refuse a symlink or a pre-existing overlay whose bytes differ. Preserve an
  already installed byte-identical artifact.
- Do not apply either overlay, edit boot configuration, reboot, load the
  module, or access GPIO, clock, DMA, transmission, or RF resources.
- Keep route selection and route-specific qualification separate from product
  installation. Update the installation model, operator documentation, tests,
  and adversarial review.

## Exit criteria

Offline installation tests must prove both overlays are present after one
product-only transaction, no qualification artifact is required, and a
foreign artifact on either route fails closed without replacement.
