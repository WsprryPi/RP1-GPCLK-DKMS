<!-- SPDX-License-Identifier: MIT -->

# Phase 5.29 DKMS module-representation successor execution prompt

Create distinct successor `0.0.0-phase5.29` for frozen Phase 5.28, whose exact
source built successfully on `wspr5` but whose administrator failed closed
because DKMS 3.2.2 emitted `rp1_gpclk_dkms.ko.xz` rather than the assumed
uncompressed `.ko` path. Preserve every Phase 5.28 artifact and failure record.

After a successful DKMS build, resolve the built module only from the exact
DKMS output directory bound to package, successor version, running kernel, and
architecture. Allow exactly one regular, non-symlink module named
`rp1_gpclk_dkms.ko`, `.ko.xz`, `.ko.gz`, or `.ko.zst`. Reject absence,
ambiguity, other suffixes, symlinks, non-regular files, and path escape. Pass
the resolved representation directly to `modinfo`; retain exact version,
vermagic, signer, and key-ID checks. Do not decompress, copy, rename, glob an
unbounded path, or weaken installed-module verification.

Add deterministic positive tests for each allowlisted representation and
negative tests for ambiguity, symlinks, directories, unknown compression, and
absence. Run the complete offline suite and a separate adversarial assessment;
correct every actionable finding and repeat affected checks.

Commit the implementation, freeze that exact clean commit with two isolated
byte-identical development release builds, and record exact identities. Then
perform an exact build-only representative compile on `wspr5`. Do not install,
load, bind, apply an overlay, access GPIO, enable a clock, submit DMA, operate
the separate I2C Si5351 path, touch a transmitter or SDR, connect an antenna,
or produce RF. Preserve services and pre-existing state.

Stop after the representative-build result. A new Phase 5.29 Gate D route
decision, target plan, attempt bundle, execution instance, pre-root envelope,
and explicit lifecycle authorization are later gates. Do not tag, publish,
open a pull request, or modify dependent repositories. Report hashes, checks,
target observations, cleanup, commit and push state, and the remaining gate.
