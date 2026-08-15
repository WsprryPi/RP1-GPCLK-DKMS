<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.15 successor and input-sealing adversarial assessment

## Outcome

Phase 5.15 closes the Phase 5.14 missing-header defect. Its source archive was
built twice byte-for-byte, includes `gate_d_busy_injector.h`, passed a clean
representative module build, and compiled both permanent helpers strictly from
the sealed target archive. It nevertheless remains blocked before installation
because the frozen tooling identity contract cannot represent distinct source
and installed-binary hashes.

No helper was run or installed. No DKMS registration, package installation,
signing, module load, binding, overlay, service change, boot change, reboot,
GPIO, clock, DMA, Si5351, transmitter, SDR, antenna, or RF activity occurred.

## Passed assertions

- Source commit: `123a94c46a2fb068a5e83c42b440f6b8a07545f6`.
- Archive SHA-256:
  `6a767723a9cbbf32b68d95c67221b0a56430a037508254aa8c3a65a9cd1bbb24`.
- Two offline release units were byte-identical and independently validated.
- The archive contains the busy-injector C source and header and the UAPI probe
  source; concrete attempt documents and evidence are excluded.
- The representative module build passed without diagnostics. Module SHA-256:
  `e692b0973fd7a39894c17f3d743d6fea387305b6828fe57485fcd8331105e6af`.
- Staged input manifest SHA-256:
  `62517b80d6ff4d1de36c1863ed10b5cdb0546c2f2f3c8d5eedcb0b966785b311`.
- Busy-injector ELF SHA-256:
  `c01d97301fcbad4266e6fd41c040f561da0c106affc28cf353455e4a071331dd`.
- UAPI-probe ELF SHA-256:
  `1ee335da403784a775efc049f49eb598e3541c625418b65015b322e29b0a1742`.
- Helper evidence manifest SHA-256:
  `43509df765c0f5f671ea36e0945a6cc3c1f0922247d1d20a58c7dcd6ceaf3564`.
- The disposable module and helper build directories were removed; the target
  evidence and input directories are checksum-sealed and read-only.

## Blocking finding

Each target-plan tooling item has one `sha256`. The plan validator compares it
with `sourcePath`, while target preflight compares it with `installedPath`.
That is valid only for copied files. The compiled helpers necessarily have
different source and ELF hashes, so no honest Phase 5.15 target plan can pass
both validators.

The next successor must introduce separate `sourceSha256` and
`installedSha256` fields plus an explicit copied-versus-built installation
kind. Offline tests must reject swapped, missing, source-only, and binary-only
identities, and target preflight must compare the correct field. Phase 5.15
must not be patched or authorized in place.

## Claim ceiling

Phase 5.15 is route-neutral `Compatible-unqualified`, `liveEligible: false`,
untagged, unpublished, and blocked before Gate D installation or execution.
