<!-- SPDX-License-Identifier: MIT -->

# Phase 5.32 ledger-backed recovery execution prompt

Recover only the preserved Phase 5.32 administrator-owned residue created by
the authorized pre-root failure on `wspr5`. This authorization does not extend
to Phase 5.33 implementation, freezing, staging, installation, or lifecycle
attempts.

Before mutation, require the immutable pre-root journal to remain
`recovery-required`, checkpoint `install`, `liveOutput=false`; require the
administrator transaction to remain `inactive-recovery-required` with exact
kernel, package, version, owned-file hashes, symlink targets, and owned
directories; require the module and endpoint absent and no route overlay active.

Invoke only the exact recovery command declared by the Phase 5.32 envelope:

```text
/usr/bin/python3 /home/pi/gate-d-inputs/phase5.32-4e62b3a0b584/extracted/rp1-gpclk-dkms-0.0.0-phase5.32/scripts/rp1-gpclk-admin.py recover --execute
```

The administrator must authenticate every ledger-owned file and symlink before
deleting it, run bounded exact-version DKMS uninstall/removal, remove only
verified owned paths and empty owned directories, and commit its journal as
`recovered`, checkpoint `inactive-clean`, `recoveryRequired=false`.

Afterward require Phase 5.32 DKMS status empty; source, installed module,
release-data, module, endpoint, and overlay absent; retained Phase 5.31 tools
unchanged; services unchanged; and `liveOutput=false`. Preserve the pre-root
failure journal, administrator recovery journal, staging, and historical
qualification root as evidence.

Stop on any identity or cleanup discrepancy. Do not manually remove files,
patch journals, invoke outer transition resume, load modules, activate overlays,
change services or boot state, reboot, access GPIO, enable clocks, submit DMA,
operate Si5351, transmitter, or SDR, connect an antenna, transmit, or produce RF.
