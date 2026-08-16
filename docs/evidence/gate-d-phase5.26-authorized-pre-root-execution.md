<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.26 authorized pre-root execution

## Outcome

The operator authorized the exact output-disabled Phase 5.26 Gate D execution
on 2026-08-16. Immediate preflight confirmed `wspr5`, Raspberry Pi 5 revision
`c04170`, AArch64 stock kernel `6.18.34+rpt-rpi-2712`, exact normal and prior
boot-artifact hashes, no module, endpoint, overlay, candidate DKMS state,
candidate root, administrator state, or prior Phase 5.26 staging.

An independent SDRplay capture was active. The execution stopped and waited
without disturbing it. After it ended naturally, the exact release and
67-file control-set input graph were staged below
`/home/pi/gate-d-inputs/phase5.26-9f009240eecd`. Release checksums and the
authenticated pre-root dry validation passed. The authorized privileged
pre-root bootstrap then began.

## Blocking failure

The bootstrap failed at the administrator `install` checkpoint before DKMS
registration. Frozen `rp1-gpclk-admin.py` calls its strict installation-path
resolver for `/lib/modules/6.18.34+rpt-rpi-2712/build`. On the representative
stock Raspberry Pi system that path is the normal kernel-header symlink into
`/usr/src`; the resolver rejects any symlink component with:

```text
ValueError: refusing symlink installation path:
/lib/modules/6.18.34+rpt-rpi-2712/build
```

This is a packaged administrator defect. It is not kernel, header, DKMS,
route, or target-identity drift. The frozen Phase 5.26 candidate must not be
patched or bypassed in place. A successor must safely validate the canonical
header-build-directory resolution and receive a new freeze, representative
build, control set, and authorization.

## Evidence and cleanup

The failure journal SHA-256 is
`b37ce7d136a7b8e7256e9696ac4c8ec2c5c65c2c8296826ba98a0801de1c252c`.
Its exact captured bytes are retained in
[`gate-d-phase5.26-pre-root-failure-journal.txt`](gate-d-phase5.26-pre-root-failure-journal.txt).
It records `administratorInvoked: true`, checkpoint `install`, status
`recovery-required`, and `liveOutput: false`. The only other residue was the
exact qualification-root marker with expected SHA-256
`3a0165ea5084f8cc01c4fa2ed37760d266be662e22f08df508c624d94cbd8f39`.
There was no administrator transaction, DKMS registration, package path,
module, endpoint, overlay, or service drift.

Both evidence objects were copied into the preserved test-owned staging area
and retrieved. Their hashes were verified before the exact marker, empty root,
and pre-root journal were removed. Final checks passed: no candidate DKMS
state, administrator state, qualification root, module, endpoint, or overlay;
the four named services matched their preflight states. The staged input and
failure-evidence directory remain preserved for review.

No module was loaded or bound. No overlay was applied. No helper, GPIO,
pinctrl, GPCLK, clock, DMA, Si5351, transmitter, antenna, or RF action
occurred. None of the 38 lifecycle attempts began.
