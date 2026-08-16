<!-- SPDX-License-Identifier: MIT -->

# Gate C representative build: wspr5 / 0.0.0-phase5.18

The exact frozen Phase 5.18 archive built successfully against stock
`6.18.34+rpt-rpi-2712` headers. The module SHA-256 is
`b433f7c2a3aea71232516eadd6ed2835f70da575b72707179c2ad694dad2a3d7`.
The busy injector and UAPI probe were compiled but not executed; their hashes
are recorded in the representative-build manifest.

The first evidence-sealing attempt used target-absolute checksum paths and
reconstructed a timestamp incorrectly after discovering that `modinfo` was
available only through `/usr/sbin/modinfo`. That evidence directory is
retained as failed/superseded. Fresh attempt 2 used directly captured UTC
timestamps and relative checksum entries; its retrieved copy passed every
checksum.

Adversarial plan construction then found that the installed target-plan and
execution-instance validators derive their identity root from their installed
path under `/usr/libexec`. They consequently resolve repository-relative plan,
attempt, and tooling references below `/usr`, rather than an explicitly bound
test-owned qualification root. Phase 5.18 is therefore blocked before target
plan and execution-instance sealing. A successor must add an explicit,
validated qualification-root binding and propagate it through permanent
executor dispatch and subordinate validators.

No package or module was installed, DKMS was not registered, helpers were not
run, and no module, overlay, service, boot, reboot, GPIO, clock, DMA,
transmission, SDR, antenna, or RF operation occurred. Both disposable build
directories were removed. Target evidence and inputs remain read-only.
