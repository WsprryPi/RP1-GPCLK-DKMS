<!-- SPDX-License-Identifier: MIT -->

# Phase 4D combined-route GPIO20 qualification execution prompt

Build one immutable stock-kernel candidate that admits GPIO4 and GPIO20 only
on the exact `wspr5` Raspberry Pi 5 and `6.18.34+rpt-rpi-2712` identity. Prove
both routes enroll under those same bytes, but produce output on GPIO20 only.
GPIO4 is query-only in this slice.

Use the user-confirmed conducted route GPIO20 through two nominal 10 dB
attenuators into RSP1B serial `2404058C60`, with no transmitter, amplifier,
filter, splitter, dummy load, or antenna. Use 2 mA and nominal 10.140200 MHz.
Do not change boot configuration, reboot, packages, services, udev, or systemd.

Run ten 1 s QRSS/TONE repetitions, one 6 s FSKCW sequence, one 6 s DFCW
sequence, one bounded STOP test, and one complete WSPR frame. The WSPR row must
use the canonical 162-symbol `AA0NT EM18 20` vector, 1.46484375 Hz tone
spacing, 110.592 s requested duration, and a 120 s hard bound. Preserve raw IQ,
terminal UAPI state, exact divider readback, all owned tick-window snapshots,
GPIO/clock restoration, identities, run-local diagnostics, and checksums.

Run the complete offline suite before target work. Arm unconditional cleanup.
Afterward, separately challenge route isolation, candidate identity, timing,
jitter, tone order and spacing, all 162 WSPR symbols, cancellation, readback,
neighbor integrity, cleanup, evidence completeness, and archive relocation.
Reinject and correct every finding, re-run the affected work, and repeat until
no objective finding remains. This slice cannot complete Phase 4: GPIO4 must
later pass the same matrix using these exact combined-candidate bytes.
