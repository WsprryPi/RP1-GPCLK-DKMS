<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.14 target-input sealing adversarial assessment

## Outcome

The target-input sealing slice stopped fail-closed before installation. The
frozen Phase 5.14 archive and both DTBOs were staged and checksum-sealed, and
the read-only target refresh completed. Disposable compilation then proved the
frozen archive cannot build its release-owned busy injector because required
header `tools/gate_d_busy_injector.h` is absent from the archive.

Phase 5.14 therefore cannot advance to Gate D installation or lifecycle
authorization. This is a candidate packaging defect, not an environmental
target failure and not something an unsealed supplemental file may repair.

## Read-only refresh

- Host: `wspr5`, Raspberry Pi 5 Model B Rev 1.0, revision `c04170`, AArch64.
- Running kernel: `6.18.34+rpt-rpi-2712`.
- Firmware: 2025-05-08 release `69471177`.
- Live FDT SHA-256:
  `e7b48c32347c4862d354c2ed2001590bcd2165a3fa432395c74112095ed77212`.
- Existing sealed boot-file identities still match the target plan.
- Matching headers exist for both planned stock kernels. An additional
  `6.18.44-v8-16k+` kernel and headers are installed but were neither selected
  nor treated as qualified.
- No Gate D overlay is active. GPIO4 and GPIO20 are unclaimed in the refreshed
  GPIO ownership report.
- `wsprrypi`, `sdrplay`, and `SoapySDRServer` are active;
  `sdrconnect-server` is inactive, matching the plan.
- The module, platform driver, and device endpoint are absent.
- The module-signing enforcement sysctl is absent and the running kernel
  configuration exposes no enabled `CONFIG_MODULE_SIG`,
  `CONFIG_MODULE_SIG_FORCE`, or `CONFIG_MODULE_SIG_ALL` entry.

## Staged immutable inputs

Target directory:
`/home/pi/gate-d-inputs/phase5.14-7bbdfe1b5c83`, mode `0555`.

- Archive SHA-256:
  `d0c17f2842716052bb49b1a4fc079d3d48a5674bae8610eee2ab9d17ac548bea`.
- GPIO4 DTBO SHA-256:
  `c3e17a685694928468bb18c24f5bb4e25454745d6989e6c9d2c2acf447b908d6`.
- GPIO20 DTBO SHA-256:
  `8eaa8afae7f88a665fc9bec6da1b013be049b2a32c909c729caeff9181bcf3aa`.
- Target `SHA256SUMS` SHA-256:
  `5efc69c2b977ee9c41d46478c57a9555ee7424f5956d6421d59a59deef2d8ec0`.

All three staged bytes verified after cleanup and remain read-only.

## Blocking finding

The exact reviewed compile command failed before producing a binary:

```text
tools/gate_d_busy_injector.c:16:10: fatal error:
gate_d_busy_injector.h: No such file or directory
```

`scripts/build_release.py` explicitly excluded the header while the Phase 5.14
installer was changed to compile and install the busy injector. The ordinary
module representative build did not exercise that installer-owned helper
path, so its prior success does not close this finding.

The partial helper-build and partial evidence directories were inspected and
removed exactly. No helper executable was produced or run. The sealed input
directory was retained. No package or tool was installed; no DKMS, module,
overlay, service, boot, reboot, GPIO, clock, DMA, Si5351, transmitter, SDR,
antenna, or RF action occurred.

## Required correction

Create a new successor rather than changing frozen Phase 5.14 in place. The
new candidate must include the busy-injector header, add a release test that
compiles both permanent helpers strictly from the generated archive, pass
offline adversarial review and deterministic double-build, then receive a new
representative build and a new bounded target-input sealing authorization.
