<!-- SPDX-License-Identifier: MIT -->

# Phase 4 timing and controlled live-output qualification execution prompt

## Mission and exit condition

Act as the kernel-module implementer, target qualification operator, evidence
custodian, and adversarial reviewer for `WsprryPi/RP1-GPCLK-DKMS`. Implement
the frozen ABI v1 live-work path, then qualify timing and controlled output on
one exactly identified Raspberry Pi 5 / RP1 target. Treat GPIO4 and GPIO20 as
independent routes and QRSS/TONE, FSKCW, DFCW, and WSPR as independent mode
evidence rows. The user's three authorization classes may group FSKCW/DFCW,
but their pass/fail results remain distinct.

Phase 4 is complete only when every advertised route and mode has its own
passing timing, divider, sequencing, cancellation, cleanup, recovery, and
conducted-RF evidence row; all evidence is portable and checksummed; a
separate adversarial assessment has no unresolved objective finding; and the
target is proved returned to its recorded baseline. A partial matrix remains
open and must not be generalized.

Do not start GPIO or RF work merely because this prompt exists. Stop at each
authorization gate unless the exact bounded permission is present in the
current task. Earlier clock-disabled, GPIO, or RF authorization does not carry
forward.

## Governing contracts and frozen inputs

Follow, in order:

1. `AGENTS.md`;
2. `docs/contracts/rp1-gpclk-dkms-module-contract.md`;
3. `docs/contracts/phased-plan.md`;
4. `docs/contracts/uapi-v1.md`;
5. `docs/development/decisions/0005-phase2e-gpio4-clock-disabled.md`;
6. `docs/development/decisions/0006-phase3-interface-freeze.md`;
7. `docs/evidence/phase2e-clock-disabled-target.md` and
   `docs/evidence/phase3b-clock-disabled-route-closure.md` as regression
   context only; and
8. canonical `include/uapi/linux/rp1_gpclk.h`, `uapi-identity.json`, and the
   compatibility-manifest schema.

ABI v1 layouts, ioctl numbers, enum values, route values, capability meanings,
overlay names, DT properties, compatible, module/device names, and identity
rules are frozen. Correct implementation defects without silently changing a
frozen interface. If an additive ABI change is truly required, stop for a
reviewed contract decision and restart qualification from the new immutable
identity.

At Phase 4 entry the driver implements only `QUERY`, `ACQUIRE`, and `RELEASE`,
advertises no submission or live-eligible capability, and rejects submission,
STOP, and state ioctls with `EOPNOTSUPP`. This is the safe baseline, not a live
implementation or qualification result.

The module repository owns kernel behavior and module-specific qualification.
`WsprryPi/WSPR-Transmitter` owns request translation, and `WsprryPi/WsprryPi`
owns UTC scheduling, application policy, and product qualification. End-to-end
mode evidence may consume exact tagged artifacts from those repositories, but
must not vendor or silently modify them here. A module result alone cannot
claim application scheduling or product qualification.

## Authorization gates

### Gate A: offline implementation

Offline source changes, compilation, static analysis, deterministic host
tests, documentation, and review are allowed only when the current task
authorizes repository changes. They authorize no target mutation.

### Gate B: target administration with output disabled

Before installing, signing, loading, binding, applying overlays, or running a
clock-disabled target test, record:

- target hostname, model/revision, connection method, and administrative
  account;
- exact source commit/archive digest and allowed module/overlay artifacts;
- permitted build, install, sign, load, bind, unbind, unload, and disposable
  file operations;
- permission for only the named route overlays; and
- exact exclusions, including boot changes, reboot, services, GPIO output,
  transmitter keying, SDR capture, and RF.

### Gate C: bounded live GPIO with RF physically inhibited

Obtain a new explicit authorization that states:

- target and exact source/module/overlay identity;
- one route (`GPIO4` or `GPIO20`) and physical pin/header identity;
- permitted drive strength, frequencies, modes, maximum individual output
  duration, maximum repetitions, and total energized time;
- the instrumented non-radiating fixture, termination, attenuation, and
  physical RF-inhibition method;
- permission to select active pinctrl, prepare/enable/rate-change GPCLK0,
  submit bounded DMA, drive only the named GPIO, measure it, cancel it, and
  restore it;
