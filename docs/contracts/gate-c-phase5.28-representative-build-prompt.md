<!-- SPDX-License-Identifier: MIT -->

# Phase 5.28 exact representative-build prompt

## Objective and sealed candidate

Perform a build-only Gate C check of unpublished `0.0.0-phase5.28` on `wspr5`.
Use only source commit `9c408ec` and the twice-reproduced archive with SHA-256
`cd7e9d60f603101634d6f81e82edda311b724678c9ce9329ff98609911bcc3d6`.
Reject any identity drift or pre-existing Phase 5.28 target residue.

## Preflight and staging

Record hostname, architecture, running stock kernel, canonical `/lib` and
`/lib/modules/KERNEL/build` resolution, header ownership and mode, kernel
configuration and `Module.symvers` hashes, compiler version, service states,
DKMS status, overlays, module/endpoint absence, and unrelated physical
activity. Stop rather than disturb unrelated work.

Stage the exact archive and release sidecars in a new candidate-specific
evidence directory. Verify the outer archive hash and every `SHA256SUMS` entry
before extraction. Preserve all Phase 5.26 and Phase 5.27 staging and evidence.

## Exact build

Extract without changing system paths. Run the kernel build system against the
running kernel's canonical stock headers with the extracted candidate as `M`.
Record the command, result, module SHA-256, version, license, vermagic,
architecture, compiler, and relevant header identities. Require internal
version and vermagic to match the sealed candidate and running kernel.

## Safety and non-goals

This authorization is build-only. Do not use `dkms add`, `dkms install`, or any
package installer. Do not copy into `/usr/src`, `/lib/modules`, or boot paths;
do not load or bind a module, activate an overlay, change services or boot
state, reboot, open an endpoint, access GPIO, enable a clock, submit DMA,
operate the Si5351, SDR, or transmitter, connect an antenna, or produce RF.

## Validation, adversarial review, and exit

After the build, independently verify candidate and module hashes, metadata,
target identity, absence of forbidden system state, and claim ceiling. A green
compile proves representative build compatibility only. Record durable JSON
and prose evidence, rerun applicable offline checks, correct every actionable
finding, commit only attributable changes, push only the current upstream
branch, and report hashes, checks, target effects, Git state, and the next gate.
