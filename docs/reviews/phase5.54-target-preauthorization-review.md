<!-- SPDX-License-Identifier: MIT -->

# Phase 5.54 target preauthorization review

Status: PASS at the read-only preauthorization ceiling.

Two consecutive read-only captures of `wspr5` were byte-identical. They bind
the unchanged boot, kernel, terminal Phase 5.53 ledger, exact DKMS
registration, absent module and endpoint, no active or boot-selected RP1 GPCLK
overlay, six inactive controlled services, absent Phase 5.54 Debian package,
and absent qualification ledger.

The installed GPIO4 and GPIO20 DTBO hashes already equal the Phase 5.54 package
members. That does not permit them to be adopted in place: the Phase 5.53
ledger owns them, so its authenticated removal must remove them and `dpkg`
must reinstall and own the identical bytes.

The successor path has one package-manager transaction rather than a second
custom installer. Every path-bearing consumer was reconstructed from the
literal `.deb`: `dh-dkms` consumes the versioned source closure and
`dkms.conf`; qualification later consumes the UAPI in that same closure; both
route choices consume package-owned DTBOs. No global UAPI or qualification
path is assumed.

The Phase 5.53 remover intentionally leaves its terminal removed ledger. That
file is preserved as transition audit evidence, not treated as Phase 5.54
package state. The later lifecycle-control reconstruction must consume `dpkg`
and DKMS ownership directly and must not reuse the old complete-ledger snapshot
contract.

No target transfer or mutation occurred. The exact authorization phrase in
the accompanying prompt is required before the one removal and one inactive
installation. Any final recapture mismatch or package failure stops the slice
without improvised cleanup.
