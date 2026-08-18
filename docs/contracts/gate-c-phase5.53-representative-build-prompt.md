<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 split-artifact representative-build prompt

Build the exact frozen Phase 5.53 product candidate from source commit
`1884c0f1c53c661495576bf10ce08d8bf7a90bc3` on representative host `wspr5`
against stock kernel `6.18.34+rpt-rpi-2712` and its canonical matching headers.
Bind the work to product archive SHA-256
`ae6df3a66a9a26a6fb8474e5896c9053b9f69580d8c45383a5556fc397ebb549`
and separately retain and verify qualification archive SHA-256
`8bd6eff31a90b95c43372d96bac47a4c6fe92b74de92da10e58d99a8ed63c052`.

Before transfer, require an inactive baseline: controlled services inactive,
module and endpoint absent, no selected route overlay, no Phase 5.53 DKMS
registration, and an absent unique build destination. Verify the exact eight-
file split release unit and transfer only regular files without host metadata.
On the target, re-enumerate and hash the release unit, verify `SHA256SUMS`, then
extract only the product archive for the module build. Prove that ordinary
product compilation does not read or install qualification tooling. Compile
the module and the two bounded UAPI helpers against the identified headers.

Capture the kernel, headers, compiler, architecture, source, archives, UAPI,
module, helpers, tool-source hashes, warnings, module version/license/vermagic,
ELF identity, and pre/post state. Independently verify the retained release
files and require the final target state to remain inactive.

This slice proves representative stock-kernel build compatibility only. Do not
run DKMS add/build/install/remove, install or load a module, apply an overlay,
change services or boot state, reboot, access GPIO or I2C, enable clocks,
submit DMA, operate Si5351 or SDR hardware, connect an antenna, transmit, or
produce RF. Do not advance `representative-lifecycle-matrix`; retain its gate
as blocked until every separately authorized matrix row passes.
