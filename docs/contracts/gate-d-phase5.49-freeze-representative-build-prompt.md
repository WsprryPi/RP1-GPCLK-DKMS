<!-- SPDX-License-Identifier: MIT -->

# Phase 5.49 freeze and representative-build execution prompt

Freeze `0.0.0-phase5.49` from the schema-2 terminal-cleanup repair committed at
`b83377d73a2800b3c563e039df7f6a63ac4a0ffb`. Advance only active release
identities and gates. Preserve every Phase 5.48 contract, control, and evidence
artifact unchanged. The only lifecycle behavior change is the opt-in schema-2
terminal cleanup and authoritative protected-path absence check.

Run focused and complete offline validation, commit and push the clean source
freeze, then generate the release twice from independent detached worktrees of
that exact commit. Require byte-identical seven-file release inventories and
archives with no missing, extra, duplicate, AppleDouble, Finder, VCS, cache,
link, special-file, or extended-attribute content.

On wspr5, require the stock `6.18.34+rpt-rpi-2712` kernel, canonical matching
headers and compiler, inactive services and runtime, absent Phase 5.49 DKMS
registration and overlay, an absent unique build directory, disconnected and
unused separate I2C Si5351 path, no antenna, unused SDR, and available
recovery. Use absolute `/usr/sbin/dkms` and `/usr/sbin/modinfo` paths.

Transfer the exact release without host metadata. Compile the module and the
two bounded UAPI helpers against the identified headers. Record exact source,
archive, inventory, module, helper, kernel, configuration, compiler, UAPI, and
post-state identities. Independently validate the target inventory and final
inactive state, then commit and push only attributable evidence.

This slice establishes a source freeze and representative build only. Do not
generate Gate D controls, request lifecycle authorization, install or load
DKMS, bind or unbind, apply overlays, mutate services or boot state, access
GPIO or I2C, enable clocks, submit DMA, operate Si5351 or SDR hardware, connect
an antenna, transmit, or produce RF.
