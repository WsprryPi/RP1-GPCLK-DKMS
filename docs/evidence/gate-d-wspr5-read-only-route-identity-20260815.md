<!-- SPDX-License-Identifier: MIT -->

# Gate D wspr5 read-only route identity

## Scope and outcome

On 2026-08-15 the operator authorized read-only SSH discovery of `wspr5`.
Commands read only procfs, sysfs, the live device tree, package metadata, and
boot files. No file was written and no package, DKMS, signing, module, overlay,
service, boot, reboot, GPIO, clock, DMA, transmitter, Si5351, SDR, antenna, or
RF action occurred.

The evidence supports route-specific `Compatible-unqualified` decisions for
GPIO4 and GPIO20 with `liveEligible: false`. It does not authorize installation
or binding. Every future attempt must repeat the fail-closed conflict and
identity preflight immediately before mutation; this read-only snapshot cannot
prove that no dynamic consumer will appear later.

## System, kernel, firmware, and signing

- Host: `wspr5`; Raspberry Pi 5 Model B Rev 1.0; revision `c04170`;
  AArch64.
- Running kernel: `6.18.34+rpt-rpi-2712`, Debian image package
  `1:6.18.34-1+rpt1`.
- Matching headers: `linux-headers-6.18.34+rpt-rpi-2712`
  `1:6.18.34-1+rpt1`.
- Compiler recorded by Gate C: GCC 14.2.0, Debian `14.2.0-19`.
- Firmware: 2025-05-08 release `69471177`, commit
  `69471177ba7e4cb7597cb2496f2a0b23f19c1113`.
- Installed base DTB SHA-256:
  `e67017e5d45b97af478ebc93d651a086f2adcb6a650fe453eb9f1cf47e66473f`.
- Live device-tree property-set digest:
  `c18f993d24dc67ba118d459cc30292b80b8caf9d56eb08600443251b09f19f71`.
- Kernel config SHA-256:
  `d5ba966d17d456a6f29e53baf53464e1fd53f9f8e31481da18f2221f1da2593d`.
- `Module.symvers` SHA-256:
  `681e9fe5710e43c785b39c9e9f410a860cba6a6037e51af23a408cb5ccbe2426`.
- `CONFIG_MODULE_SIG`, `CONFIG_MODULE_SIG_FORCE`, `CONFIG_MODULE_SIG_ALL`,
  and `CONFIG_SECURITY_LOCKDOWN_LSM` are unset; `modules_disabled=0`; no
  lockdown interface was exposed. This is the non-enforcing signing-policy
  identity, not evidence for a signature-enforcing system.

The prior stock image and headers `6.12.75+rpt-rpi-2712`
`1:6.12.75-1+rpt1` are installed. Their config SHA-256 is
`2e36192aee8bf4d919bcdae59f67600f3d4ec2a5d4b1e4701b0a305c730ae019`
and `Module.symvers` SHA-256 is
`851d09a0f49aab4bfb2ea13be7f6db890eb0b7332b17db783fa021fbe1e90503`.
This inventory does not establish a predecessor build or prior-kernel positive
compatibility decision.

## Provider and resource identity

The live clock provider is
`/axi/pcie@1000120000/rp1/clocks@18000`, compatible
`raspberrypi,rp1-clocks`, with one clock cell and register property bytes
`000000c0400180000000000000010038`. The platform device
`1f00018000.clocks` is bound to stock driver `rp1-clk`.

The live DMA provider is `/axi/pcie@1000120000/rp1/dma@188000`, compatible
`snps,axi-dma-1.01a`, with one DMA cell, eight channels, status `okay`, and
register property bytes `000000c0401880000000000000001000`. Platform device
`1f00188000.dma` is bound to `dw_axi_dmac_platform`.

The live GPIO/pinctrl provider is `/axi/pcie@1000120000/rp1/gpio@d0000`,
compatible `raspberrypi,rp1-gpio`, bound to `pinctrl-rp1`. Its GPIO4 and
GPIO20 groups both name function `gpclk0` and pins `gpio4` and `gpio20`
respectively. Candidate DTBO identities remain:

- GPIO4: `c3e17a685694928468bb18c24f5bb4e25454745d6989e6c9d2c2acf447b908d6`.
- GPIO20: `8eaa8afae7f88a665fc9bec6da1b013be049b2a32c909c729caeff9181bcf3aa`.

## Conflict and residue observations

The active boot configuration selects `vc4-kms-v3d` and the conditional CM5
`dwc2` overlay only. It contains no GPCLK, WsprryPi, GPIO4, or GPIO20 route
selection. The live tree contains no `wsprrypi` or `rp1-gpclk-dkms`
compatible endpoint, no reference to either route-group phandle, no GPCLK0
clock reference, and no RP1 DMA TICK0 request reference. The module and its
platform driver are absent.

An unowned historical file
`/boot/firmware/overlays/rp1-gpclk-provider.dtbo` exists with SHA-256
`d3d42232d3bbd43b9bf376ceb130b5c3607639e57d6569131c09fc4a37b83e30`.
It is not selected by the boot configuration and has no live-tree endpoint.
It must be preserved as unrelated historical state and rechecked by future
preflight; it does not satisfy the genuine pre-existing-conflict row.

Retained `kernel_2712_phase6h.img` and `kernel_2712_phase6x.img` files also
exist but are not selected by the active configuration. They are historical
administrator artifacts, not Gate D inputs or test-owned residue.

## Authorized stock-kernel boot discovery

A later read-only discovery on 2026-08-15 resolved the exact reversible
stock-kernel inputs. Normal `config.txt` has SHA-256
`b6218fd92bd231151f177029b0dfd84a2af1e92f94dac768bd9501af087d43e2`.
The unrelated historical `tryboot.txt` has SHA-256
`c06b262332c145a0cfea594e020fced762a02eef269e4026fe84de71fb152b0a`
and selects the custom `kernel_2712_phase6h.img` plus provider overlay; Gate D
must preserve it and never use tryboot.

The package-owned prior stock kernel is
`/boot/vmlinuz-6.12.75+rpt-rpi-2712`, SHA-256
`c194093a665071826ff94fb014b574de8ad896584b7317bbeafefe94154b0b44`.
Its generated initramfs is `/boot/initrd.img-6.12.75+rpt-rpi-2712`, SHA-256
`e3d47bcb88e0a0ed9cb338832fc1ac503d423692ab49842134c68677dc505068`.
The current normal firmware kernel and initramfs hashes match the versioned
`6.18.34` files. The reviewed selector therefore stages only digest-bound
test-owned copies on the firmware partition, atomically appends a marked
temporary selection to `config.txt`, restores its exact original bytes after
the prior-kernel row, and removes only those copies. Discovery made no change.