- stop triggers, TERM/KILL and hardware-disconnect procedure, observer roles,
  and maximum cleanup deadline; and
- exclusions: the other route, other pins, transmitter/amplifier/filter
  connection, antenna, intentional radiation, boot/service changes, reboot,
  and any frequency/mode outside the record.

Authorize GPIO4 and GPIO20 separately. Complete, clean, and assess one route
before requesting authorization for the other.

### Gate D: bounded conducted RF

After Gate C passes for the same exact route and identity, obtain separate RF
authorization stating:

- route; mode; each carrier/tone or band; drive; amplifier/filter state;
  maximum transmission/frame duration, repetitions, and total RF-on time;
- transmitter chain, shielded dummy load, attenuation, measurement tap, SDR or
  analyzer, shared reference, calibration identity/date/uncertainty, and proof
  that no antenna or radiating load is connected;
- legal/control-operator responsibility and permitted time window;
- permission for only the named conducted tests and captures; and
- immediate stop, power isolation, cleanup, and post-test verification.

Authorize QRSS/TONE, FSKCW/DFCW, and WSPR independently for each route. Within
an authorized FSKCW/DFCW class, retain separate FSKCW and DFCW result rows. One
authorization may list several rows only when every row and bound is explicit.
No successful carrier, two-tone test, WSPR decode, or result on one route fills
another matrix cell.

## Safety invariants

- Use only stock-kernel exported APIs, DT-derived resources, the allocated
  DMAengine channel, pinctrl, and common-clock operations. Never use `/dev/mem`,
  raw userspace MMIO, private-symbol discovery, fixed physical addresses, a
  custom kernel, or fallback to another transmitter backend.
- Reject unknown provider, clock, resource, divider offset, DMA translation,
  pin route, kernel, DT, firmware, module, UAPI, signing, or cleanup identity.
- Reject GPCLK0 initially enabled, an unexpected prepare/enable/protect count,
  a cooperative resource conflict, active conflicting pinmux, or an unsafe
  output state. Do not disturb a competing consumer to make the test pass.
- One file owner and one nonzero generation exist at a time. Work is finite,
  kernel-owned, fully validated before start, and has no successor after STOP.
- A stale callback or stale generation cannot change current state or hardware.
- Cancellation drains at most the explicitly defined finite current
  descriptor, verifies final divider readback, stops pacing, disables the
  clock, selects safe pinctrl, and publishes exactly one terminal reason.
- Restore through supported common-clock and pinctrl operations only. Release
  only resources acquired by this module; never replay a stale snapshot over a
  later consumer's state.
- Neighboring registers are observational evidence only unless owned by this
  module. The module may write only the allowlisted GPCLK0 `DIV_FRAC` target
  through its bounded DMA program.
- Cleanup failure latches `Rejected`, inhibits further live work, and requires
  operator remediation. It cannot be cleared by close, reload, or a nominal
  later run without the reviewed recovery contract.
- Every command has a TERM deadline, KILL deadline, expected status, timestamp,
  and armed cleanup. Any unexpected output, timeout, identity change, kernel
  warning, readback mismatch, register delta, or ambiguous cleanup stops the
  run.
- A clean run does not prove exclusion against direct-MMIO or hostile or
  uncoordinated kernel software.

## Phase 4A: offline live-path implementation

Implement the smallest maintainable live path consistent with ABI v1:

1. Validate and copy complete WSPR and event requests into bounded kernel
   storage with checked counts, sizes, pointers, divider adjacency, dither
   periods, symbols, modes, flags, drive values, duration sums, and reserved
   fields.
2. Implement `SUBMIT_WSPR`, `SUBMIT_EVENTS`, `STOP`, and `GET_STATE` with
   nonzero monotonically increasing generations, exact owner/lease checks,
   stable state snapshots, stale rejection, and exactly one terminal reason.
3. Build finite DMA programs without accepting arbitrary addresses, channels,
   registers, or unbounded work. Prove descriptor-count, allocation-size, and
   duration calculations cannot overflow.
4. Implement divider writes and device-to-memory exact divider readback using
   the validated DMA-owned path. Do not use `clk_get_rate()` as exact direct
   divider readback.
