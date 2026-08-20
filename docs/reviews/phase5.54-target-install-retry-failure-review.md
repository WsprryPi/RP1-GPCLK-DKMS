<!-- SPDX-License-Identifier: MIT -->

# Phase 5.54 target installation retry failure review

Status: safely stopped with the package half-configured.

The exact GPIO4 orphan recovery matched its authorized prestate, deleted only
the bound orphan, and invoked exactly one package retry. Package unpacking then
succeeded. Standard `dh-dkms` built and installed the module for four Raspberry
Pi stock-kernel identities, including the running
`6.18.34+rpt-rpi-2712` kernel.

Configuration failed because unconstrained DKMS autoinstall also selected the
installed historical `6.18.44-v8-16k+` development kernel. Its build link is
the custom `/home/pi/rpi-linux-phase6g` tree, which contains a different
same-path `include/uapi/linux/rp1_gpclk.h`. That header shadowed the package's
canonical UAPI and produced the first compiler error at
`include/rp1_gpclk/core.h:65` for undefined `RP1_GPCLK_MAX_TONES`.

This is not evidence that the running stock-kernel build failed. It is a
package policy defect: a stock-kernel-only product allowed DKMS autoinstall to
attempt an out-of-contract historical custom kernel. The package must express
and test its supported kernel-name scope through the conventional DKMS
configuration, without deleting the user's kernel or maintaining a custom
kernel dependency.

The module and endpoint remain absent and no overlay is active or
boot-selected. Both package-owned inactive DTBOs and the canonical versioned
UAPI are present with exact hashes. The staged package remains intact. No
second retry, package repair, kernel removal, module activity, or hardware/RF
work was performed.

The next slice is offline only: repair and test the DKMS kernel-selection
contract, produce a new package revision and hash, and define an exact
half-configured-package recovery. Target repair requires separate authorization.
