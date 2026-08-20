<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.24 authorized pre-root execution

Status: stopped fail-closed before DKMS or package mutation

The operator granted fresh authorization for the exact sealed Phase 5.24
ten-row output-disabled Gate D execution on `wspr5`. The authorization-only
instance SHA-256 was
`e6da3592d09c188b3788a545692d24d140da90ba723cd9a13ea7c1a3cd9ea08a`;
the dependent pre-root launch-envelope SHA-256 was
`becd2734921767b820194d1dbb13ef3d5ebd5c0fe88e97a5b7e45b2320d3046f`.
Both complete offline suites passed before target contact, and the staged
pre-root validator returned `valid: true`, `readOnly: true`, and
`outputDisabled: true`.

The read-only target preflight found the expected Raspberry Pi 5 baseline:
stock kernel `6.18.34+rpt-rpi-2712`, matching headers for both planned stock
kernels, DKMS 3.2.2, no test DKMS versions, no module, endpoint, driver, or
overlay, and the expected named-service states. The predecessor archive and
successor archive hashes matched the target plan. The successor archive,
DTBOs, qualification identity, and 56 control files were staged read-only at
`/home/pi/gate-d-inputs/phase5.24-2a6ddeb8e0f7`.

The authenticated pre-root transition failed at checkpoint `install` before
the administrator created its transaction state. The sealed administrator was
given the declared release directory, but that directory did not contain
`release-metadata.json`:

```text
FileNotFoundError: /home/pi/gate-d-inputs/phase5.24-2a6ddeb8e0f7/release-metadata.json
```

The control-set envelope binds the candidate archive, extracted bootstrap
files, DTBOs, qualification identity, and transition files, but omits the
release sidecars required by the administrator at the declared release
directory.

The exact `--resume` recovery path then failed before cleanup because it
unconditionally dispatched administrator recovery. The administrator correctly
reported `no real transaction state to recover`; the pre-root coordinator did
not distinguish failure before administrator-state creation.

The final read-only audit found no DKMS state, installed permanent tools,
module, endpoint, driver, overlay, service change, boot change, or kernel
change. Boot configuration hashes remained
`b6218fd92bd231151f177029b0dfd84a2af1e92f94dac768bd9501af087d43e2`
and `431c52efdb5bd829be2d5accc7073a51e7a7be5858f9482a9b3f0453dde44a88`.
No reboot, GPIO, clock, DMA, Si5351, transmitter, SDR, antenna, or RF activity
occurred.

The fail-closed residue is limited to the read-only input tree, the root-owned
marker at
`/home/pi/gate-d-qualification/phase5.24-2a6ddeb8e0f7/.gate-d-root.json`, and
`/var/lib/rp1-gpclk-dkms/gate-d/pre-root-phase5.24.json` with status
`recovery-required`. No ad-hoc cleanup was attempted.
