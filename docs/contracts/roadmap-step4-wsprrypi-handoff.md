<!-- SPDX-License-Identifier: MIT -->

# Roadmap Step 4 WsprryPi handoff

## Entry condition

Begin from current synchronized WsprryPi `devel`, preserve every checkout and
dirty file, and create a fresh focused `codex/` branch for the integration.
Compare the completed guarded-development policy revision and every Issue 412
branch/worktree by behavior and patch content before editing. Do not revive a
historical branch as the authoritative line merely because it contains unique
work. Incorporate unique required work, obtain exact approval before discarding
anything, and finish with one documented authoritative Issue 412 development
line without stranded unique work.

Step 4 integrates development source and remains hardware-free unless a later
operation is separately authorized. It does not authorize Step 5 target,
receiver, GPIO, transmission, waveform, decode, product, SDR, or RF work.

## Required implementation

1. Replace the pinned 1.1.1 consumer with an intentional 1.1.2 ABI-v2
   development consumer. Bind the exact reviewed source/artifact, UAPI,
   diagnostics, route-manager, overlay, and compatibility identities; do not
   accept a moving branch or version ordering.
2. Support only
   `v1.1.2-pi5-gpio4-6.18.34-development-candidate-r4` and
   `v1.1.2-pi5-gpio20-6.18.34-development-candidate-r4`, independently. Keep
   state `Experimental`; never display or serialize it as Qualified.
3. Preserve the completed guarded-development policy and its one-use exact
   operation/route physical confirmation. A route change, identity change,
   failed query, cleanup, cancellation, or consumption invalidates approval.
4. Expose a stable machine-readable operation record containing all identity,
   route, endpoint, lease, generation, state, terminal, cancellation, cleanup,
   process, timing, and executable fields required by
   `qualification-harness-integration.md`.
5. Keep requested, persisted, configured, active-overlay, module-reported,
   reconciled, and live-eligible routes separate. Require exactly-one-route
   topology and exact agreement before acquisition. Never transfer GPIO4
   evidence or authorization to GPIO20, or vice versa. Permit no automatic fallback
   to another route, backend, `/dev/mem`, or raw MMIO.
6. Provide typed, noninteractive application-plan construction for WSPR, finite
   Tone, QRSS, FSKCW, and DFCW. Every plan explicitly supplies mode parameters,
   exact RF frequencies, band when applicable, route, 2 mA development drive,
   finite bounds, cancellation, and expected terminal state. No qualification
   path may depend on persisted device defaults.
7. Preserve immutable source and executable identity through the structured
   argument vector used by the Harness. Bind the Harness plan digest to the
   exact WsprryPi request and reject substitution, replay, route drift, or
   mismatched operation identity before endpoint acquisition.
8. Use only documented external Harness interfaces. Do not import Harness
   internals, vendor Harness code, or make the Harness a DKMS runtime
   dependency.
9. For WSPR, expose a bounded application path suitable for the Harness carrier
   gate and later three independent frame observations. For Tone use only
   kernel-bounded finite TONE for the first carrier plan. For QRSS, FSKCW, and
   DFCW, expose exactly one bounded message per keyed transaction.
10. On stop, timeout, interruption, process death, submission failure, or
    capture-side cancellation, reject a successor, request generation-specific
    bounded drain, retain the stable terminal reason, release the lease, close
    the endpoint, and report cleanup/quiescence. Cleanup failure overrides
    measurement success.
11. Make pre-launch failure distinguishable from post-launch capture failure.
    Retain proof of whether acquisition/submission reached RUNNING so the
    Harness can classify a later receiver failure as `fixture_blocked` rather
    than transmitter unqualification.
12. Emit semantically valid result inputs and preserve immutable artifact
    destinations. Rejected/partial capture artifacts must not be advertised as
    valid evidence.

## Hardware-free acceptance

- exact 1.1.2/UAPI/route identity success and every near-match rejection;
- independent GPIO4 r3 and GPIO20 r3 plan, policy, and result fixtures;
- requested/persisted/configured/active/module/reconciled/eligible mismatch
  matrix and zero/both-route rejection;
- all five modes through application-plan validation and simulated planning;
- finite Tone bounds, WSPR completion, keyed expected-event construction, and
  explicit frequency/timing inputs;
- exact digest authorization success plus changed executable, argument, route,
  frequency, duration, identity, and stale/replayed digest rejection;
- pre-launch failure, post-launch capture blockage, timeout, cancellation,
  process death, cleanup fault, endpoint-close, and terminal-silence fixtures;
- stable lease/generation/terminal result serialization and schema/semantic
  validation;
- immutable destination, artifact-index rejection, and wrong-route evidence
  tests; and
- full applicable WsprryPi hardware-free CI with transmitter-hardware access
  audit.

## Step 4 exit and Step 5 gate

Record exact WsprryPi, component, executable, DKMS, UAPI, overlay,
compatibility, Harness, schema, and validator identities. Produce semantically
valid hardware-free plans and rehearsals for all five modes and a fully
resolved-but-not-authorized carrier plan template.

The resulting Step 5 campaign must preserve five distinct tests in this order:
finite carrier, WSPR, QRSS, FSKCW, and DFCW. The latter three are the required
QRSS-family modes and must remain separate plan, capture, analysis, lifecycle,
cleanup, result, and evidence records. No aggregate or representative keyed
test may replace any of the three.

Step 5 may begin only after a separate operator review supplies one exact route,
target and receiver identity, physical connection and safe-level basis,
calibration decision, frequency, finite duration, timing bounds, new artifact
destination, operator window, abort/cleanup/silence procedure, and approval of
the final canonical plan digest. GPIO20 requires its own later authorization
and cannot inherit a GPIO4 result.
