<!-- SPDX-License-Identifier: MIT -->

# Gate C successor build authorization and disposition

The operator explicitly approved this exact dossier on 2026-08-15. The build
completed under that authority; its durable disposition is recorded in
[`../evidence/gate-c-representative-build-wspr5-phase5.13.md`](../evidence/gate-c-representative-build-wspr5-phase5.13.md)
and `release/gate-c-representative-build-manifest-v1.json`.

The proposed operation is a disposable, output-disabled representative build
on `wspr5` using stock kernel `6.18.34+rpt-rpi-2712`, matching installed headers,
the recorded kernel configuration and `Module.symvers`, GCC 14.2.0, and exact
successor commit `61ee2ea592c2551eca56fd0566fef43097b8c682`, archive
`rp1-gpclk-dkms-0.0.0-phase5.13.tar.gz`, and archive SHA-256
`58cb12864b291380fefd31ea9a203f7ee308767790787e3fce0be352dab19b14`.
Permitted writes are one new user-owned
temporary source/output directory and one immutable evidence directory.

The proposed evidence records archive, UAPI, configuration, `Module.symvers`,
headers, compiler, architecture, module SHA-256, version, vermagic, unresolved
symbols, namespace/modpost output, commands, UTC and monotonic times, bounded
output, exit status, and cleanup. The claim ceiling is
`Compatible-unqualified`, `liveEligible: false`.

The operation must not register with DKMS, install packages, sign, enroll a key,
load or bind the module, apply an overlay, change a service or boot file, reboot,
touch GPIO/clock/DMA/transmitter/Si5351/SDR/antenna/RF state, or select a
fallback. Cleanup removes only the disposable build directory after evidence
is sealed.

Until the exact filled dossier is approved and its build evidence accepted, no
positive compatibility decision may be added.
