<!-- SPDX-License-Identifier: MIT -->

# Phase 5.50 freeze and representative-build execution prompt

Freeze `0.0.0-phase5.50` from the schema-6 preauthorization repair committed
at `0588cc89a74b8f51d65b779cafb36fc185e9cf54`. Advance only active release
identities and gates. Preserve every Phase 5.49 contract, control draft
assessment, snapshot, build record, and evidence artifact unchanged. The only
control behavior change is execution-instance schema 6: it binds
`attemptSchemaVersion=2`, permits a consistent unapproved/not-ready control
state, and preserves schema 1 through 5 behavior.

Run focused and complete offline validation, commit and push the clean source
freeze, then generate the release twice from independent detached worktrees of
that exact commit. Require byte-identical seven-file release inventories and
archives. Reject missing, extra, duplicate, AppleDouble, Finder metadata,
extended attributes, VCS metadata, caches, links, special files, and every
path outside the exact expected target inventory.

On wspr5, require the stock `6.18.34+rpt-rpi-2712` kernel, canonical matching
headers and compiler, inactive controlled services and runtime, absent Phase
5.50 DKMS registration and overlays, an absent unique build destination,
disconnected and unused separate I2C Si5351 path, no antenna, unused SDR, and
available recovery. Use absolute `/usr/sbin/dkms` and `/usr/sbin/modinfo`
paths. Do not retry a bare `modinfo` or `dkms` command.

Transfer only the exact seven regular release files without host metadata.
Before compiling, enumerate the target destination and fail on any unexpected
file. Compile the module and two bounded UAPI helpers against the identified
headers. Capture commands, identities, hashes, warnings, module metadata,
archive inventory, and pre/post target state. Enumerate the target destination
again, independently validate every retained file and final inactive state,
then commit and push only attributable evidence.

This slice establishes source freeze, deterministic archive identity, and
representative build compatibility only. Do not generate Gate D controls,
request lifecycle authorization, stage lifecycle inputs, install or load
DKMS, bind or unbind, apply overlays, mutate services or boot state, access
GPIO or I2C, enable clocks, submit DMA, operate Si5351 or SDR hardware, connect
an antenna, transmit, or produce RF.
