<!-- SPDX-License-Identifier: MIT -->

# Phase 4B GPIO4 controlled-output qualification execution prompt

## Mission and hard boundary

Act as kernel-module implementer, safety operator, SDR measurement operator,
test author, evidence custodian, and independent adversarial reviewer for
`WsprryPi/RP1-GPCLK-DKMS`.

Qualify only GPIO4 on the exact `wspr5` stock-kernel identity through the
confirmed direct conducted path. Begin from the accepted Phase 4A commit and
evidence. Implement and validate every correction needed for safe live
enrollment before the first burst. Measure clock timing and jitter; validate
finite DMA sequencing, exact divider readback, STOP/cancellation, restoration,
and neighboring-register integrity; then assess QRSS/TONE and FSKCW/DFCW in
separate evidence rows.

Hard-stop after GPIO4 cleanup and adversarial review. Do not move the lead to
GPIO20. Do not apply the GPIO20 production overlay. Do not qualify or claim
GPIO20. Do not perform intentional radiation or Gate D RF qualification.

The authorized burst ceiling is ten seconds. A standards-complete WSPR frame
is longer than that ceiling, so WSPR is `Unavailable` in this prompt unless the
user separately expands the duration authorization. Do not substitute a
truncated waveform or short parser test for WSPR qualification.

## Exact authorization

The recorded controlled-output authorization is:

> Selected GPIO pin -> 10 dB attenuator -> 10 dB attenuator -> RSP1B, with no
> transmitter, amplifier, filter, dummy load, splitter, or antenna connected.
> GPIO4 first, then physically move the lead and qualify GPIO20 separately;
> 2 mA drive; 10.1402 MHz; bounded test bursts no longer than 10 seconds each;
> no service changes.

For this prompt, “selected GPIO pin” means GPIO4 only. The physical route must
be confirmed immediately before enrollment:

```text
GPIO4 -> 10 dB attenuator -> 10 dB attenuator -> RSP1B serial 2404058C60
```

No transmitter, amplifier, filter, dummy load, splitter, antenna, unlisted
load, or radiating conductor may be connected. The two attenuators must be
identified and their nominal values/orientation recorded. Do not infer that
the conducted connection authorizes on-air emission.

Gate B remains available for the module/overlay lifecycle required by this
test. Gate C permits only the exact GPIO4 conducted output above. No boot
configuration change, reboot, service change, package upgrade, persistent
module enrollment, udev/systemd change, or network reconfiguration is allowed.

## Authoritative inputs and entry identity

Read completely and follow:

1. `AGENTS.md`;
2. `docs/contracts/rp1-gpclk-dkms-module-contract.md`;
3. `docs/contracts/phased-plan.md`;
4. `docs/contracts/uapi-v1.md`;
5. `docs/contracts/phase4-timing-controlled-live-output-execution-prompt.md`;
6. `docs/contracts/phase4a-stock-kernel-live-path-implementation-execution-prompt.md`;
7. Decision 0007;
8. the Phase 4A implementation adversarial assessment and Gate B evidence;
9. canonical UAPI/header identity and compatibility manifests; and
10. exact source history and current worktree state.

The accepted prerequisite is commit
`5258aeff766ffa55f4c2c69a754fc7a9577bb2ce` on
`codex/phase-3-gpio20-interface-freeze`. Phase 4A evidence identifies stock
kernel `6.18.34+rpt-rpi-2712`, boot ID
`0f9d1f9b-c27b-4e6a-962f-b8e8ac3683d7`, UAPI ABI 1, module version
`0.0.0-phase4a`, and RSP1B serial `2404058C60`. Re-measure every drift-prone
identity; do not assume the kernel, boot ID, DT, firmware, SDR, wiring, source,
or worktree is unchanged.

Require a clean, synchronized, reviewed source tree. If implementation changes
are needed, preserve Phase 4A evidence, use a new version/build/compatibility
identity, invalidate every later artifact, and rebuild all evidence from the
new bytes.

## Exit gate

Phase 4B passes only if all of the following are true for GPIO4:

- an exact compatibility allowlist permits live enrollment; a bare module
  parameter can never make an unknown identity `LIVE_ELIGIBLE`;
- the production live path passes deterministic failure-injection tests and a
  warnings-fatal build against the exact running headers;
- the complete Phase 4A clock-disabled regression is repeated against the
  exact live-candidate bytes before enrollment;
- physical wiring, attenuation, SDR identity, frequency, 2 mA drive, and the
  absence of every prohibited component are recorded and independently checked;
- clock enable/disable latency and jitter have predeclared thresholds,
  sufficient repetitions, uncertainty, raw timestamps, and reproducible
  analysis;
- DMA word count/order, exact final-divider readback, bounded STOP behavior,
  common-clock restoration, pin restoration, and neighboring-register
  integrity pass;
