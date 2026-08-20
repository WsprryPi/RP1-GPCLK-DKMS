<!-- SPDX-License-Identifier: MIT -->

# Release 1.0.0 public-download verification review

## Outcome

PASS. On `wspr5`, all eight assets were downloaded directly from the public
`v1.0.0` GitHub Release into one fresh user-owned directory. Their literal
names, sizes, and SHA-256 digests match the published release record. The
published `SHA256SUMS` validates all seven other assets.

The Debian product is a valid `1.0.0-1` `all` package with the exact declared
50-member control/data closure. Its files remain confined to the declared DKMS,
product-support, and product-documentation roots, with no qualification,
evidence, Gate D, or target-verification content.

The separate qualification archive has exactly the declared 16 regular files,
matches its canonical member-inventory digest, and passes its archived offline
control validator. Its target plan remains explicitly unauthorized and
unexecuted.

## Safety and cleanup

This was download-only validation. No package installation or removal, module
or overlay operation, boot change, reboot, GPIO, clock, DMA, transmission, or
RF activity occurred. The isolated verification directory was removed after
the result was captured; the module remained unloaded and the endpoint absent.

## Claim boundary

Release `v1.0.0` is now a publicly downloaded, identity-verified, consumable
module release. This does not claim consumer integration or qualification;
that work remains separately owned by `WSPR-Transmitter` and then `WsprryPi`.
