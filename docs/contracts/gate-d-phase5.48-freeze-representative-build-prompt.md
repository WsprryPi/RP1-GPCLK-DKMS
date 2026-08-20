<!-- SPDX-License-Identifier: MIT -->

# Phase 5.48 freeze and representative-build execution prompt

Freeze `0.0.0-phase5.48` from service-snapshot repair commit
`51d330dddd192560f0245734b886318ad03cb946`. Bind the freeze to the fresh,
canonical wspr5 snapshot whose SHA-256 is
`9377d109235305f29e85134026cf9247e5d462b0bd2c8e05d9c0463162156e33`.

Advance only active release identities from Phase 5.47 to Phase 5.48. Preserve
all historical Phase 5.47 evidence and contracts byte-for-byte. Add behavior,
security, snapshot, and review records; reset release gates so the archive and
representative build remain explicit blockers. Run focused checks, the complete
offline suite, whitespace validation, and an adversarial diff review. Commit
and push the source freeze before generating any archive.

From two independent clean exports of the exact freeze commit, generate the
release twice. Require byte-identical archives and inventories. Reject missing,
extra, duplicate, AppleDouble, Finder metadata, extended-attribute, or
out-of-contract files. Inspect the archive contents against the release layout
and record its SHA-256.

On wspr5, require the exact stock kernel, matching headers and compiler,
canonical device-tree aliases, all controlled services inactive, the module,
endpoint, and Phase 5.48 overlays absent, no Phase 5.48 DKMS registration, and
an absent unique build destination. Require the separate I2C Si5351 path to
remain disconnected and unused, no antenna, an unused SDR, and available
recovery. Use absolute `/usr/sbin/modinfo` and `/usr/sbin/dkms` paths.

Transfer the exact release and clean source archive without host metadata.
Compile the module and bounded UAPI helpers against the identified headers.
Capture commands, identities, hashes, warnings, module metadata, archive
inventory, and pre/post target state. Independently validate all evidence and
commit and push only attributable repository records.

This slice establishes source freeze, deterministic archive identity, and
representative build compatibility only. Do not generate Gate D controls,
request or consume lifecycle authorization, stage lifecycle inputs, install or
load DKMS, bind or unbind, apply overlays, mutate services or boot state, drive
GPIO, use I2C or Si5351, enable clocks, submit DMA, operate an SDR, connect an
antenna, transmit, or produce RF.
