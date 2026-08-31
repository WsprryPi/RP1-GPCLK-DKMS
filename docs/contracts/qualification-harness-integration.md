<!-- SPDX-License-Identifier: MIT -->

# Qualification Harness integration contract

## Scope

This contract defines the evidence boundary between an external WsprryPi
Qualification Harness, WsprryPi, and the RP1-GPCLK-DKMS 0.9.0 development
module. It prepares later product integration and qualification; it does not
authorize installation, target access, module or overlay changes, endpoint
operation, GPIO output, receiver access, transmission, or RF activity.

The Harness is an external installable package. Consumers use only its console
script, `python -m` entry point, published schemas, maintained semantic
validators, supported replay/fixture interfaces, and machine-readable result
bundles. No WsprryPi or DKMS code may import undocumented Harness internals.

The current module state is `Experimental`. GPIO4 and GPIO20 are separate
independently attributable targets requiring exact-build qualification; identity,
authorization, results, and retained evidence never transfer between them.

## Identity record

Every resolved plan and result binds these values without relying on version
ordering or implicit defaults.

### Module source and artifact

- repository URL and absolute checkout path used for development evidence;
- exact 40-hex source revision and whether tracked or untracked bytes differ;
- module, DKMS, and intended Debian versions;
- canonical UAPI ABI range and header SHA-256;
- module ID, build ID, and route-specific compatibility ID from ABI-v2 QUERY;
- compatibility metadata path, ID, SHA-256, selected entry, state, reason, and
  `liveEligible` value;
- source and installed module hashes, transform, vermagic, signer, signing
  policy, and actual installed module-file hash when an artifact exists; and
- route overlay source, compiled DTBO, and installed DTBO hashes.

Unreleased 0.9.0 source labels are development inputs, not a final package,
tag, inventory, compatibility manifest, or consumer identity. An absent future
package identity remains an explicit blocker rather than a fabricated value.

### Target and route

- authorized transmitter host alias; model, revision, architecture, kernel,
  headers/configuration, firmware, base device-tree hash, and boot ID;
- clock and DMA provider identity and ancestry, GPCLK0 clock ID, DMA request and
  translation, pinctrl identity, resource layout, and signing policy;
- requested, persisted, configured, active-overlay, module-reported,
  reconciled, and live-eligible routes as separate values;
- exactly one enabled `rp1-gpclk-dkms-gpio4` or
  `rp1-gpclk-dkms-gpio20` endpoint, with the matching `wsprrypi,route`
  property;
- exact GPIO4 r3 or GPIO20 r3 compatibility ID and `Experimental` state; and
- package route-manager transaction ID, status, boot IDs, configuration
  hashes, attribution, and reconciliation result.

The route manager supplies configured and active route state. WsprryPi supplies
requested and persisted state. ABI-v2 QUERY supplies the module-reported route
and compatibility identity. The DKMS diagnostics report independently records
the live endpoint topology and agreement; none of these observations may be
substituted for another.

### Endpoint and operation

- canonical endpoint `/dev/rp1-gpclk`, file identity and availability;
- ABI-v2 capability mask including finite TONE, duration bounds, compatibility
  state/reason, and cleanup-fault latch;
- WsprryPi parent revision, executable path, SHA-256, build metadata, component
  tree identity, backend, mode, band, exact output frequencies, route, drive,
  request and plan identities, and authorized plan digest;
- endpoint ownership check before launch; acquired nonzero lease and strictly
  increasing generation; RUNNING/DRAINING/terminal state and reason; current
  event; elapsed/remaining time; cancellation outcome; cleanup result; and
- process exit, endpoint closure, lease release, GPIO-safe state, clock/DMA
  quiescence, cleanup latch, and terminal-silence observation.

DKMS diagnostics are passive and do not acquire a lease. WsprryPi must retain
the operation-scoped lease, generation, state, terminal reason, and cleanup
evidence returned through its provider adapter.

### Receiver and physical path

- receiver host/local identity, SDR serial/device and driver, sample format,
  rate, bandwidth, center frequency, gain, AGC and bias-tee state;
- calibration policy (`required`, `optional`, or `disabled`), complete profile
  identity, validity domain, application request/result identities, and
  qualification-usability decision;
- physical connection, attenuation and tolerances, load/antenna state, filter,
  safe-input basis, and current operator confirmation; and
- RF-off pre-roll, RF-on duration, post-roll, exact sample count, launch and
  capture timeouts, capture start evidence, and terminal-silence interval.

Receiver calibration preserves indicated measurements and may add
estimated-true frequency and uncertainty. It does not change requested RF,
transmitter arguments or PPM, transmitter identity, output power, harmonic
claims, or product eligibility.

## Mode readiness

