<!-- SPDX-License-Identifier: MIT -->

# Gate C representative build: wspr5 / 0.0.0-phase5.13

## Outcome

The explicitly authorized disposable build passed on `wspr5`. Exact successor
archive `58cb12864b291380fefd31ea9a203f7ee308767790787e3fce0be352dab19b14`
at source commit `61ee2ea592c2551eca56fd0566fef43097b8c682` built with exit status
zero against stock kernel and headers `6.18.34+rpt-rpi-2712`. The build log
contains no compiler or modpost warning or error diagnostic.

The resulting 57,448-byte AArch64 module has SHA-256
`3aee571fde3cb0d74eda4a0128ae1110796f2bb7be035d974c30b38cfafc749d`,
version `0.0.0-phase5.13`, license `Dual MIT/GPL`, and vermagic
`6.18.34+rpt-rpi-2712 SMP preempt mod_unload modversions aarch64`.

This evidence establishes only `Compatible-unqualified` build compatibility,
with `liveEligible: false`. It is route-neutral and does not satisfy a
route-specific compatibility-manifest entry or any Gate D lifecycle row.

## Exact inputs and evidence

- Pi: Raspberry Pi 5 Model B Rev 1.0, revision `c04170`, AArch64.
- Compiler: GCC 14.2.0, Debian `14.2.0-19`.
- Header packages: `linux-headers-6.18.34+rpt-rpi-2712` and
  `linux-headers-rpi-2712`, both `1:6.18.34-1+rpt1`.
- Kernel config SHA-256:
  `d5ba966d17d456a6f29e53baf53464e1fd53f9f8e31481da18f2221f1da2593d`.
- `Module.symvers` SHA-256:
  `681e9fe5710e43c785b39c9e9f410a860cba6a6037e51af23a408cb5ccbe2426`.
- UAPI SHA-256:
  `1d411644352e61402bd4685a5692070d543ab2ee5b016d394294aa98970bd7fb`.
- Evidence UTC interval: `2026-08-15T19:00:22Z` through
  `2026-08-15T19:00:51Z`.
- Target evidence directory:
  `/home/pi/gate-c-evidence/phase5.13-61ee2ea592c2`.
- Evidence-manifest SHA-256:
  `339c32513378bdf54d618cab1eeed65df904a29e20d30f7ad1a9ca8e757a0371`.

The target evidence directory is retained mode `0555` with its files mode
`0444`. A retrieved review copy passed every checksum in that manifest.
`modinfo` was unavailable and was not installed; equivalent module version,
license, name, dependency, and vermagic fields were recorded directly from
the ELF `.modinfo` section.

## Cleanup and prohibited activity

The exact disposable directory
`/home/pi/gate-c-build-phase5.13-61ee2ea592c2` was removed after evidence
capture. Pre- and post-build checks recorded the module absent from live module
and platform-driver state. No DKMS registration, package installation, module
installation, signing, loading, binding, overlay, service, boot, reboot, GPIO,
clock, DMA, transmitter, Si5351, SDR, antenna, or RF activity occurred.

## Adversarial finding

The current kernel-config digest differs from the historical Phase 4 digest
`2a83d4324e9b47d418b4efac18d3af43d15cc956b71c5a8eb074060bf8383801`
in the existing exclusion entries. Those old runtime identities must not be
copied into a successor entry. The machine-readable build decision therefore
remains explicitly route-neutral and non-live. Route-specific lifecycle work
still requires a separately reviewed compatibility-manifest decision and all
distinct representative-system inputs.
