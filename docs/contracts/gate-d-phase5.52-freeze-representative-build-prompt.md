<!-- SPDX-License-Identifier: MIT -->

# Phase 5.52 freeze and representative-build execution prompt

Freeze `0.0.0-phase5.52` from the exact prior-kernel initial-preflight ordering
successor committed through
`970e27da145287c53d36c13d0dd938c2ffd52d69`. Advance only active release
identities and gates. Preserve every Phase 5.51 control, authorization,
staging, successful attempt, sealed failure, snapshot, build record, and
evidence artifact unchanged.

Before accepting the freeze, run the focused initial-preflight regression, all
negative trust cases, and the complete offline suite with the exact Phase 5.51
archive. Commit and push the clean source freeze, then generate the release
twice from independent detached worktrees of that exact commit using its commit
timestamp as `SOURCE_DATE_EPOCH`. Require byte-identical seven-file release
inventories and archives. Validate both release units and rerun the
self-contained permanent-executor regression from the extracted candidate
archive before any representative build.

Reject missing, extra, duplicate, AppleDouble, Finder metadata, extended
attributes, VCS metadata, caches, links, special files, and every path outside
the exact expected target inventory.

On wspr5, require stock `6.18.34+rpt-rpi-2712`, canonical matching headers and
compiler, inactive controlled services and runtime, absent Phase 5.52 and
Phase 5.51 DKMS registrations and route overlays, an absent unique Phase 5.52
build destination, disconnected and unused separate I2C Si5351 path, no
antenna, unused SDR, and available recovery. Preserve all Phase 5.51 staging,
qualification, journal, and attempt evidence unchanged. Use absolute
`/usr/sbin/dkms`, `/usr/sbin/modinfo`, and `/usr/sbin/modprobe` paths.

Transfer only the exact seven regular release files without host metadata.
Enumerate and validate the target build destination before and after transfer.
Compile the module and two bounded UAPI helpers against the identified headers.
Do not install or load the module. Capture commands, identities, hashes,
warnings, module metadata, archive inventory, archived executor regression,
and pre/post target state. Independently validate every retained file and the
final inactive state, then commit and push only attributable evidence.

This slice establishes source freeze, deterministic archive identity,
exact-entrypoint archive compatibility, and representative stock-kernel build
compatibility only. Do not generate Gate D lifecycle controls, request or
consume lifecycle authorization, stage lifecycle inputs, administer DKMS,
load or bind a module, apply overlays, mutate services or boot state, reboot,
access GPIO or I2C, enable clocks, submit DMA, operate Si5351 or SDR hardware,
connect an antenna, transmit, or produce RF.
