<!-- SPDX-License-Identifier: MIT -->

# Phase 5.30 installed-module-representation adversarial assessment

Status: implementation review passed; representative build still required

The review challenged kernel identity, canonical `/lib` topology, intermediate
symlinks, directory absence, filename allowlisting, ambiguity, unknown
suffixes, symlinks, non-regular files, and preservation of metadata checks.
The resolver reuses the bounded real kernel-module-tree resolution, walks only
real `updates/dkms` components, and accepts exactly one `.ko`, `.ko.xz`,
`.ko.gz`, or `.ko.zst` regular file. Module-like unknown siblings fail closed.

The resolved path is passed unchanged to the existing version, vermagic,
signer, and key-ID checks. No decompression, copying, renaming, fallback path,
glob expansion, module load, or route widening was introduced. Positive tests
cover all four representations; negative tests cover absence, ambiguity,
unknown compression, symlinks, and directories. The complete offline suite
passed after reinjection.

No target, DKMS installation, module lifecycle, GPIO, clock, DMA, Si5351,
transmitter, SDR, antenna, or RF action was authorized or performed by this
assessment.
