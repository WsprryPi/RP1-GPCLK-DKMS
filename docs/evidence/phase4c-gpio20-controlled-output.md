<!-- SPDX-License-Identifier: MIT -->

# Phase 4C GPIO20 controlled-output evidence

Date: 2026-08-14
Status: GPIO20 limited qualification passed; absolute carrier and WSPR unavailable
Compatibility ceiling: `Experimental`, exact identity only

## Route and identities

The user confirmed the lead had moved before execution. The only live route
was GPIO20 at 2 mA through two nominal 10 dB attenuators into locally attached
SDRplay RSP1B serial `2404058C60`. No GPIO4 output, transmitter, amplifier,
filter, dummy load, splitter, antenna, boot/reboot, package, service, udev,
systemd, or network change occurred.

The target was `wspr5`, Raspberry Pi 5 Model B Rev 1.0, boot ID
`0f9d1f9b-c27b-4e6a-962f-b8e8ac3683d7`, stock kernel
`6.18.34+rpt-rpi-2712`, FDT SHA-256
`e7b48c32347c4862d354c2ed2001590bcd2165a3fa432395c74112095ed77212`.
The exact query reported route 2, ABI 1, capabilities `0xff`, build
`0.0.0-phase4c-gpio20`, compatibility state `Experimental`, and compatibility
ID `phase4c-wspr5-gpio20-6.18.34`. GPIO4 live probe was rejected before an
endpoint was exposed.

Artifact SHA-256 identities were:

- unsigned module:
  `866e8e71b2804f45e464ae2b40d9daaedbf6486b7a67f4c68312d8b5d04707e8`;
- disposable signed module:
  `2ef86f2b85b2ea46872cdf6ee1218df77684bfa68650dcca0ddfc3d033823a0d`;
- UAPI:
  `1d411644352e61402bd4685a5692070d543ab2ee5b016d394294aa98970bd7fb`;
- GPIO20 overlay:
  `8eaa8afae7f88a665fc9bec6da1b013be049b2a32c909c729caeff9181bcf3aa`;
  and
- GPIO4 rejection-probe overlay:
  `c3e17a685694928468bb18c24f5bb4e25454745d6989e6c9d2c2acf447b908d6`.

## Results

| Row | Accepted observation | Decision |
| --- | --- | --- |
| QRSS/TONE timing | Ten runs measured 0.995 s; median and p95 0.995 s; maximum error 5 ms; peak-to-peak 0 at 5 ms resolution | Pass |
| DMA/readback | Thirteen finite requests completed with correct sequencing and exact final fractional-divider readback | Pass |
| Restoration/integrity | All four module-owned mapped tick registers restored exactly after every request; final clock 50 MHz parent `xosc`, all counts zero | Pass |
| FSKCW | Six alternating events, 5.995 s total; adjacent spacing magnitude 19.775-20.142 Hz | Pass |
| DFCW | Four 0.995 s marks and three 0.505 s disabled gaps; adjacent spacing magnitude 19.775-20.142 Hz | Pass |
| STOP/cancellation | `STOPPED`, cleanup fault zero, detected output 0.995 s, kernel elapsed 1.002716067 s, below 1.15 s | Pass |
| Absolute 10.140200 MHz carrier | Receiver-relative calibration only | Unavailable |
| WSPR | Complete frame exceeds the authorized 10 s ceiling | Unavailable |

Neighboring-register integrity is bounded to the complete module-owned mapped
8-byte windows for each of four tick resources. Provider-adjacent clock
registers were not read through unsupported interfaces. Supported evidence is
the exact divider DMA readback and final common-clock parent, rate, and counts.

## Cleanup and archive

The final target had GPIO4 and GPIO20 input, no overlay, module, endpoint, or
installed artifact, and zero clock prepare/enable/protect counts. The signing
private key was removed before sealing. The run-local dmesg delta contains all
13 telemetry rows and no cleanup fault, warning, oops, BUG, or call trace; the
only negative result is expected `-ECANCELED` for STOP.

Portable archive:
`/private/tmp/rp1-gpclk-phase4c-gpio20-evidence.tar.gz`, SHA-256
`9e0d3e5c8fdf9b9f965d34da533a9a96e06409375b5f7a1991defeac690d6114`.
Internal checksums passed in place, after target relocation, and after download
and independent local relocation.