5. Define and validate the stock-kernel DMA-tick pacing resources in device
   tree, including resource identity, containment, exclusive ownership,
   mapping, DREQ configuration, enable/disable, and neighboring-register
   boundaries. Historical fixed offsets and custom-kernel provider lease APIs
   are evidence only; they are not production dependencies. Refuse live work
   if exported DMAengine plus validated DT resources cannot provide the exact
   bounded pacing contract.
6. Establish reviewed ordering for common-clock rate protection, preparation,
   rate/parent handling, pinctrl activation, DMA preparation/submission,
   enable, start, completion, stop/drain, readback, disable/unprepare, safe
   pinctrl, and resource release. Use supported common-clock prepare/enable and
   disable/unprepare operations; do not recreate or claim the historical
   provider-private lease. Prove disabled event gaps can be implemented without
   an atomic-context API violation or unsafe enable-reference race.
7. Implement bounded cancellation for every descriptor boundary, process
   death, close, unbind, and injected failure. Reject or synchronously quiesce
   removal while callbacks or open files retain references.
8. Advertise submission, stop/drain, stable-state, and live-eligible
   capabilities only when their implementation and exact compatibility rule
   permit them. Unknown identities remain non-live.
9. Preserve route-neutral code and independent GPIO4/GPIO20 compatibility
   records. Do not embed a preferred route in common logic.

Add deterministic offline tests for every UAPI field and bound; arithmetic and
allocation failures; state transitions; generation wrap/staleness; callback
races; cancellation at every boundary; process death; close/unbind/remove;
partial clock/pinctrl/DMA acquisition and submission failures; readback and
cleanup faults; capability truthfulness; and both route identities. Inspect
all test implementations before running them. Run the complete offline suite
twice, warnings fatal where supported, plus SPDX, UAPI identity, manifests,
overlays, documentation links, whitespace, and representative kernel-header
builds.

Perform an adversarial review before any target work. Reinject each finding
into this prompt or a reviewed decision, correct it, rerun all affected checks,
and repeat until no unresolved objective finding remains.

## Phase 4B: clock-disabled target regression and instrumentation proof

Under Gate B, rebuild and test the exact Phase 4 source on the named target.
Repeat the complete Phase 3B two-route clock-disabled matrix and prove that
adding live code did not weaken route identity, conflicts, lifetime, safe
states, zero prepare/enable counts, failure recovery, diagnostics, or final
absence.

Before Gate C, prove instrumentation without enabling output:

- capture exact monotonic/raw, kernel trace-clock, GPIO instrument, analyzer,
  SDR, frequency-reference, and UTC identities and their synchronization;
- define the event timestamps used for requested start, pin activation, clock
  enable, first observed edge, last edge, disable, safe pin, DMA callback,
  drain completion, readback, and terminal publication;
- measure and subtract or report fixture and probe delay without hiding it;
- predeclare numeric acceptance thresholds and sample counts from product or
  engineering requirements, including latency, jitter, frequency error,
  spacing, transition settling, cancellation bound, and spectral limits;
- prohibit post-hoc threshold selection; and
- run an inert rehearsal proving bounded capture, hashes, timestamps, cleanup,
  evidence packaging, and emergency stop without active pinctrl or clocks.

## Phase 4C: per-route live GPIO qualification with RF inhibited

Run this entire matrix first for one Gate-C-authorized route, return to the
baseline, assess it, then obtain authorization and repeat independently for
the other route:

1. Revalidate exact hardware, kernel, DT, overlay, route, drive, module, UAPI,
   source, tools, instruments, fixture, and authorization identities.
2. Snapshot GPCLK0 and a reviewed window of neighboring registers through an
   observational kernel-owned/debug interface that does not race or mutate
   them. Record ownership and masks for volatile bits.
3. Reject initially enabled/claimed GPCLK0 and cooperative clock, pin, DMA,
   or shared-endpoint conflicts. Where a cooperative competing consumer can be
   installed safely, prove rejection without changing its state, then remove
   only the test-owned consumer.
4. At the lowest authorized drive and a benign authorized frequency, perform
   bounded enable/disable trials. Measure requested-to-enabled,
   enabled-to-first-edge, last-edge-to-disabled, and disabled-to-safe-pin
   latency distributions using predeclared sample counts. Report min, median,
   p95, p99, maximum, standard deviation, outliers, missed deadlines, clock
   source, raw samples, and uncertainty—not only averages.
