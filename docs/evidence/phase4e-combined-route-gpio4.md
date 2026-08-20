<!-- SPDX-License-Identifier: MIT -->

# Phase 4E combined-route GPIO4 evidence

Date: 2026-08-14
Status: GPIO4 combined-candidate qualification passed
Compatibility ceiling: `Experimental`, exact identity only

The user confirmed the conducted lead was moved to GPIO4. The route was GPIO4
at 2 mA through two nominal 10 dB attenuators into RSP1B serial `2404058C60`,
with no transmitter, amplifier, filter, splitter, dummy load, or antenna.
GPIO20 enrolled under the combined candidate but received only a safe query.

This run used the same unsigned module SHA-256
`03877f92cd82dec3cdeb85a0efcba132b15304e3605736379fdb3ce166ae1cc0`,
UAPI `1d411644352e61402bd4685a5692070d543ab2ee5b016d394294aa98970bd7fb`,
GPIO4 overlay `c3e17a685694928468bb18c24f5bb4e25454745d6989e6c9d2c2acf447b908d6`,
GPIO20 overlay `8eaa8afae7f88a665fc9bec6da1b013be049b2a32c909c729caeff9181bcf3aa`,
FDT `e7b48c32347c4862d354c2ed2001590bcd2165a3fa432395c74112095ed77212`,
stock kernel `6.18.34+rpt-rpi-2712`, build `0.0.0-phase4d-combined`, and
compatibility ID `phase4d-wspr5-combined-6.18.34` as the GPIO20 run. The
disposable signed-module SHA-256 was
`61afea761dcc465a2415300eda81d2d59b5a11075f0051807d15060b5681c626`.

| Row | Observation | Decision |
| --- | --- | --- |
| QRSS/TONE | Ten 0.995 s runs; no observed spread at 5 ms resolution | Pass |
| FSKCW | Six alternating events; spacing magnitude 19.775-20.142 Hz | Pass |
| DFCW | Four 0.995 s marks; three 0.505 s gaps; expected tone order | Pass |
| STOP | Terminal `STOPPED`; cleanup zero; detected output 0.995 s | Pass |
| WSPR | 110.63 s detected; fitted spacing 1.46426 Hz; all 162 golden-vector symbols correct; maximum residual 0.266 Hz | Pass |
| DMA/readback | Fourteen requests; exact final divider readback and owned tick-window restoration | Pass |
| Final restoration | Both pins input; GPCLK0 50 MHz from `xosc`; all counts zero; no module, overlay, endpoint, or installed artifact | Pass |
| Absolute RF accuracy/power | Receiver-relative observation accepted for Phase 4; calibrated series deferred | Deferred |

The run-local delta passed with exactly 14 telemetry rows and no warning,
oops, BUG, call trace, cleanup failure, or nonzero cleanup result. Services
were unchanged. Portable archive:
`/private/tmp/rp1-gpclk-phase4e-gpio4-evidence.tar.gz`, SHA-256
`bdba7ac3a37c6dfbc1ac006a73b3af3e41f0488b1ef0ad1f96bd7a864dce7e73`.
Its internal manifest SHA-256 is
`7848f7925c3d13a3de1bfbf2fe679e55688e2211be54dae8c1eef18481dc9371`.
The downloaded archive passed independent listing verification.