The common readiness labels are `externally consumable`,
`hardware-free exercised`, `live-plan ready`, `not ready`, and
`not applicable`. No Step 3 result is labelled qualified.

For each of WSPR, Tone, QRSS, FSKCW, and DFCW, a readiness record covers:

1. application-plan construction;
2. explicit mode parameters with no device defaults;
3. source and executable identity;
4. backend, output, band, route, and frequency binding;
5. receiver and physical-path inputs;
6. receiver-calibration policy;
7. exact plan digest and authorization;
8. bounded transmitter and capture timing;
9. cleanup and backend quiescence;
10. schema and maintained semantic validation;
11. immutable artifact/index/manifest handling; and
12. a passing hardware-free rehearsal.

Harness support alone does not make a WsprryPi mode `live-plan ready`. That
label additionally requires an exact integrated WsprryPi execution path for DKMS 0.9.0,
final artifact identities, operator window, receiver configuration, physical
path, and cleanup contract.

### Roadmap Step 3 assessment

The inspected external Harness baseline is the clean synchronized `main`
checkout at revision `5b6c0c89d4e25ee62a8047f633eb5863fcfb64d1`, package
version `0.1.0.dev0`. Step 3 built and installed its wheel into the disposable
environment `/private/tmp/rp1-step3-harness.EgwFVp/package-venv`; the console
script is `bin/wsprrypi-qualification` below that environment and the selected
interpreter is its `bin/python` (CPython 3.14.7). This temporary path records
the Step 3 rehearsal and is not a durable product path.
The reproducibly repeated wheel SHA-256 is
`df233894b69f1264be5ea0ab4451aee66a3b9e391c412b8aad7e542cab15018f`;
the acceptance sdist SHA-256 is
`f9963cc7a53a28922edf3c42f6c0baea721b77947739c4358bb95794b5c12f6e`.

The schema source is the Harness `schemas/` directory and its byte-matched
installed package copies. Maintained semantic validation is implemented by
`offline.validate_document`, `turnkey_campaign.validate_resolved_campaign_plan`,
`real_session.validate_real_session_plan`, and
`keyed_session_contracts.validate_resolved_keyed_plan`; JSON Schema alone is
not accepted. The turnkey request, resolved-plan, and result schema SHA-256
values at that revision are respectively:

- `913952897b7a6eabe9cf21ca7ea67dcf83cfd1f4d7ccd8b5f86fcf05b0fa32d5`;
- `007f78d2503d53a1481166439bfbc1341b67ed544d39dc3f4055d1bb017d4c4c`;
  and
- `fc9dee9846fab5217ebcbab0cd034c248214c30a9241886137b6243bc660489a`.

All five modes are `externally consumable` and `hardware-free exercised` at
that exact Harness revision. Each passed all twelve readiness criteria for the
Harness side: typed application-plan input, explicit fixture parameters,
source/executable binding fields, backend/output/band/route/frequency fields,
receiver/RF-path contracts, explicit calibration binding, digest confirmation,
bounded timing, cleanup/quiescence contracts, schema plus semantic validation,
immutable manifest bundles, and a deterministic hardware-free rehearsal.

None is `live-plan ready` for the RP1-GPCLK-DKMS 1.1.2 WsprryPi product path in
Step 3. The WsprryPi Step 2 baseline is clean revision
`4fb8f94542e687c3c565e599fe7e7ceba35dbc90`, with component tree object
`7086ad0243dee9fa1bad77b60886da9bb9feca0c`. It still pins the predecessor
1.1.1 consumer, and no exact Step 4 executable, 1.1.2 package/manifest, complete
operation record, final receiver configuration, safe-level basis, operator
window, or authorized plan digest exists.

| Mode | Harness readiness | RP1/WsprryPi live readiness | Step 3 rehearsal route |
| --- | --- | --- | --- |
| WSPR | hardware-free exercised | not ready | `real_session` |
| Tone | hardware-free exercised | not ready | `real_session` |
| QRSS | hardware-free exercised | not ready | `live_keyed` |
| FSKCW | hardware-free exercised | not ready | `live_keyed` |
| DFCW | hardware-free exercised | not ready | `live_keyed` |

The five immutable rehearsal bundles are below
`/private/tmp/rp1-step3-harness.EgwFVp/five-mode/runs`. Each result is
`inconclusive`, has `qualification_claim: false`, reports zero external calls
during planning/validation, and passed the maintained semantic validator.

### Current physical-path fact

