<!-- SPDX-License-Identifier: MIT -->

# Phase 5.54 half-configured target-recovery authorization prompt

Execute one fail-closed recovery on `wspr5`, bound to source commit
`5587d438f1d75aa938e1f44444dec5e29ad32174`, failure-state capture
`74028d8a3ea0b620d37fc370eb1e53d8f70584bd09c2243fe52cfe941f7ed112`,
failed package SHA-256
`a6bcc854bb807c298b07d81a0405960fbdc7e053df80802e2e95ebc2ca02f095`,
and repaired package SHA-256
`f61286a6e63c2735413a0e86d13c5dc2d91f4581e8a20aab7291234b1991f90b`.

Begin with one read-only recapture. Require the package to remain
`0.0.0~phase5.54-1` and `install ok half-configured`; require the recorded DKMS
registrations, both exact inactive overlays, unloaded module, absent endpoint,
unchanged boot selections, and historical custom header identity to match the
failure capture. Stop on any mismatch.

Only after a match, transfer the exact `-2` package without metadata, verify
its digest, and perform exactly one `dpkg --install` of that package. Do not
configure or retry `-1` separately. Verify `dpkg --audit` is empty; package
version is configured `-2`; the historical `6.18.44-v8-16k+` tree was skipped;
the running stock kernel has the exact DKMS module installed; both boot DTBOs
match the package canonical copies and remain inactive; the module is unloaded;
the endpoint is absent; and boot configuration is unchanged. Remove only the
user-owned staged `-1` and `-2` package files after success.

Stop before lifecycle attempt 1. This prompt does not authorize qualification
tooling, module load/unload, overlay activation/removal, boot changes, reboot,
GPIO/clock/DMA activity, transmission, or RF. A command failure or unexpected
state stops the slice without cleanup beyond the explicitly safe staged-file
rule.
