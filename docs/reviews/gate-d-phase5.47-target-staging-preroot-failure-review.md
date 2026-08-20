<!-- SPDX-License-Identifier: MIT -->

# Phase 5.47 target-staging failure independent review

Status: failed closed during unprivileged staging verification. No pre-root
transition or lifecycle attempt began.

The immediate live-target recapture was exactly 7,057 bytes and byte-identical
to canonical snapshot SHA-256
`7f018fb331c769c44eb1691fdabc4a8a6ff22e0a3debc9e1ed69404d829332b0`.
Target-side validation and the local independent comparison against the sealed
envelope, predecessor inventory, route decision, and representative build all
passed.

All 62 declared input hashes passed before transfer. The staging transport was
then constructed with the macOS archive tool. Although its member listing did
not contain AppleDouble entries, the archive carried macOS extended-attribute
metadata. GNU tar on wspr5 warned about `LIBARCHIVE.xattr.com.apple.provenance`
and materialized undeclared `._*` regular files. The complete archive-derived
target path-set comparison rejected those extras before the archived executor
or privileged transition ran.

The newly created Phase 5.47 staging directory and transient capture and
verification files were removed. The Phase 5.47 qualification root and
pre-root journal remain absent. Post-cleanup inspection found no loaded module,
endpoint, or overlay, no candidate DKMS test version, and all six services
inactive.

The next successor must replace the macOS metadata-bearing transport with a
bounded metadata-free transfer whose locally enumerated regular-file set is
identical to the target extraction. It must re-run the canonical recapture and
all staging verification from the beginning; this failed slice does not
authorize continuation from partial state.

A separate negative-content review of the sealed release archive found no
AppleDouble `._*` members. The unwanted files therefore came from the staging
transport, not the frozen release archive. The successor must nevertheless
reject AppleDouble files, `.DS_Store`, VCS metadata, editor backups, caches,
bytecode, and every path absent from the independently derived allowlist both
before transfer and after target extraction.

No GPIO operation, active pinctrl, clock enablement, DMA submission, Si5351 or
SDR operation, antenna connection, transmission, or RF occurred.
