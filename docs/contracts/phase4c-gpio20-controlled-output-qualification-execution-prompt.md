<!-- SPDX-License-Identifier: MIT -->

# Phase 4C GPIO20 controlled-output qualification execution prompt

## Mission and authorization

Qualify GPIO20 only on `wspr5` using the exact conducted route confirmed by
the user on 2026-08-14:

```text
GPIO20 -> 10 dB attenuator -> 10 dB attenuator -> RSP1B 2404058C60
```

Use 2 mA drive, nominal 10.140200 MHz, and individually bounded bursts no
longer than 10 s. No transmitter, amplifier, filter, dummy load, splitter,
antenna, or other conductor is authorized. Do not change boot configuration,
reboot, alter services, change packages, or produce GPIO4 output. Gate B
continues to permit the disposable module, overlay, signing, build, and
evidence lifecycle needed for this test.

The previously accepted GPIO4 result is historical prerequisite evidence, not
GPIO20 evidence. Absolute carrier accuracy remains deferred: this slice may
qualify receiver-relative timing and tone spacing but must record absolute
10.140200 MHz accuracy as `Unavailable`. WSPR remains `Unavailable` because a
complete frame exceeds the authorized 10 s ceiling.

## Exact-byte entry gate

1. Begin from clean synchronized commit
   `5f30b282a0256a3dae6f5066d893eaba0be7efa8`.
2. Create a new module/build/compatibility identity whose live allowlist
   admits only GPIO20 on the exact Raspberry Pi 5 and stock
   `6.18.34+rpt-rpi-2712` identity.
3. Prove GPIO4 live enrollment rejects before an endpoint is exposed.
4. Run the complete offline suite twice and an exact-header
   `W=1 KCFLAGS=-Werror` build.
5. Repeat the complete Phase 4A clock-disabled two-route target matrix against
   the exact live-candidate bytes with `live_output=0`.
6. Require both pins input, no endpoint/module/overlay, and zero common-clock
   counts immediately before live enrollment.

Any implementation change invalidates later artifacts and requires all
affected gates to repeat.

## Frozen measurement plan

Reuse the pre-observation thresholds and analysis method in
`docs/development/phase4b-gpio4-measurement-plan.md`, changing only the route
from GPIO4 to GPIO20. Capture complex CF32 at 192 ksample/s using the local
SoapyRemote RSP1B, fixed 0 dB gain, AGC off, 200 kHz bandwidth, and receiver
center 10.135200 MHz to avoid the zero-IF notch. Select the quiet-window
distribution for amplitude gating and use windowed full-band spectral peaks.

Required independent rows are:

- ten 1 s QRSS/TONE timing repetitions;
- one 6 s alternating 20 Hz FSKCW sequence;
- one 6 s DFCW sequence with four 1 s marks and three 0.5 s disabled gaps;
- one 8 s finite request stopped after 0.5 s, with output no longer than
  1.15 s; and
- WSPR recorded `Unavailable`, with no shortened substitute.

For every request require exact final-divider readback, complete four-window
tick snapshot/restoration, finite descriptor ordering, one terminal reason,
cleanup fault zero, GPIO20 returned to input, clock rate/parent restored, and
balanced prepare/enable/protect counts. Neighboring-register claims remain
limited to the complete module-owned mapped tick windows and supported
common-clock observations; do not use `/dev/mem` or unsupported MMIO.

## Evidence, adversarial loop, and exit

Preserve raw IQ, request/client output, exact hardware/kernel/boot/FDT/route/
drive/module/UAPI/overlay/SDR identities, per-request kernel telemetry,
run-local dmesg delta, safe-state snapshots, signing certificate, checksums,
and every failed attempt. Remove the private signing key before sealing.

After execution, independently challenge eligibility, route isolation, timing
statistics, tone/gap decisions, cancellation, DMA readback, restoration,
neighboring-register scope, historical-log contamination, archive portability,
and final cleanup. Reinject every objective finding and repeat affected work.

Phase 4C passes only when the exact final bytes pass every gate, the relocated
archive verifies independently, the target is absent/safe, and the final
assessment has no unresolved objective finding. Commit and push only then.
