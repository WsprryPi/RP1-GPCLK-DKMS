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
host tests. `development_tone_v2_client.c` is different: it is a target-only
development client that can open the endpoint and request output. It is never
compiled or executed by an ordinary test target and requires separate,
route-specific hardware authorization.

`development_frequency_sweep.cpp` is also target-only. Build it explicitly
with `make development-frequency-sweep-client` on a target with SoapySDR
development headers. Its default, hardware-free `--render-only` run requests
16 uniformly spaced RF frequencies, inclusive, from 135.7 kHz through 148.0
MHz. It uses finite two-second GPIO20 tones at 2 mA only with explicit `--live`,
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

Run the same vector live only in an authorized GPIO20/SDRplay window:

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

## Historical compatibility checks

The 1.0.1 and 1.1.0 contract-freeze checks are intentionally retained. They
protect published UAPI bytes and predecessor compatibility; they do not claim
that those versions are the current module or package. Route-manager tests
likewise retain explicit 1.1.1 fixtures solely to verify bounded migration to
the current owned-block format.

Generated test output belongs in temporary directories. Qualification captures,
run results and deployment inventories belong outside this source checkout.
The retained version-specific archive layouts, four archive contract inputs in
`docs/releases/`, and their helpers are consumed by package/integrity regressions.
Their generation CLIs are blocked; they do not describe current release eligibility.
The ABI snapshots protect command layouts and the migration fixtures protect
ownership and rollback. They are functional test inputs, not retained runs.

Target waveform and mode qualification belongs in the external WsprryPi Harness.
No ordinary repository test authorizes installation, loading, GPIO, transmission,
SDR capture or RF operation.
