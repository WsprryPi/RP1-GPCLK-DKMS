<!-- SPDX-License-Identifier: MIT -->

# Phase 5.30 authorized-execution adversarial assessment

Status: blocked safely during bootstrap cleanup; inactive baseline restored

The authorization, execution instance, envelope, target, release checksums,
and output-disabled dry validation all matched the reviewed Phase 5.30 control
set. The candidate correction worked: both built and installed compressed
module representations were resolved and verified. Installation remained
inactive, and no runtime lifecycle attempt began.

Adversarial review identifies one actionable blocker. `complete-removal`
constructs unconditional DKMS uninstall and remove commands for both candidate
and predecessor. After removing the candidate, it interprets DKMS exit status
3 for an already-absent historical predecessor as a cleanup failure. That is
inconsistent with its required package-absent terminal state and prevents a
fresh target from entering the qualification root when the predecessor is not
installed.

The successor correction must be narrow and fail closed. It may accept an
exact version/kernel as already absent only after bounded DKMS-state inspection
proves that exact tuple absent; it must not suppress arbitrary DKMS failures,
accept ambiguity, use forced removal, or weaken owned-path identity checks.
Tests must cover absent predecessor, present predecessor, command failure with
state still present, wrong kernel/version, ambiguity, and repeated removal.

Failure evidence was preserved before cleanup. Recovery verified the completed
administrator ledger byte-for-byte, removed only its hash-bound files,
symlinks, and empty owned directories, then independently verified the final
inactive baseline and service states. The pre-root resume was not invoked
because it would retry the known-defective cleanup in the same operation.

No module load or binding, overlay activation, GPIO, pinctrl, clock, DMA,
Si5351, transmitter, SDR test, antenna, transmission, reboot, or RF action
occurred. Phase 5.30 is blocked and is not execution-ready.
