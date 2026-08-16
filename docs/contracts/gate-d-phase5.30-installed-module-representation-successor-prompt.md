<!-- SPDX-License-Identifier: MIT -->

# Phase 5.30 installed-module-representation successor execution prompt

Create distinct successor `0.0.0-phase5.30` for frozen Phase 5.29. Its
built-module compression resolution passed on `wspr5`, but bootstrap failed
closed after DKMS installed `rp1_gpclk_dkms.ko.xz` while the administrator
assumed an uncompressed installed `.ko`. Preserve every Phase 5.29 artifact,
control, authorization, staging, and failure record.

After successful DKMS installation, resolve the installed module only beneath
the exact running-kernel `updates/dkms` directory reached through the already
allowlisted canonical `/lib -> usr/lib` topology. Require real, non-symlink
`modules/KERNEL/updates/dkms` components. Allow exactly one regular,
non-symlink module named `rp1_gpclk_dkms.ko`, `.ko.xz`, `.ko.gz`, or `.ko.zst`.
Reject absence, ambiguity, unknown suffixes, symlinks, non-regular files,
unsafe kernel identities, and path escape. Pass the resolved representation
unchanged to the existing version, vermagic, signer, and key-ID checks. Do not
decompress, copy, rename, or broaden discovery.

Add deterministic positive and negative tests for all representations and
failure states. Run the complete offline suite and a separate adversarial
assessment; correct every actionable finding and repeat affected checks.

Commit the implementation, freeze that exact clean commit with two isolated,
byte-identical development release builds, and record all identities. Perform
an exact build-only representative compile on `wspr5`; do not install or load
it. Do not bind, activate overlays, change services or boot state, access GPIO,
enable clocks, submit DMA, operate the separate I2C Si5351 path, touch a
transmitter or SDR, connect an antenna, or produce RF.

Stop after the representative-build result. A new Phase 5.30 Gate D control
set and explicit lifecycle authorization are later gates. Do not tag, publish,
open a pull request, or modify dependent repositories. Report hashes, checks,
target observations, cleanup, commits, push state, and the remaining gate.
