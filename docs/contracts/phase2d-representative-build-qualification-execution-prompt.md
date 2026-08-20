<!-- SPDX-License-Identifier: MIT -->

# Phase 2D representative build qualification execution prompt

## Outcome and boundary

Act as the kernel build maintainer and adversarial qualification reviewer for
`WsprryPi/RP1-GPCLK-DKMS`. Build the Phase 2C clock-disabled module against at
least two explicitly identified stock Raspberry Pi Pi 5 (`rpt-rpi-2712`)
kernel-header identities, add deterministic compile/static checks and a DKMS
build configuration, and preserve reproducible evidence for every result.

This is source-transfer, compilation, inspection, and documentation work only.
Do not add or install the source in the host DKMS tree; install, sign, load,
bind, unbind, unload, or remove a module; apply an overlay; mutate boot, udev,
systemd, signing, or kernel configuration; select pinctrl; operate clocks or
DMA; change GPIO; transmit; or produce RF. Use a disposable host build copy and
leave the repository as the only source of truth.

## Authorities and compatibility ceiling

Follow `AGENTS.md`, the module engineering contract, phased plan, accepted
Phase 2A through 2C decisions, canonical UAPI, and licensing policy. Preserve
the Phase 2C inertness boundary. The maximum result of any successful compile,
static check, or DKMS build-command validation is `Compatible-unqualified`.
A failed or missing build prerequisite is `Unavailable`; a known unsafe result
is `Rejected`. Never infer loadability, probe success, signing acceptance,
resource identity, cleanup, coexistence, GPIO behavior, timing, transmission,
or RF qualification from a build.

## Required implementation

- Define one explicit prerelease module/source version and expose it through
  both `MODULE_VERSION()` and `dkms.conf`; fail a static check if they diverge.
- Add a conventional DKMS source-build configuration for the single
  `rp1_gpclk_dkms` module. Its build and clean commands must use DKMS's explicit
  kernel source directory. Do not add install/removal automation in this slice.
- Keep the root external-module build fail-closed: an explicit kernel build
  directory is mandatory and no running-host default is inferred.
- Add deterministic static checks for DKMS/module/version identity, Kbuild
  object identity, required build configuration, and the absence of DKMS
  installation or module lifecycle commands from ordinary checks.
- Preserve records of the exact source archive checksum and Git identity,
  module/UAPI versions and UAPI checksum, kernel release/header path and
  package, kernel configuration checksum and selected values, compiler and
  architecture, symbol-version context, page size, module vermagic/signing
  metadata, commands, results, diagnostics, compatibility ceiling, and
  exclusions.

## Representative build execution

Use `wspr5` as a compilation host, but do not treat its running historical
custom kernel as representative stock-kernel evidence. In a disposable
directory, build from the exact transferred archive against both installed
stock Raspberry Pi Pi 5 header sets:

- `/usr/src/linux-headers-6.12.75+rpt-rpi-2712`;
- `/usr/src/linux-headers-6.18.34+rpt-rpi-2712`.

Before building, identify each header package, configuration, compiler,
architecture, page size, preemption model, module-versioning/signing settings,
and kernel release. For each identity run a clean external-module build with
warnings treated as errors, then inspect the generated module with `file`,
`readelf`, and `modinfo` (or explicitly record a missing tool). Exercise the
exact `dkms.conf` build command without invoking `dkms add`, `build`, `install`,
or any system DKMS mutation. Record all skips and failures honestly.

## Adversarial exit loop

Separately attempt to falsify: use of stock Pi 5 headers; header/package and
configuration identity; compiler and architecture capture; source/archive and
UAPI identity; module version and DKMS consistency; complete Kbuild object
linkage; vermagic/kernel-release agreement; signing and symbol-version claims;
warnings/static diagnostics; record integrity; the `Compatible-unqualified`
ceiling; and the prohibition on install/load/bind/GPIO/RF activity. Include
negative tests that alter the DKMS version and expected vermagic so the checks
must fail. Reinject every objective finding into this prompt or its decision
record, correct it, rerun the affected and complete suites and both header
builds, and repeat until no objective finding remains.

## Exit statement

Passing Phase 2D establishes only source-level compile compatibility for the
exact recorded header/configuration/compiler identities and validates the DKMS
build recipe without system registration. It cannot close the Phase 2 target
gate. Signing, installation, load/probe/bind behavior, device-tree identity,
resource acquisition, clock-disabled lifecycle cleanup, kernel concurrency,
GPIO, transmission, and RF remain separately authorized validation classes.

## Reinjectable findings log

The first stock 6.12 header build found a collision between the local owner
counter name and the arm64 kernel `current` macro, use of the removed
`no_llseek` helper despite `nonseekable_open()`, and a stale
`RP1_GPCLK_TERMINAL_PROVIDER_REMOVED` name. Phase 2D must retain the corrected
macro-safe name, omit the obsolete helper, use the canonical
`RP1_GPCLK_REASON_PROVIDER_REMOVED` value, and prove all three through the
representative header build before exit.

The corrected archive run then exposed that the offline whitespace check
called `git diff` even when the transferred source intentionally had no Git
metadata, producing misleading usage output. The check must now distinguish a
Git worktree (`PASS`) from an exact source archive (`SKIP` with reason), while
archive integrity remains covered by its recorded SHA-256.