- QRSS/TONE, FSKCW, and DFCW each have separate requests, captures, metrics,
  terminal states, cleanup proofs, and decisions;
- WSPR is recorded as `Unavailable` because the authorized burst duration is
  insufficient, unless a new authorization explicitly changes that bound;
- every failed attempt remains preserved; every finding is reinjected and the
  affected matrix rerun;
- the final target is absent/safe and the portable evidence verifies after
  relocation; and
- a separate final adversarial assessment has no unresolved objective finding.

No result may qualify GPIO20, another kernel/DT/firmware identity, another
drive, another frequency, another physical route, intentional radiation, or
product-wide RF performance.

## Pre-burst implementation and safety gate

Before setting `live_output=true`, inspect the exact implementation and prove:

1. live eligibility requires both immutable enrollment and an exact reviewed
   kernel/DT/route/module/UAPI compatibility identity;
2. unknown or mismatched identities reject submission before allocation,
   pinctrl, clock, MMIO, tick, or DMA mutation;
3. GPIO4 is the only bound/requested route and GPIO20 is never selected;
4. the initial clock is disabled, unprepared, parented to the expected source,
   at the expected rate, and exclusively rate-protected by this endpoint;
5. TICKS DMA0 and DMA TICK0 start idle with only reviewed volatile bits;
6. the divider target and tick resources derive from the authoritative runtime
   DT range and match the accepted translated identities;
7. finite buffers and descriptors are armed before active pinctrl selection;
8. generation-tagged completion, STOP, close, process death, unbind, and module
   removal converge through one synchronous cleanup path;
9. readback uses DMA device-to-memory and restoration uses supported
   common-clock operations without stale-snapshot overwrite; and
10. cleanup ambiguity latches rejection and prevents a successor.

Add or correct deterministic tests for every failed assertion. Run the full
offline suite twice and repeat the accepted Phase 4A `wspr5` clock-disabled
matrix with `live_output=false`. Perform a separate pre-burst adversarial
review. Any unresolved finding stops the phase before output.

## Measurement plan and predeclared thresholds

Write a reviewed measurement-plan document before the first burst. It must
define, with units and rationale:

- clock enable and disable event definitions;
- timestamp domains and their synchronization or correlation method;
- sample rate, bandwidth, gain, AGC state, reference source, center frequency,
  expected conducted level, overload check, and raw IQ format;
- warm-up/discard policy and minimum repetition count;
- median, tail percentile, maximum, peak-to-peak jitter, and uncertainty;
- acceptable frequency error, tone spacing, event-duration error, missed or
  duplicated transition count, and spectral artifact thresholds;
- DMA expected word sequence and descriptor boundaries;
- exact divider readback expectation and volatile-mask rules;
- the complete neighboring-register window, stable/volatile masks, snapshot
  timing, and fail condition;
- STOP injection points and maximum residual-work/drain deadline;
- expected initial/final pinctrl, clock rate/parent/counts, tick state, DMA
  state, terminal state/reason, and dmesg classification; and
- pass/fail rules for QRSS/TONE, FSKCW, and DFCW separately.

Thresholds must precede observations. Do not tune them after seeing results.
If the available SDR/reference cannot support the claimed uncertainty, narrow
the claim or stop as `Unavailable`.

## Armed cleanup and command discipline

Use a new work and evidence directory for each attempt. Before every mutation:

- capture full baseline identity and dmesg;
- arm cleanup for client, worker, overlay, module, installed artifact, signing
  files, SDR capture, and evidence writers;
- give every command a TERM deadline, KILL deadline, expected status, and
  timestamp;
- prove GPIO4 and GPIO20 input/safe and GPCLK prepare/enable/protect counts zero;
- prove no overlay, endpoint, test module, active DMA, conflicting consumer,
  stale client, or service change; and
- record raw register windows only through the reviewed kernel/instrumentation
  path—never `/dev/mem` or raw userspace MMIO.

On any unexpected state, stop new work, execute cleanup, preserve the failed
attempt, prove the safe baseline, and only then diagnose.

## Bounded GPIO4 execution order

All bursts use GPIO4, 2 mA, nominal 10.1402 MHz, and are at most ten seconds.
Do not combine steps or advance on a partial result.

### 1. Enrollment without submission

- Build, sign, install, and load the exact candidate with its reviewed live
  enrollment and compatibility identity.
- Apply only the GPIO4 production overlay.
- Query capabilities and require exact route GPIO4 plus `LIVE_ELIGIBLE`.
- Do not submit yet. Recheck both pins, clocks, tick registers, DMA, device,
  SDR availability, and dmesg.

### 2. Sentinel QRSS/TONE burst

