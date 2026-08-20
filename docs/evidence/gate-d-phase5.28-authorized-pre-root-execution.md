<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.28 authorized pre-root execution

## Outcome

The operator authorized the exact output-disabled Phase 5.28 Gate D execution
on 2026-08-16. The repository authorization binding was committed as
`4f03b14`. Target preflight confirmed `wspr5`, AArch64 stock kernel
`6.18.34+rpt-rpi-2712`, no module, endpoint, overlay, candidate DKMS state,
source tree, transaction, or qualification root.

All 67 Phase 5.28 input files and every release sidecar matched the sealed
control hashes below `/home/pi/gate-d-inputs/phase5.28-9c408ec493ab`. Release
checksum verification passed. The authenticated pre-root dry validation passed
with `outputDisabled=true`, `readOnly=true`, and `valid=true`. Privileged
bootstrap then began, accepted the bounded canonical `/lib` alias and final
kernel-header `build` symlink, registered the candidate with DKMS, and completed
the DKMS build.

## Blocking failure

Bootstrap failed before module installation or any lifecycle attempt. DKMS
3.2.2 compressed the built module and produced:

```text
/var/lib/dkms/rp1-gpclk-dkms/0.0.0-phase5.28/6.18.34+rpt-rpi-2712/aarch64/module/rp1_gpclk_dkms.ko.xz
```

The frozen Phase 5.28 administrator instead required the uncompressed path
ending in `rp1_gpclk_dkms.ko`. Its `modinfo -F version` check therefore failed
closed with:

```text
modinfo: ERROR: Module .../rp1_gpclk_dkms.ko not found.
```

The target also contained `Module.symvers` in that DKMS module directory. This
is a bounded DKMS built-module path/format discovery defect, not target identity
drift and not a build-compatibility failure.

## Evidence and cleanup

The preserved target evidence below the staging directory has these SHA-256
values:

- failed administrator transaction: `3241b3204a9d6aa14b4bcae49d23313a9a04c3e1772b419b6b089c0ef46a9dad`
- qualification-root marker: `2be8bbeb82c53d7dbe715de870365ff21f387e34092beb778aac5453ef40dd69`
- recovered administrator transaction: `31cb555ce3af3ba44cfeb5070007d35966f769ea8a2baefae6cf27718e2eafbc`

The exact Phase 5.28 administrator recovery removed the candidate DKMS and
owned source state. The recovered transaction and qualification root were then
removed after evidence preservation. Final checks found no candidate DKMS
entry, source tree, transaction, qualification root, module, endpoint, or
overlay. Services returned to `wsprrypi=active`, `sdrplay=active`,
`sdrconnect-server=inactive`, and `SoapySDRServer=active`.

None of the 38 lifecycle attempts began. No module was loaded or bound, no
overlay was activated, and no GPIO, clock, DMA, Si5351, transmitter, SDR,
antenna, or RF operation occurred. Phase 5.28 must not be patched or bypassed
in place; a new successor requires bounded, fail-closed recognition and
verification of the DKMS-built module representation, a new freeze,
representative build, control set, and authorization.