5. Validate each submitted divider sequence against independent observations
   and exact DMA readback. Prove allowed divider writes, ordering, dither
   counts, stable final divider, and no skipped, duplicated, late, or
   out-of-generation descriptor.
6. Compare neighboring-register snapshots with masks and independent traces.
   Require no unexplained change outside the allowlisted divider target and
   common-clock/pinctrl effects explicitly owned by the module.
7. Cancel before start, at every descriptor boundary class, during steady
   output, at the last descriptor, after callback/terminal publication, on
   owner close, process death, and provider removal where the reviewed
   lifetime procedure permits. Prove no successor, bounded drain, stale
   callback rejection, correct reason, exact final readback, and safe cleanup.
8. Inject each supported clock, pinctrl, DMA prepare/submit/callback, readback,
   allocation, copy, deadline, and cleanup failure. Require the specific
   terminal reason, bounded residual activity, and cleanup latch where
   applicable.
9. Repeat enable/disable, sequencing, cancellation, and recovery enough to
   expose intermittent faults under the predeclared plan. Do not continue
   after a contaminated row.
10. Prove the unselected route remained input, unclaimed, and unaltered for the
    entire run. Finish with both pins safe, counts zero, no active DMA, no
    endpoint/client/overlay/module/install residue, and no unclassified dmesg.

Passing Phase 4C is electrical/timing evidence with RF inhibited. It does not
qualify a transmitter chain, spectrum, emissions, a mode, or RF output.

## Phase 4D: per-route, per-mode conducted-RF qualification

Under Gate D, create separate evidence rows for the Cartesian product:

| Route | QRSS/TONE | FSKCW | DFCW | WSPR |
| --- | --- | --- | --- | --- |
| GPIO4 | independent row | independent row | independent row | independent row |
| GPIO20 | independent row | independent row | independent row | independent row |

For every row, use the authorized shielded chain and dummy load and repeat
identity, pre-state, stop, cleanup, and register-integrity checks. Preserve raw
IQ/analyzer captures and analysis code with hashes.

### QRSS/TONE

- ABI v1 represents a constant `TONE` as an enabled `QRSS` event with one tone;
  record that mapping and do not invent a new mode value.
- Measure each authorized static carrier's frequency error, stability, phase
  noise/jitter proxy, harmonics, spurs, occupied bandwidth, startup/settling,
  bounded duration, disable tail, cancellation, and final safe state.
- Exercise output-disabled gaps independently from an enabled constant tone.
  A usable carrier proves only this row.

### FSKCW/DFCW

- Validate both tones independently and then the planned message/event
  sequence: absolute frequencies, spacing, transition direction, ordering,
  element/gap timing, settling, unintended intermediate energy, cancellation
  during each element class, duration, and terminal RF-off state.
- Keep FSKCW and DFCW results individually visible even if one authorization
  and capture set covers both. Their timing semantics are not interchangeable.

### WSPR

- Validate all four symbol tones, spacing and monotonic order, exact 162-symbol
  sequence, `writes_per_symbol`, dither distribution, frame start alignment,
  symbol timing, total duration, frequency stability, spectral behavior,
  cancellation, and terminal RF-off state.
- Use an independent decoder and preserve complete logs when decoding is an
  acceptance criterion. A decode does not prove calibrated power, absolute
  frequency, spectral compliance, cleanup, or the other modes.
- Attribute even-UTC frame planning and application launch timing to the exact
  WsprryPi scheduler/adapter artifacts. The module can prove bounded execution
  after submission but ABI v1 contains no UTC scheduled-start field. Do not
  misattribute application scheduling evidence to the module.

For all rows, compare results only with thresholds declared before output.
Report measurement uncertainty and any limitation of the shared reference,
SDR/analyzer dynamic range, load/attenuator calibration, or fixture isolation.
Intentional radiation is outside this prompt.

## Evidence identity and integrity

Record, at minimum:

- authorization text and matrix row;
- operator, observers, target hostname, Pi model/revision/serial or privacy-safe
  stable identifier, boot ID, UTC interval, and monotonic interval;
- running kernel release/build/config/package, architecture, compiler, headers,
  firmware/bootloader, base FDT and runtime DT hashes;