- Start and verify raw SDR capture before submission.
- Submit one constant TONE/QRSS event no longer than one second.
- Record request bytes, generation, all state snapshots, enable/disable timing,
  raw IQ, DMA/readback result, restoration, neighboring registers, and dmesg.
- Require successful cleanup and the exact safe baseline before continuing.

### 3. Timing and jitter repetitions

- Run the predeclared number of identical TONE bursts, each within the
  ten-second ceiling and separated by complete cleanup/baseline checks.
- Preserve every capture. Compute metrics only from immutable raw inputs.
- Test enable and disable independently; do not hide outliers or failed starts.

### 4. Cancellation and restoration

- Inject STOP before activation where constructible, early in a descriptor, at
  reviewed descriptor boundaries, and near final completion.
- Require no successor, bounded drain, one terminal reason, exact final-divider
  readback where a write occurred, safe pin, balanced clock references,
  restored rate/parent, stopped tick, synchronized DMA teardown, unchanged
  neighboring registers, and a reusable endpoint only after clean completion.
- Separately exercise owner close/process death under a bounded live burst.
  Do not unbind/remove until synchronous quiescence is proved.

### 5. QRSS/TONE mode row

- Exercise constant tone and at least one reviewed QRSS on/off event pattern.
- Assess timing, carrier frequency, level stability, spectral artifacts,
  sequence integrity, terminal state, and cleanup against predeclared limits.

### 6. FSKCW mode row

- Exercise a bounded two-tone FSKCW sequence.
- Verify tone identity/spacing, transition order and timing, absence of skipped
  or duplicated events, cancellation behavior, and cleanup.

### 7. DFCW mode row

- Exercise a bounded DFCW sequence separately from FSKCW.
- Verify mark/space timing semantics, gap behavior, tone identity/spacing,
  sequence integrity, cancellation behavior, and cleanup.

### 8. WSPR row

- Do not transmit a WSPR frame under the current ten-second authorization.
- Record `Unavailable — authorized burst ceiling is shorter than one complete
  WSPR frame` with no inferred qualification from parser tests, DMA fragments,
  historical evidence, or another route.

## Evidence identity

Record exact hardware, kernel, configuration, headers, compiler, firmware,
boot ID, base FDT/runtime DT, overlay source/DTBO, route/pin/header position,
drive, frequency, module source/commit/archive/build/version/unsigned/signed/
installed/loaded hashes, signer, vermagic, UAPI bytes/hash, compatibility ID,
capabilities, DMA provider/request/channel, clock provider/ID/parent/rate/
counts, translated resources, request bytes, generations, terminal states,
attenuator identities, RSP1B identity/settings, raw IQ, analysis code, clocks/
references, uncertainty, dmesg, commands, timestamps, and reviewer identity.

Generate a relative-path manifest only after every writer closes and all
test-owned target assets are removed. Hash the archive, download it, extract it
under a different path, verify every inner hash, and rerun analysis from raw
captures. Preserve failed attempts as separate immutable archives.

## Adversarial reinjection loop

After pre-burst implementation review and after each execution row, separately
attempt to falsify authorization, wiring containment, compatibility enrollment,
route isolation, clock context/order, DMA sequence/readback, cancellation
bound, restoration, neighboring-register masks, timestamp correlation,
statistics, uncertainty, SDR overload, spectral conclusions, mode separation,
cleanup, evidence portability, and every compatibility claim.

Write every objective finding into the governing prompt/decision or a review;
correct implementation, tests, thresholds, or evidence; invalidate affected
artifacts; repeat the complete affected matrix; and reassess. Stop if a fix
needs expanded authorization, a changed interface, GPIO20, a longer burst, a
different physical chain, a service change, reboot, or intentional radiation.

## Final cleanup, publication, and report

Stop/reap clients and captures; remove only test-owned overlay, module,
installed artifact, key, build, and evidence-working files. Prove GPIO4 and
GPIO20 input/safe; GPCLK counts zero; tick and DMA idle; original clock
rate/parent restored; no overlay/module/device/client/artifact remains; no SDR
capture remains active; services are unchanged; and every dmesg delta is
classified.

Commit and push only if the GPIO4 Phase 4B exit gate passes, the exact tested
source and evidence identities correspond, the worktree/staged set is cleanly
scoped, documentation/licensing are correct, and publication remains
appropriate. Do not tag, release, alter WsprryPi, advance GPIO20, or begin
Phase 5 without separate authorization.

Report pass/fail first, then exact identities and evidence hashes; timing and
jitter metrics with uncertainty; DMA/readback/cancellation/restoration/
neighboring-register results; separate QRSS/TONE, FSKCW, DFCW, and WSPR
decisions; adversarial findings and reruns; hardware/GPIO/SDR/system actions
performed and not performed; final safe state; Git state; and the exact next
gate. Never describe the result as on-air RF qualification.
