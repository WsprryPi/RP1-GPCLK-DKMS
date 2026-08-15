<!-- SPDX-License-Identifier: MIT -->

# Proposed Gate C successor build authorization

This is a proposed authorization dossier, not authority to contact `wspr5`.
Fill the successor commit and artifact hashes only after candidate sealing, then
obtain an explicit operator approval before SSH or build work.

The proposed operation is a disposable, output-disabled representative build
on `wspr5` using stock kernel `6.18.34+rpt-rpi-2712`, matching installed headers,
the recorded kernel configuration and `Module.symvers`, GCC 14.2.0, and exact
successor archive `0.0.0-phase5.13`. Permitted writes are one new user-owned
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