- overlay source/DTBO hashes, bound route and pin, pinctrl states, clock
  provider/ID/parent/rate/counts, resource range, divider target, DMA
  provider/request/channel identity, and neighboring-register window/masks;
- physical header pin, drive, frequency/tone plan, mode, durations, repetitions,
  load, attenuation, transmitter/filter/amplifier chain, and RF-inhibition
  state;
- source commit/archive, dirty-state record, module source/build ID/version,
  unsigned/signed/installed/loaded hashes, signer/vermagic, canonical UAPI
  version/hash, compatibility ID/state/reason/capabilities, userspace adapter
  identity, and exact request bytes or canonical representation;
- instruments, probes, SDR/analyzer settings, sample clocks, reference source,
  calibration records, uncertainties, raw captures, analysis tools and hashes;
  and
- commands, expected/actual results, deadlines, timestamps, state snapshots,
  dmesg baselines/deltas, cleanup, raw samples, derived metrics, thresholds,
  pass/fail decisions, and reviewer identity.

Use a new evidence and work directory for every attempt. Never reuse, append,
delete, or rewrite failed evidence. Generate relative-path manifests only
after writers close and disposable target artifacts are removed. Verify the
archive hash locally, extract it to a different path, verify every inner hash,
and rerun analysis from preserved raw inputs.

## Adversarial assessment and reinjection loop

After each implementation, route, and RF-mode gate, independently attempt to
falsify:

- authorization scope and physical RF inhibition;
- identity completeness and artifact reproducibility;
- capability truthfulness and compatibility-state ceiling;
- timing clock synchronization, sample sufficiency, threshold provenance,
  statistics, uncertainty, and raw-to-derived reproducibility;
- DMA ordering, divider readback, volatile-mask justification, and neighboring
  register integrity;
- initial conflict rejection and noninterference with cooperative consumers;
- generation ownership, callback lifetime, cancellation bound, terminal
  reason uniqueness, cleanup latch, and restoration ordering;
- GPIO4/GPIO20 independence and safety of the unselected route;
- QRSS/TONE, FSKCW, DFCW, and WSPR separation;
- conducted-load containment, spectral analysis, and the limits of a decode;
- dmesg completeness, failed-attempt retention, archive portability, and final
  target absence; and
- every `Qualified`, `Experimental`, or other compatibility claim.

Write each objective finding into the execution specification or a reviewed
decision, correct it, invalidate affected evidence, rerun the full affected
matrix from a clean baseline, and repeat the assessment. Do not waive findings
because ordinary tests are green. Stop if correction needs a new interface,
expanded authorization, different hardware, or unsafe action.

## Final cleanup, compatibility decision, and publication gate

Close every client; stop and reap work; remove only test-owned overlays,
modules, installed artifacts, signing material, and files; restore services
only if their stop/start was separately authorized; and prove both pins safe,
clock counts zero, no active DMA, no output/RF, no unexpected process/device,
and no unclassified kernel diagnostic. Record cleanup even after a failed row.

Mark an exact matrix cell `Qualified` only when its complete evidence and
adversarial assessment pass. Use `Experimental`, `Compatible-unqualified`,
`Unavailable`, or `Rejected` exactly as the module contract defines. Unknown
or untested identities never inherit qualification.

Commit and push only after the applicable phase exit is complete, the final
worktree diff and staged set contain only reviewed project files, all tests and
evidence hashes correspond to those exact bytes, licensing/SPDX and docs are
correct, and the current task authorizes publication. Keep module and WsprryPi
application commits/releases separate. Do not tag or advance Phase 5 without
separate authorization.

## Completion report

Lead with the outcome and state:

- which implementation and matrix rows passed, failed, remain unavailable, or
  were not authorized;
- exact identities and evidence bundle hashes;
- timing/jitter, divider/readback, cancellation/restoration, neighboring-
  register, and per-mode RF results with uncertainty and thresholds;
- all adversarial findings, reinjections, reruns, and remaining limitations;
- hardware, GPIO, DMA, transmission, RF, system, and service actions actually
  performed and explicitly not performed;
- licensing, UAPI, documentation, compatibility, and qualification impact;
- final target state and next gated step; and
- branch/worktree state and whether anything was staged, committed, pushed,
  tagged, released, or published.
