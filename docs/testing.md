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
