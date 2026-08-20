<!-- SPDX-License-Identifier: MIT -->

# Phase 4B GPIO4 controlled-output evidence

Date: 2026-08-14
Status: GPIO4 limited qualification passed; absolute carrier and WSPR unavailable
Compatibility ceiling: `Experimental`, exact identity only

## Authorized path and identity

The only live path exercised was GPIO4 at 2 mA through two user-confirmed
10 dB attenuators into the locally attached SDRplay RSP1B serial
`2404058C60`. No transmitter, amplifier, filter, dummy load, splitter, or
antenna was connected. Each burst was at most 10 s. GPIO20 was not driven and
the lead was not moved. No boot, reboot, package, service, udev, systemd, or
network change was made.

The accepted target was `wspr5`, Raspberry Pi 5 Model B Rev 1.0, stock kernel
`6.18.34+rpt-rpi-2712`, boot ID
`0f9d1f9b-c27b-4e6a-962f-b8e8ac3683d7`. The live query required route GPIO4,
ABI 1, capabilities `0xff`, build `0.0.0-phase4b-gpio4`, compatibility state
`Experimental`, and compatibility ID
`phase4b-wspr5-gpio4-6.18.34`. GPIO20 live enrollment was explicitly rejected
with `-EOPNOTSUPP` and exposed no endpoint.

The final unsigned module SHA-256 is
`ea3a702739245745da072b3731ef40bd2224e90419df804b0b500f6fd4c909c2`;
the disposable signed module SHA-256 is
`511d61e1aaca51715e81cf6d380aedfd9d4ea1d2a6941a46b2609ef28f977077`.
The UAPI SHA-256 is
`1d411644352e61402bd4685a5692070d543ab2ee5b016d394294aa98970bd7fb`;
the GPIO4 and GPIO20 overlay SHA-256 values are respectively
`c3e17a685694928468bb18c24f5bb4e25454745d6989e6c9d2c2acf447b908d6`
and `8eaa8afae7f88a665fc9bec6da1b013be049b2a32c909c729caeff9181bcf3aa`.
The FDT SHA-256 is
`e7b48c32347c4862d354c2ed2001590bcd2165a3fa432395c74112095ed77212`.
The pre-metadata-hardening archive was
`/private/tmp/rp1-gpclk-phase4b-gpio4-evidence.tar.gz`, SHA-256
`5e5069bcd68b422211a113563d8abe8f1af056f89574b0aab20fe1fdfa464115`;
it is retained as superseded evidence.

## Results

| Row | Accepted observation | Decision |
| --- | --- | --- |
| QRSS/TONE timing | 10 runs measured 0.995-1.000 s; median 0.995 s, p95 0.99775 s, max error 5 ms, standard deviation 1.5 ms, peak-to-peak 5 ms | Pass |
| DMA sequencing/readback | Finite descriptors completed in order; every run reported exact final fractional-divider readback | Pass |
| Restoration/integrity | All four module-owned mapped tick registers restored exactly; GPIO4 returned input; clock returned to 50 MHz `xosc`, prepare/enable/protect counts zero | Pass |
| FSKCW | Six alternating events, 5.995 s total; adjacent measured spacings 19.775 to 20.508 Hz in magnitude | Pass |
| DFCW | Four 0.995 s marks, three 0.505 s clock-disabled gaps; adjacent tone spacing 19.775 to 20.142 Hz in magnitude | Pass |
| STOP/cancellation | STOPPED terminal reason, cleanup fault zero, detected output 0.995 s and kernel elapsed 1.003 s, below 1.15 s | Pass |
| Absolute 10.140200 MHz carrier | Pi and RSP1B lacked a traceable common reference; preserved retries exceeded the frozen 25 Hz limit | Unavailable |
| WSPR | A standards-complete frame exceeds the authorized 10 s burst ceiling | Unavailable |
| GPIO20 | No physical move or live burst occurred | Not qualified |

Neighboring-register integrity is limited to the complete module-owned mapped
8-byte windows for each of the four tick resources. Provider-adjacent clock
registers were not exposed or read through unsupported means; the supported
evidence for that boundary is exact programmed-divider DMA readback plus final
common-clock parent, rate, and reference counts. No `/dev/mem`, raw userspace
MMIO, or private kernel-symbol fallback was used.

## Cleanup and retained evidence

After every accepted row and at final exit, GPIO4 and GPIO20 were inputs, no
overlay was loaded, the module and endpoint were absent, the installed module
was removed, and common-clock counts were zero. The disposable signing private
key was removed before sealing. Raw CF32 IQ, requests, client terminal states,
kernel telemetry, identities, dmesg deltas, restoration state, checksums, and
failed/superseded attempts were retained. `tests/phase4b_analyze.py` reproduces
the accepted duration, relative-spacing, DFCW-gap, and cancellation decisions.

Final archive:
`/private/tmp/rp1-gpclk-phase4b-gpio4-final6-evidence.tar.gz`, SHA-256
`d1c840dd545d77b4435f0f402d89f9140f1c35d2b2a6686708fee161190dddbe`.
Its internal checksums passed on `wspr5`, after target-side relocation, and
after download and independent local relocation. The final run-local dmesg
delta contains 13 expected telemetry rows and no cleanup fault, warning, oops,
BUG, or call trace. Its sole negative result is `-ECANCELED` for the requested
STOP row, whose UAPI terminal reason is `STOPPED` with cleanup fault zero.