The operator reported that wspr5 GPIO4 is connected through two cascaded
nominal −10 dB attenuators directly to the SDRplay connected to wspr5. This is
a topology fact only. The exact attenuator identities/tolerances, connector and
cable state, SDRplay model/serial/driver, gain, center frequency, sample rate,
bandwidth, calibration binding, load/antenna state, expected source level,
maximum receiver input, overload margin, and safe-input calculation remain
`REQUIRED-BEFORE-LIVE`. The connection is not authorization to contact wspr5,
open the SDR, operate GPIO4, transmit, or perform RF work. GPIO20 remains a
separate physical route and has no transferred connection or evidence.

## Control and capture sequence

1. Create a new output and work directory. Reject an existing run destination.
2. Resolve the typed request through the supported Harness CLI. Validate every
   request and resolved document using both JSON Schema and its maintained
   semantic validator.
3. Bind exact Harness, DKMS, WsprryPi, target, route, receiver, calibration,
   helper, service, and RF-path identities. Unknown required values block live
   authorization.
4. Compute the canonical plan digest. Record a short-lived operator approval
   for exactly that digest, route, frequency, duration, connection, receiver,
   abort procedure, and window. Never embed approval in a reusable profile.
5. Install cleanup before receiver or transmitter access. Verify WsprryPi and
   provider idleness, exactly-one route topology, reconciliation, endpoint
   closure, no cleanup fault, and pre-test RF silence.
6. Start exact-count capture and complete the RF-off preamble before launching
   WsprryPi through the plan-bound structured argument vector and authenticated
   helper. A pre-launch capture failure prevents output.
7. Prove launch from authenticated process evidence plus a nonzero lease,
   matching generation, and RUNNING state. A process start alone is
   insufficient.
8. Enforce the kernel/request duration and Harness deadline. Cancellation
   names the exact generation, permits only bounded drain, and admits no
   successor.
9. On success, failure, timeout, or interruption, stop owned processes, observe
   a stable terminal state, release the lease, close the endpoint, verify GPIO,
   clock and DMA quiescence, restore only owned service state, and capture the
   post-run silence interval.
10. Classify capture failure after proven launch as receiver/fixture blockage,
    not transmitter unqualification. Remove incomplete or rejected IQ from the
    valid artifact index while retaining bounded authenticated diagnostics.
11. Semantically validate every result, artifact index, and manifest; seal the
    immutable bundle; and publish/index only accepted evidence.

Automated checks cover typed validation, identity equality, exact counts and
hashes, deadlines, process/endpoint/lease state, terminal reason, cleanup
precedence, artifact membership, and immutable destination use. Manual review
covers physical topology, safe-level basis, current operator authorization,
calibration applicability, spectral interpretation, and claim scope.

## First live-plan template

The Step 5 campaign contains five separate test definitions:

1. finite carrier (`TONE`), never continuous TONE;
2. WSPR;
3. QRSS;
4. FSKCW; and
5. DFCW.

QRSS, FSKCW, and DFCW are the three required QRSS-family modes. Each has its
own explicit mode parameters, plan identity, lifecycle result, capture and
analysis evidence, cleanup result, and semantic validation. A passing carrier
does not replace any mode test, and one keyed-mode result does not satisfy another.

The first Step 5 entry plan is the finite carrier test. It uses ABI-v2 finite
TONE and a kernel-enforced duration. The carrier gate must pass before WSPR or
the three QRSS-family tests proceed. Step 3 leaves these run-specific values
unresolved until Step 4 and the later operator gate:

- WsprryPi revision/executable: `REQUIRED-BEFORE-LIVE`;
- DKMS revision/module/artifact/manifest: `REQUIRED-BEFORE-LIVE`;
- route: one of GPIO4 r3 or GPIO20 r3, independently authorized;
- transmitter host alias and current target identities: `REQUIRED-BEFORE-LIVE`;
- receiver, calibration binding, connection, attenuation, load/antenna state,
  center/analysis frequency, sample rate, bandwidth, and gain:
  `REQUIRED-BEFORE-LIVE`;
- duration, pre-roll, post-roll, capture/launch/cancel/cleanup/silence bounds:
  `REQUIRED-BEFORE-LIVE`; and
- new artifact destination, operator window, abort method, and exact approval
  digest: `REQUIRED-BEFORE-LIVE`.

The template is not authorization and is not executable while any placeholder
remains.

## Evidence boundaries

Hardware-free plan validation, simulation, synthetic IQ, replay, mock
lifecycle, and sealed coordinator rehearsal establish software-contract
evidence only. Read-only actual-host preflight remains actual-host evidence.
Module build, load, binding, output, receiver capture, waveform, decode,
WsprryPi product-path, packaging, SDR, and RF qualification are separate
classes and never inherit from one another.

Existing artifacts are accepted only through supported authenticated replay or
intake. Missing, altered, partial, unauthenticated, unrelated, or wrong-route
sources are rejected and never indexed. Retained evidence is not a new run.
