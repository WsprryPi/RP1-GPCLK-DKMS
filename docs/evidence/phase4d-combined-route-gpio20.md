<!-- SPDX-License-Identifier: MIT -->

# Phase 4D combined-route GPIO20 evidence

Date: 2026-08-14
Status: GPIO20 combined-candidate qualification passed; Phase 4 remains open
Compatibility ceiling: `Experimental`, exact identity only

The exact combined candidate enrolled GPIO4 and GPIO20 on `wspr5`, but GPIO4
received only a safe UAPI query. All output used GPIO20 at 2 mA through two
nominal 10 dB attenuators into RSP1B `2404058C60`. The target was Raspberry Pi
5, boot ID `0f9d1f9b-c27b-4e6a-962f-b8e8ac3683d7`, stock kernel
`6.18.34+rpt-rpi-2712`, and FDT SHA-256
`e7b48c32347c4862d354c2ed2001590bcd2165a3fa432395c74112095ed77212`.
Query reported build `0.0.0-phase4d-combined`, compatibility ID
`phase4d-wspr5-combined-6.18.34`, and capabilities `0xff` on each route.

Exact SHA-256 identities were unsigned module
`03877f92cd82dec3cdeb85a0efcba132b15304e3605736379fdb3ce166ae1cc0`,
signed module `e2364beba172ccdf61eb599b4afba79eee6d2b56ba81bdb0b9be1f9cab4561c6`,
UAPI `1d411644352e61402bd4685a5692070d543ab2ee5b016d394294aa98970bd7fb`,
GPIO4 overlay `c3e17a685694928468bb18c24f5bb4e25454745d6989e6c9d2c2acf447b908d6`,
and GPIO20 overlay
`8eaa8afae7f88a665fc9bec6da1b013be049b2a32c909c729caeff9181bcf3aa`.

| Row | Observation | Decision |
| --- | --- | --- |
| QRSS/TONE | Ten runs: 0.990-0.995 s; standard deviation 1.5 ms; peak-to-peak 5 ms | Pass |
| FSKCW | Six alternating events; spacing magnitude 19.775-20.142 Hz | Pass |
| DFCW | Four 0.995 s marks; three 0.505 s gaps; expected tone order | Pass |
| STOP | Terminal `STOPPED`; cleanup zero; kernel elapsed 1.002588 s | Pass |
| WSPR | 110.63 s detected; requested 110.592 s; fitted spacing 1.4683 Hz; all 162 golden-vector symbols correct; maximum residual 0.242 Hz | Pass |
| DMA/readback | Fourteen requests; exact final divider readback and owned tick-window restoration | Pass |
| Final restoration | Both pins input; GPCLK0 50 MHz from `xosc`; prepare, enable, and protect counts zero; no module, overlay, endpoint, or installed artifact | Pass |
| Absolute RF accuracy/power | Receiver-relative observation only; no calibrated reference | Unavailable |

The whole-run reconstructed delta contains exactly 14 telemetry lines and no
BUG, warning, oops, call trace, cleanup failure, or nonzero cleanup result.
Services were not changed; WsprryPi remained active and the pre-existing
SoapySDRServer process remained present.

Portable archive:
`/private/tmp/rp1-gpclk-phase4d-gpio20-evidence.tar.gz`, SHA-256
`4d458e77f8fc4208e8485ff53ede89b265c1a5910dbf49b45ad684804b524fab`.
Its internal `SHA256SUMS` identity is
`8d52839dcca68facf7100f9a203dc3f4394b9b361121a40f60e3e9c83cf13813`;
the downloaded archive passed independent listing verification.

Phase 4 remains open until GPIO4 repeats the complete matrix, including WSPR,
using these exact combined-candidate bytes. Earlier GPIO4 evidence used a
different route-specific module and cannot fill that final matrix row.
