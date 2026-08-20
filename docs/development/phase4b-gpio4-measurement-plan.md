<!-- SPDX-License-Identifier: MIT -->

# Phase 4B GPIO4 measurement plan

Status: frozen before the first live burst

This plan applies only to GPIO4 on `wspr5`, through the confirmed two 10 dB
attenuators into the locally attached SDRplay RSP1B. Output drive is 2 mA,
nominal carrier is 10.140200 MHz, and each bounded request is at most 10 s.
It does not qualify GPIO20 or WSPR and does not authorize an antenna,
transmitter, amplifier, service change, boot change, or reboot.

## Receiver and analysis

- Use the already-running local SoapyRemote service and RSP1B serial
  `2404058C60`; do not change either service.
- Capture complex samples at 192 ksample/s. The initial center at 10.140200 MHz
  exposed the RSP1B zero-IF/DC notch during FSKCW review, so affected rows are
  recaptured at 10.135200 MHz with the signal expected at +5 kHz. Use AGC
  disabled, fixed 0 dB gain, and the minimum supported 200 kHz bandwidth.
- Each capture contains at least 0.5 s of baseline before and after output.
- Estimate carrier and tone offsets with windowed full-band spectral peaks
  after amplitude gating. Phase-difference averaging is not used because it
  was shown to bias results across modulation transitions. Define onset and
  offset at the first and last 5 ms window whose RMS
  is at least 12 dB above the median pre-burst baseline for three consecutive
  windows. Retain raw IQ and analysis output.

## Frozen acceptance limits

- Sentinel: one 1.0 s QRSS/TONE burst; detected duration error no more than
  50 ms and carrier error no more than 25 Hz.
- Enable/disable timing: ten independent 1.0 s QRSS/TONE bursts. Each duration
  error is no more than 50 ms; duration standard deviation is no more than
  25 ms and peak-to-peak spread no more than 75 ms.
- FSKCW: a separate 6.0 s program alternating 10.140200 MHz and 10.140220 MHz
  in 1.0 s events. Both tones must be detected, measured spacing must be
  20 Hz +/- 3 Hz, every boundary error no more than 50 ms, and total duration
  error no more than 75 ms.
- DFCW: a separate 6.0 s program with 1.0 s marks and 0.5 s clock-disabled
  spaces at the same two tones. Both tones and every space must be detected;
  tone spacing is 20 Hz +/- 3 Hz and each boundary error no more than 50 ms.
- Cancellation: submit an 8.0 s multi-event program, request STOP after 0.5 s,
  and require a stable stopped terminal reason and output no longer than
  1.15 s. Each DMA descriptor is one second so bounded drain is measurable.
- Every run must report exact DMA divider readback equality, restore the
  captured clock rate and all four mapped tick-register values exactly, return
  GPIO4 to input/safe state, and leave clock prepare/enable/protect counts at
  their pre-run values.

WSPR is `Unavailable` in this slice because a standards-conforming WSPR frame
cannot fit the authorized 10 s ceiling. A shortened WSPR program is not
evidence.

## Re-injected source-rate calibration finding

The first otherwise-clean sentinel produced 1.000 s of detected output but
measured 592.3 Hz low against RSP1B `2404058C60`, failing the frozen 25 Hz
limit. Before any retry, the effective parent was frozen at 49,997,080 Hz
(-58.41 ppm relative to nominal 50 MHz) for divider planning. The original IQ,
request, telemetry, and failure decision remain evidence. The ±25 Hz limit is
unchanged; the corrected sentinel and every later row use the frozen effective
parent. This is a route-and-receiver-relative calibration, not an absolute
frequency-standard qualification.

The first corrected retry measured +36.6 Hz when transition samples were
excluded and therefore also failed the unchanged limit. A linear fit through
the two preserved observations froze the final effective parent at 49,997,248
Hz before the next retry. No acceptance limit was changed.

## Re-injected receiver and absolute-frequency findings

The centered captures hid close-in FSKCW energy in the RSP1B zero-IF/DC
notch. Before repeating the affected mode rows, the receiver center was moved
5 kHz low while the transmit frequency, drive, path, sample rate, bandwidth,
gain, and frozen thresholds remained unchanged. Full-band windowed spectral
peaks then preserved signed tone order and spacing without relying on the
notched center bins.

The Pi source and RSP1B were not locked to a traceable common reference. The
preserved calibration retries also wandered by more than the frozen 25 Hz
absolute-carrier limit. Therefore the absolute 10.140200 MHz carrier criterion
is `Unavailable`, not passed and not relaxed. This slice can decide only
receiver-relative duration, transition order, and 20 Hz tone spacing, plus
the module's exact programmed-divider readback.
