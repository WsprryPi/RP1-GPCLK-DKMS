<!-- SPDX-License-Identifier: MIT -->

# Gate C wspr5 version/kernel build matrix

## Outcome

Three explicitly authorized disposable, module-only builds passed on `wspr5`:

| Version | Source commit | Stock headers | Module SHA-256 | Vermagic |
| --- | --- | --- | --- | --- |
| `0.0.0-phase5.2` | `a1aed8cbb3e717758dcf34f1b35a9fb3c781ca2a` | `6.18.34+rpt-rpi-2712` | `0c99658d7e096600adbe194805f76e6d371d078856d49d38eda05f5f497cab69` | `6.18.34+rpt-rpi-2712 SMP preempt mod_unload modversions aarch64` |
| `0.0.0-phase5.2` | `a1aed8cbb3e717758dcf34f1b35a9fb3c781ca2a` | `6.12.75+rpt-rpi-2712` | `bf8f46cca459fe33e6c8ba82cb06a9bb29159eb57b5981714df9baf32e298be8` | `6.12.75+rpt-rpi-2712 SMP preempt mod_unload modversions aarch64` |
| `0.0.0-phase5.13` | `61ee2ea592c2551eca56fd0566fef43097b8c682` | `6.12.75+rpt-rpi-2712` | `635596b1c9b30490564583152956f3c9404063de3b87a65be9eed8b4bd70857f` | `6.12.75+rpt-rpi-2712 SMP preempt mod_unload modversions aarch64` |

Every build exited zero, produced the expected AArch64 relocatable module,
retained UAPI SHA-256
`1d411644352e61402bd4685a5692070d543ab2ee5b016d394294aa98970bd7fb`,
and emitted no warning, error, or modpost diagnostic. All results remain
`Compatible-unqualified` with `liveEligible: false`.

## Frozen inputs

The predecessor archive was
`rp1-gpclk-dkms-0.0.0-phase5.2.tar.gz`, SHA-256
`f334853d9c94d733ea22e9b7b93961a005e63442ec4efc4edbe2b12d6321aaf4`.
The successor archive was
`rp1-gpclk-dkms-0.0.0-phase5.13.tar.gz`, SHA-256
`58cb12864b291380fefd31ea9a203f7ee308767790787e3fce0be352dab19b14`.

For `6.18.34`, the kernel-config SHA-256 was
`d5ba966d17d456a6f29e53baf53464e1fd53f9f8e31481da18f2221f1da2593d`
and `Module.symvers` SHA-256 was
`681e9fe5710e43c785b39c9e9f410a860cba6a6037e51af23a408cb5ccbe2426`.
For `6.12.75`, the corresponding values were
`2e36192aee8bf4d919bcdae59f67600f3d4ec2a5d4b1e4701b0a305c730ae019`
and `851d09a0f49aab4bfb2ea13be7f6db890eb0b7332b17db783fa021fbe1e90503`.

## Evidence and cleanup

- Predecessor/current evidence:
  `/home/pi/gate-c-evidence/predecessor-6.18.34-a1aed8cbb3e7`, evidence-manifest
  SHA-256 `63d5897038ce6540ab0adc72f7c05906de8fb406472642089e3d6ae0011beadc`.
- Predecessor/prior evidence:
  `/home/pi/gate-c-evidence/predecessor-6.12.75-a1aed8cbb3e7`, evidence-manifest
  SHA-256 `28bc78af0e0c0442012d6103fe43aa1e87a29c87455216b14ff5b5edd0c2ff10`.
- Successor/prior evidence:
  `/home/pi/gate-c-evidence/successor-6.12.75-61ee2ea592c2`, evidence-manifest
  SHA-256 `d776902a7ae485a7da040a86645b018f0561fd3a4dc31dcd2ff7c1b511f6eedd`.

Every file in all three retrieved evidence copies passed its recorded checksum.
The retained target directories and files are read-only. All three exact
disposable build directories were removed. The module and platform driver were
absent before and after the work.

The files named `build-end-utc.txt` were recorded during evidence collection
after the three short builds had completed, not immediately at compiler exit.
They bound the overall capture interval but must not be interpreted as build
duration measurements. Exit status and build output are independently
recorded.

No DKMS registration, package or module installation, signing, loading,
binding, overlay, service, boot, reboot, GPIO, clock, DMA, transmitter,
Si5351, SDR, antenna, or RF action occurred.
