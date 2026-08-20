<!-- SPDX-License-Identifier: MIT -->

# Phase 4C GPIO20 measurement plan

Status: frozen before the first GPIO20 burst

This plan adopts every threshold, receiver setting, detection rule, and
uncertainty limitation from the frozen Phase 4B GPIO4 measurement plan. The
only physical-route change is GPIO20 replacing GPIO4. The user confirmed the
lead move before execution. Drive remains 2 mA, nominal carrier remains
10.140200 MHz, each request remains at most 10 s, and the receiver remains
RSP1B `2404058C60` through two nominal 10 dB attenuators.

Acceptance remains: ten 1 s tones each within 50 ms, duration standard
deviation no more than 25 ms and peak-to-peak no more than 75 ms; FSKCW and
DFCW tone spacing 20 Hz +/- 3 Hz with every boundary within 50 ms; DFCW spaces
present; and STOP output no longer than 1.15 s. Exact DMA divider readback,
four mapped tick-register restoration, GPIO20 input/safe restoration, clock
parent/rate restoration, and balanced counts are mandatory for every row.

Absolute carrier accuracy is `Unavailable` under receiver-relative
calibration. WSPR is `Unavailable` under the 10 s authorization. Neither
limitation changes the frozen timing or relative-spacing thresholds.
