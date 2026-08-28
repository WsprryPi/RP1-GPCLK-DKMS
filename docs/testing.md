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
and measures them with SDRplay serial `2404058C60`. Frequencies through 50 MHz
use the fundamental; higher requested frequencies measure the third harmonic.
Source-clock and receiver PPM values are separate explicit inputs; both default
to zero. The CSV includes the divider plan, raw SDR estimate,
receiver-corrected estimate, and rejected points. This diagnostic is never part
of `make check` and does not itself authorize target or RF work.

Render the wspr5 plan twice without touching hardware:

```sh
./build/development-frequency-sweep --render-only --points 16 --repeats 2 \
  --source-rate-ppm -41.203682 --receiver-ppm 1.078468 \
  --output /tmp/rp1-gpclk-plan.csv
```

Run the same vector live only in an authorized GPIO20/SDRplay window:

```sh
./build/development-frequency-sweep --live --points 16 --repeats 3 \
  --source-rate-ppm -41.203682 --receiver-ppm 1.078468 \
  --output /tmp/rp1-gpclk-live.csv
```

The transmitter PPM describes the physical XOSC (`negative` means slow) and
changes divider planning through `corrected_parent = 50 MHz * (1 + ppm/1e6)`.
The receiver PPM corrects the SDR estimate by division by `(1 + ppm/1e6)`.
The wspr5 values are development measurements for that device and receiver,
not defaults for other systems.

## Historical compatibility checks

The 1.0.1 and 1.1.0 contract-freeze checks are intentionally retained. They
protect published UAPI bytes and predecessor compatibility; they do not claim
that those versions are the current module or package. Route-manager tests
likewise retain explicit 1.1.1 fixtures solely to verify bounded migration to
the current owned-block format.

Obsolete Phase 2 through Phase 4 target campaigns, retired Gate-D evidence
machinery, and tests requiring deleted release evidence are not maintained in
this repository. Target waveform and mode qualification belongs in the
WsprryPi Qualification Harness. No ordinary repository test authorizes module
installation, loading, GPIO operation, transmission, SDR capture, or RF work.
