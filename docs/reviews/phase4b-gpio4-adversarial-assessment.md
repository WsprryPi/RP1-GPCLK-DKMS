<!-- SPDX-License-Identifier: MIT -->

# Phase 4B GPIO4 adversarial assessment

Date: 2026-08-14
Status: passed; no unresolved objective finding in the bounded GPIO4 scope

## Scope

This review challenges only the bounded GPIO4 conducted qualification. It does
not review or qualify GPIO20, WSPR, absolute-frequency accuracy, intentional
radiation, a transmitter chain, or product-wide RF performance.

## Findings reinjected

1. Parameter-only live eligibility was insufficient. Enrollment now requires
   the exact kernel, Pi model, route, compatibility identity, module version,
   and live parameter; GPIO20 and mismatches fail before output mutation.
2. Cleanup initially restored an incomplete tick snapshot. All four complete
   mapped tick-register pairs are now captured, verified, and restored.
3. SDR selection arguments and startup logging were ambiguous. The capture
   client pins the remote SDRplay serial and emits exact receiver settings and
   a ready marker before submission.
4. Reusing the DMA channel across direction changes caused readback timeout.
   Successful transmit descriptors are synchronously terminated before the
   device-to-memory readback configuration.
5. Pretranslating the peripheral address caused the DMA engine to translate it
   twice. The module now supplies the validated CPU-physical resource address
   expected by the DMA API and retains exact readback telemetry.
6. Immediate tick verification could observe posted writes. Restoration now
   performs bounded exact readback polling and fails closed on timeout.
7. Receiver-relative source calibration could not establish absolute carrier
   accuracy. The 25 Hz threshold was not relaxed; absolute frequency is
   recorded as `Unavailable`.
8. Centered reception hid close-in tones in the RSP1B zero-IF/DC notch. The
   affected rows were repeated with the receiver tuned 5 kHz low and analyzed
   using full-band windowed spectral peaks.
9. DFCW spaces initially left output active. Disabled events now disable the
   clock and select safe input state; the corrected row proved distinct gaps.
10. The module description still claimed a clock-disabled prototype and the
    accepted analysis was not durable. Metadata now describes the experimental
    controlled-output provider and `tests/phase4b_analyze.py` reproduces the IQ
    decisions. This change invalidates earlier module bytes and requires the
    complete final regression and live matrix below.
11. The first durable-analyzer run assumed its first 0.5 s was quiet, but SDR
    readiness did not guarantee that delay. Raw IQ and clean kernel telemetry
    were preserved; baseline selection now uses the capture's quiet-window
    distribution and is validated against the preserved dataset.
12. A whole-boot dmesg capture displayed diagnostics from superseded attempts
    alongside the final run. A run-local delta is now sealed and checked: it
    contains all 13 final telemetry rows, no cleanup fault or kernel fault,
    and only the expected `-ECANCELED` result for STOP.

## Final assertions

The assessment can close only after the exact final bytes pass the offline
suite twice, warnings-fatal exact-kernel build, complete Phase 4A clock-disabled
matrix, GPIO4 eligibility/GPIO20 rejection, QRSS timing repetitions, FSKCW,
DFCW, cancellation, restoration, safe cleanup, and relocated archive checksum.
The final evidence must state the narrower neighboring-register boundary and
must not promote receiver-relative spacing into absolute-frequency evidence.

## Final disposition

The offline suite passed twice before target enrollment and again after runner
hardening. The exact running-header `W=1 KCFLAGS=-Werror` build and complete
Phase 4A clock-disabled target matrix passed. The final uninterrupted GPIO4
matrix passed every frozen receiver-relative timing, relative-spacing, DMA,
readback, cancellation, restoration, and cleanup assertion. The sealed archive
SHA-256 is
`d1c840dd545d77b4435f0f402d89f9140f1c35d2b2a6686708fee161190dddbe`
and verified after two independent relocations.

No unresolved objective finding remains within this limited claim. Absolute
carrier accuracy and WSPR remain `Unavailable`; GPIO20 remains unqualified.
