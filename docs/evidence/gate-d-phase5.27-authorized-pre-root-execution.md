<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.27 authorized pre-root execution

## Outcome

The operator authorized the exact output-disabled Phase 5.27 Gate D execution
on 2026-08-16. The repository was clean and synchronized at control-set commit
`5f19ae7a3b6c30e9d6da954cfc0ba53363c5a90c`. Target preflight confirmed
`wspr5`, AArch64 stock kernel `6.18.34+rpt-rpi-2712`, no module, endpoint,
overlay, candidate DKMS state, source tree, or qualification root. A historical
Phase 5.26 inactive transaction was recovered with its frozen administrator,
preserved, and removed before Phase 5.27 staging.

All 67 Phase 5.27 input files and every release sidecar matched the sealed
control hashes below `/home/pi/gate-d-inputs/phase5.27-bfb927256317`. The
authenticated pre-root dry validation passed with output disabled. Privileged
bootstrap then began.

## Blocking failure

Bootstrap failed before DKMS registration. The Phase 5.27 administrator's
kernel-header resolver first calls the generic symlink-free resolver for
`/lib/modules/6.18.34+rpt-rpi-2712`. On this stock Raspberry Pi OS image,
`/lib` is the standard symlink to `usr/lib`; the generic resolver therefore
fails before evaluating the separately supported final `build` symlink:

```text
ValueError: refusing symlink installation path:
/lib/modules/6.18.34+rpt-rpi-2712
```

`namei` confirmed `/lib -> usr/lib`, a real
`/usr/lib/modules/6.18.34+rpt-rpi-2712` directory, and
`build -> ../../../src/linux-headers-6.18.34+rpt-rpi-2712`, resolving to the
root-owned mode-0755 `/usr/src/linux-headers-6.18.34+rpt-rpi-2712` directory.
This is a second bounded canonical-path defect, not target identity drift.

## Evidence and cleanup

The preserved target evidence SHA-256 values are:

- failed administrator transaction: `9708055c3c999df8fe433ae4cda3491a0156a01dc23f61508775876bbedab31c`
- qualification-root marker: `7d864bd85bacf8ebf3eb03e647c805372d09eed38e17e3c1e7b98a87dcdb7d1b`
- recovered administrator transaction: `666773e397c41bb24ae3f51fb3528b05e157de4c5bf5e34bdeb2d66c3631e06d`

Recovery reported no owned files or directories. The exact transaction and
root marker were removed after evidence preservation. Final checks found no
candidate DKMS entry, source tree, transaction, qualification root, module,
endpoint, or overlay. Services returned to `wsprrypi=active`, `sdrplay=active`,
`sdrconnect-server=inactive`, and `SoapySDRServer=active`.

No lifecycle attempt began. No module was loaded or bound, no overlay was
activated, and no GPIO, clock, DMA, Si5351, transmitter, SDR, antenna, or RF
operation occurred. Phase 5.27 must not be patched or bypassed in place; a new
successor requires a bounded canonical `/lib` alias policy, freeze,
representative build, control set, and authorization.
