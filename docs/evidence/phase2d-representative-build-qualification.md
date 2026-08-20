<!-- SPDX-License-Identifier: MIT -->

# Phase 2D representative build qualification

Date: 2026-08-14
Build host: `wspr5`
Result: `Compatible-unqualified` for the two exact build identities below

## Source and interface identity

- Base Git commit: `f5519a35043223fbca601de9b48a53aa4f179150`
- Git state: Phase 2D changes were intentionally unstaged and uncommitted.
- Exact transferred build-input archive SHA-256:
  `9391f60e18671fc3b852b6ec1f4633d26e29098e2c062005d2f0bc2a465077a5`
- Archive: `/private/tmp/rp1-gpclk-phase2d-source-final.tar.gz` on the
  development Mac; extracted to a disposable `/tmp` directory on `wspr5`.
- Module/DKMS prerelease version: `0.0.0-phase2d`
- Canonical UAPI ABI: `1`
- Canonical UAPI header SHA-256:
  `1d411644352e61402bd4685a5692070d543ab2ee5b016d394294aa98970bd7fb`

This evidence document and the adversarial review were generated after the
build and therefore are not members of the recorded build-input archive. The
archive is the exact input that produced the inspected modules; these reports
do not affect compilation.

## Host context and boundary

The build host was AArch64 `wspr5` with 16 KiB userspace page size and GCC
`14.2.0` (`Debian 14.2.0-19`), GNU ld `2.44`, GNU Make `4.4.1`, Python `3.13.5`,
and ShellCheck installed. The running host kernel was the historical custom
`6.18.44-v8-16k+`; it was not used as representative stock-kernel evidence.

The host had no `dkms`, Sparse, Smatch, or Clang command. The exact build and
clean strings from `dkms.conf` were sourced and executed directly, without
registering source with DKMS or changing `/var/lib/dkms`. `W=1` and
`KCFLAGS=-Werror` made compiler warnings fatal. Repository source-boundary
checks, strict host tests, ASan/UBSan, ShellCheck, full JSON Schema validation,
documentation links, SPDX, manifest, and UAPI identity checks passed on
`wspr5`. Whitespace was explicitly skipped in the archive because Git metadata
was intentionally absent; `git diff --check` passed in the source worktree.

## Exact stock Raspberry Pi header identities

### Raspberry Pi 6.12 line

- Headers: `/usr/src/linux-headers-6.12.75+rpt-rpi-2712`
- Debian package/version:
  `linux-headers-6.12.75+rpt-rpi-2712`, `1:6.12.75-1+rpt1`
- Kbuild kernel release: `6.12.75+rpt-rpi-2712`
- Architecture/compiler: AArch64; `aarch64-linux-gnu-gcc-14` 14.2.0
- Configuration SHA-256:
  `32806f754b437ea037a5173495a2fc83a0628747238874070f0a8b5ba3c79618`
- Symbol-version context (`Module.symvers`) SHA-256:
  `851d09a0f49aab4bfb2ea13be7f6db890eb0b7332b17db783fa021fbe1e90503`
- Selected configuration: `CONFIG_ARM64=y`, `CONFIG_PAGE_SIZE_16KB=y`,
  `CONFIG_PREEMPT_BUILD=y`, `CONFIG_PREEMPT=y`, `CONFIG_MODVERSIONS=y`,
  `CONFIG_COMMON_CLK_RP1=y`, `CONFIG_MODULE_COMPRESS=y`, and
  `CONFIG_MODULE_SIG` unset.
- Module SHA-256:
  `d9ef62788c207b2bb987e283bbd4b8184fb9e2fcceca7e175f6aec646fe72df2`
- Module identity: ELF64 little-endian AArch64, version
  `0.0.0-phase2d`, license `Dual MIT/GPL`.
- Vermagic:
  `6.12.75+rpt-rpi-2712 SMP preempt mod_unload modversions aarch64`
- Build/static/artifact result: pass with no warning or diagnostic.
- Signing result: unsigned build artifact; load/signature acceptance untested.

### Raspberry Pi 6.18 line

- Headers: `/usr/src/linux-headers-6.18.34+rpt-rpi-2712`
- Debian package/version:
  `linux-headers-6.18.34+rpt-rpi-2712`, `1:6.18.34-1+rpt1`
- Kbuild kernel release: `6.18.34+rpt-rpi-2712`
- Architecture/compiler: AArch64; `aarch64-linux-gnu-gcc-14` 14.2.0
- Configuration SHA-256:
  `2a83d4324e9b47d418b4efac18d3af43d15cc956b71c5a8eb074060bf8383801`
- Symbol-version context (`Module.symvers`) SHA-256:
  `681e9fe5710e43c785b39c9e9f410a860cba6a6037e51af23a408cb5ccbe2426`
- Selected configuration: `CONFIG_ARM64=y`, `CONFIG_PAGE_SIZE_16KB=y`,
  `CONFIG_PREEMPT_BUILD=y`, `CONFIG_PREEMPT=y`, `CONFIG_MODVERSIONS=y`,
  `CONFIG_COMMON_CLK_RP1=y`, `CONFIG_MODULE_COMPRESS=y`, and
  `CONFIG_MODULE_SIG` unset.
- Module SHA-256:
  `380e1eabcc8f9121ab364e73d5c8dcd27c7d995b32233d0350d03c94c9e30238`
- Module identity: ELF64 little-endian AArch64, version
  `0.0.0-phase2d`, license `Dual MIT/GPL`.
- Vermagic:
  `6.18.34+rpt-rpi-2712 SMP preempt mod_unload modversions aarch64`
- Build/static/artifact result: pass with no warning or diagnostic.
- Signing result: unsigned build artifact; load/signature acceptance untested.

## Commands and negative checks

For each identity, the build sourced `dkms.conf`, executed its `CLEAN` and
`MAKE[0]` recipes with the identity-specific `kernel_source_dir`, and appended
`W=1 KCFLAGS=-Werror`. `tests/check_built_module.py` then required the expected
AArch64 ELF machine, source module version, dual-license metadata, and exact
kernel-release prefix in vermagic.

Two adversarial negatives passed:

- expected vermagic changed to `0.0.0-adversarial`: rejected with an exact
  expected/found mismatch;
- copied `dkms.conf` version changed to `0.0.0-adversarial`: rejected because
  module and DKMS versions differed.

## Compatibility meaning and exclusions

The maximum and recorded result is `Compatible-unqualified`. It applies only
to compilation of this exact archive with these exact header, configuration,
symbol-version, compiler, and architecture identities. No DKMS registration,
installation, signing, module load, probe, bind, unbind, overlay, system
configuration, clock, pinctrl, DMA execution, GPIO, transmission, SDR, or RF
work occurred. Loadability, target resource identity, runtime coexistence,
cleanup, kernel concurrency, signing policy, update/recovery, and every
hardware behavior remain unqualified. The Phase 2 target exit gate remains
open.
