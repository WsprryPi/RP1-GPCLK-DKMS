<!-- SPDX-License-Identifier: MIT -->

# Testing

## Maintained inventory

`make check` runs every standalone `tests/check_*.py` program except
`check_built_module.py`. The latter is a parameterized build validator: it
requires a caller-supplied `.ko` and exact kernel release and never loads the
module. `check_test_inventory.py` fails when a new standalone Python check is
neither registered by a standard runner nor explicitly classified as a
parameterized utility.

`make package-check` repeats the package-specific subset. Repetition there is
intentional because package validation is also a separately usable gate.

The C programs compiled by `tests/run-offline-checks.sh` are hardware-free
host tests. `development_tone_client.c` is different: it is a target-only
development client that can open the endpoint and request output. It is never
compiled or executed by an ordinary test target and requires separate,
route-specific hardware authorization.

Its `finite` operation submits one one-second event. The `cancel-start`,
`cancel-middle`, and `cancel-boundary` operations each submit one
maximum-duration logical event, then request cancellation immediately, halfway
through the first one-second DMA chunk, or at its boundary. Each operation
requires the opened endpoint to be a root-owned mode-`0600` character device,
then requires a stable `COMPLETE/STOPPED` result with no cleanup fault. It polls
passive snapshots to prove the module reports GPIO safety and clock/DMA
quiescence and a completed bounded drain before release, and that owner and
lease are absent afterward. A
target campaign must additionally use independent physical observation to
prove endpoint closure, absence of a successor, GPIO safety, clock and DMA
quiescence, and terminal silence; the client result alone is not that proof.

## Cancellation and fault evidence

The ordinary host suite injects every core transaction fault and every
execution-machine setup/cleanup operation. It proves lease and generation
rollback, one terminal publication, one plan release, stage-specific failure
reasons, cleanup-failure precedence, the persistent cleanup latch, and complete
cleanup attempts after an earlier failure. Those mocks do not prove RP1
hardware state.

A target evidence campaign therefore repeats the three maximum-duration
cancellation positions and injects failures at clock setup/enable, active and
safe pinctrl selection, DMA preparation/submission/completion, divider readback,
and cleanup restoration. Fault injection must be compiled into a separately
identified test artifact or supplied by reviewed kernel fault facilities; it is
not a production module parameter or UAPI command. After every case, capture
the lease-scoped terminal reason followed by a passive snapshot proving stable
terminal state, the expected owner/lease disposition, GPIO safety, clock and DMA
quiescence, and cleanup-latch state. The authority observation is the immutable
root-owned mode-`0600` endpoint; there is no kernel authorization credential to
restore or clear.

The maintained target cancellation client measures latency from issuance of
`STOP` to observation of terminal state. It rejects latency above one fixed DMA
chunk plus 500 ms of cleanup, scheduler, and polling allowance; total execution
elapsed time is recorded separately because a boundary-race winner may have
committed the next chunk immediately before `STOP` obtained the commit lock.

The maintained compile-time target injector has stages 1 through 15 for clock
rate setup, clock preparation, active pinctrl, clock enable, DMA preparation,
DMA submission, DMA completion, readback, and each ordered cleanup operation. Build exactly one
stage into an otherwise exact source tree with:

```sh
make KERNEL_BUILD="/lib/modules/$(uname -r)/build" \
  RP1_TARGET_FAULT_STAGE=STAGE
modinfo rp1_gpclk_dkms.ko | grep rp1_target_fault_stage
```

An injected artifact emits a prominent `TEST-ONLY` kernel warning and carries
the `rp1_target_fault_stage` module-information field. The setting is a build
variable only: it creates no module parameter and no UAPI control. Clean or use
a separate build tree between stages and retain every artifact hash. Compile
`development_fault_client.c` separately on the target; it requires the expected
terminal reason and whether a cleanup latch is expected. It verifies retained
terminal state twice, GPIO/clock/DMA quiescence, normal lease release for setup
or execution failures, and deliberate `EUCLEAN` release refusal for cleanup
faults. The administrator must unload each cleanup-latched test artifact and
verify endpoint, lease authority, route, clock, DMA, and GPIO teardown before
continuing.

`development_frequency_sweep.cpp` is also target-only. Build it explicitly
with `make development-frequency-sweep-client` on a target with SoapySDR
development headers. Its default, hardware-free `--render-only` run requests
16 uniformly spaced RF frequencies, inclusive, from 135.7 kHz through 148.0
MHz. It uses finite two-second generic `GPIO20` events at 2 mA only with explicit `--live`,
and measures them with SDRplay serial `2404058C60`. With the selected
`pll_sys` parent, frequencies through the provider's 100 MHz GPCLK0 output
limit use the fundamental; higher requested frequencies measure the third
harmonic.
Source-clock and receiver PPM values are separate explicit inputs; both default
to zero. The CSV includes the divider plan, raw SDR estimate,
receiver-corrected estimate, carrier level, worst spur outside a roughly 200 Hz
carrier exclusion, median in-band noise, and rejected points. This diagnostic
is never part of `make check` and does not itself authorize target or RF work.
Repeat `--frequency-hz` for a repeatable selected-frequency comparison within
the same range; otherwise the uniformly spaced vector is retained. Explicit
`--parent-hz` and `--maximum-direct-hz` inputs allow the same client and RF
vector to compare XOSC and PLL_SYS plans without changing its source. When an
ideal pair straddles an integer-divider boundary, the renderer selects the
nearest legal same-integer pair and clamps its weighting instead of rejecting
the requested frequency.

Render a plan without touching hardware:

```sh
./build/development-frequency-sweep --render-only --points 16 --repeats 2 \
  --source-rate-ppm 0 --receiver-ppm 0 \
  --output /tmp/rp1-gpclk-plan.csv
```

Run the same vector live only in an authorized `GPIO20`/SDRplay window:

```sh
./build/development-frequency-sweep --live --points 16 --repeats 3 \
  --source-rate-ppm 0 --receiver-ppm 0 \
  --output /tmp/rp1-gpclk-live.csv
```

The transmitter PPM describes the selected source (`negative` means slow) and
changes divider planning through `corrected_parent = 200 MHz * (1 + ppm/1e6)`.
The receiver PPM corrects the SDR estimate by division by `(1 + ppm/1e6)`.
Replace the example zero corrections only with values calibrated for the
actual source and receiver. They are not interchangeable.

## Interface checks

UAPI tests protect the current canonical header, ioctl layouts, exact digest,
and absence of legacy layouts or commands. Route-manager tests retain only the
minimal deterministic fixtures needed to verify current ownership and recovery
behavior.

Generated test output belongs in temporary directories. Qualification captures,
run results and deployment inventories belong outside this source checkout.
Release metadata and publication checks are added with a reviewed release
candidate rather than retained from development runs.

Target waveform and mode qualification belongs in the external WsprryPi Harness.
No ordinary repository test authorizes installation, loading, GPIO, transmission,
SDR capture or RF operation.
