<!-- SPDX-License-Identifier: MIT -->

# Phase 2D adversarial assessment

Date: 2026-08-14
Scope: representative stock Raspberry Pi header compilation and DKMS recipe
Result: pass for the exact offline evidence after four correction cycles

## Method

The assessment separately attempted to falsify the Phase 2D execution prompt,
stock Pi 5 header/package identity, kernel configuration and symbol-version
identity, compiler and AArch64 output, complete Kbuild linkage, module/DKMS/UAPI
version consistency, vermagic agreement, signing claims, warnings and static
checks, archive integrity, compatibility ceiling, and the prohibition on
system, module-lifecycle, hardware, transmission, and RF actions.

It used source review, the complete offline suite on macOS and `wspr5`, two
clean external-module builds with `W=1 KCFLAGS=-Werror`, exact `dkms.conf`
recipe execution, `file`, `readelf`, `modinfo`, SHA-256 records, and negative
module-vermagic and DKMS-version mutations.

## Reinjected findings and resolutions

1. The first 6.12 build found that local variable `current` collided with the
   arm64 kernel macro, `no_llseek` was absent, and removal used the nonexistent
   `RP1_GPCLK_TERMINAL_PROVIDER_REMOVED` name. The variable is now macro-safe,
   the obsolete file-operation member is omitted after `nonseekable_open()`,
   and removal uses canonical `RP1_GPCLK_REASON_PROVIDER_REMOVED`. Both header
   lines then compiled cleanly.
2. The first archive execution called `git diff --check` without Git metadata,
   producing misleading usage output. The suite now reports an explicit
   archive skip while the source worktree performs and passes the check.
3. Initial inspection transcribed `readelf` and `modinfo` output but did not
   machine-validate it. `tests/check_built_module.py` now rejects wrong ELF
   machine, source/module version, license, or vermagic release. Its wrong
   expected-vermagic negative is killed.
4. The initial DKMS static assertion checked the aggregate module name but not
   completeness of its constituent objects. It now compares every `src/*.c`
   stem with every Kbuild `src/*.o` entry and rejects missing or extra objects.

## Final assertions

- The only positive build claims use packaged stock Raspberry Pi
  `6.12.75+rpt-rpi-2712` and `6.18.34+rpt-rpi-2712` headers. The running custom
  host kernel is context only.
- Both exact DKMS recipes compile every source object without warnings and
  produce validated AArch64 modules whose version, license, and vermagic match
  the requested identity.
- Configuration and `Module.symvers` checksums, package/compiler identities,
  module and UAPI versions/checksums, module hashes, page size, preemption,
  module versioning, compression, stock RP1 clock configuration, and unsigned
  status are recorded without implying runtime behavior.
- The DKMS-version and expected-vermagic mutations are rejected.
- No lifecycle command exists in the offline suite. No DKMS registration or
  system/module/hardware operation occurred.
- The result is capped at `Compatible-unqualified`; the Phase 2 target gate is
  explicitly open.

## Limitations

The `dkms` command itself was unavailable, so Phase 2D validated the exact
configuration recipes without exercising DKMS's private staging workflow.
Sparse, Smatch, and Linux-host Clang were unavailable; compiler `W=1` plus
`-Werror`, source contract scans, strict host builds, sanitizers, and
ShellCheck are the recorded static evidence. The modules are unsigned and were
not loaded. These limitations cannot be promoted into installation, signing,
load, target, GPIO, timing, coexistence, cleanup, update, recovery, or RF
claims.

No uncorrected objective finding remains in the Phase 2D evidence examined.
