<!-- SPDX-License-Identifier: MIT -->

# Phase 5.41 freeze and representative-build review

Status: accepted for Phase 5.41 control-set construction; lifecycle execution
remains disabled and unauthorized.

The candidate is frozen at `640877c1f29297e2f6ea855742605550781256e9`.
Two isolated release units generated with its commit timestamp validated as
non-publishable and matched byte for byte. The exact archive SHA-256 is
`b49cd75baefdb245d6d00e60cd171ba6fa4da4c00e63b07e925cdd52f0b0934f`.

The checksummed archive compiled directly and unprivileged on `wspr5` against
the canonical stock `6.18.34+rpt-rpi-2712` headers. The first evidence command
compiled the module and helpers but stopped when bare `modinfo` was outside the
SSH PATH. The retained continuation used verified `/usr/sbin/modinfo`, repeated
the compilation, and passed. This PATH-only stop did not invoke a module or
helper and did not change runtime state.

The current exact kernel configuration, `Module.symvers`, compiler, signing
policy, completed terminal recovery, module, UAPI, tools, and transcript are
bound in the manifest. Initial and final inactive baselines agree. No DKMS,
installation, module, overlay, GPIO, clock, DMA, separate I2C Si5351, SDR,
transmitter, antenna, service, boot, reboot, transmission, or RF action
occurred. This establishes build compatibility only.

No actionable finding remains in this build-only scope.
