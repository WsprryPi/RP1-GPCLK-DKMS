<!-- SPDX-License-Identifier: MIT -->

# Phase 5.45 exact representative-build execution prompt

Execute one bounded, build-only representative-kernel validation of the frozen
Phase 5.45 source commit `4b50db7868b7fe5ca9d830f51cd404c250192188`
on `wspr5`. The release identity is `0.0.0-phase5.45`. Generate the release
unit twice from a clean export of that exact commit, validate both units, and
require byte-for-byte equality before target staging. Transfer only one
validated unit and a clean Git archive of the exact commit into a new,
previously absent Phase 5.45 evidence directory.

Before any target mutation, record and validate the hostname, architecture,
running stock kernel, resolved header tree and its ownership and mode, kernel
configuration and `Module.symvers` hashes, compiler identity, inactive relevant
services, absent module and device endpoints, absent overlays, absent DKMS
registration, and absent destination directory. Stop on any unexpected state.
The operator declarations remain: the separate I2C Si5351 path is disconnected
and unused, the SDR is unused, no antenna is connected, and recovery is
available. This build-only slice must not inspect or operate those devices.

Build the module against the exact running-kernel header tree, with the source
extracted from the clean Git archive rather than from a moving or dirty
worktree. Compile the two permanent Gate D helper programs from that same
source and canonical UAPI header. Capture the complete build transcript,
command status, module hash, module metadata, helper hashes, release-input
inventory, source and tool hashes, and all target identities needed to reproduce
or reject the result. Validate that every transferred release byte matches the
locally validated deterministic unit.

Perform an independent, adversarial review of the resulting evidence. Reject
the slice for any missing file, unchecked hash, source drift, kernel/header
mismatch, ambiguous command status, noncanonical helper build, unsafe target
state, or unsupported claim. Correct all actionable evidence defects and repeat
the affected validation until clean. Update the Phase 5.45 integration gate
only with facts actually established by this execution.

Do not install or register DKMS, install the module, load, bind, unbind, or
unload it, apply or remove an overlay, change services or boot configuration,
reboot, access GPIO or I2C, operate the Si5351 or SDR, submit DMA, enable a
clock, key a transmitter, connect an antenna, or produce RF. Do not use
`/dev/mem`, a custom kernel, forced removal, a general upgrade, or any
unreviewed persistent mutation. A successful result is build compatibility
only and cannot establish lifecycle, cleanup, coexistence, timing, hardware,
transmission, or RF qualification.

Exit only after the prompt, evidence, manifest, independent review, and gate
state are internally consistent; repository checks pass; attributable changes
are committed and pushed on the current branch; and the final report states the
exact build result, evidence identities, prohibited work not performed, Git
state, and the next gated step.
