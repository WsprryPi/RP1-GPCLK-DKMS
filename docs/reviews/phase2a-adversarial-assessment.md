<!-- SPDX-License-Identifier: MIT -->

# Phase 2A adversarial assessment

Date: 2026-08-14
Scope: public contracts and inert source skeleton only
Result: pass for the offline evidence examined after three correction cycles

## Assessment method

The assessment attempted to falsify the Phase 2A execution prompt, module
contract section 16, frozen ABI decision, UAPI byte/layout tests,
compatibility-schema safety rules, source inertness, route neutrality,
licensing/provenance, and documentation claims. Historical source was consulted
only to test semantic sufficiency; it was not copied.

## Reinjected findings and resolution

1. The initial header used ordinary 64-bit fields, had no separate stable
   compatibility-reason enum, the example manifest contained placeholder
   identities, and `Qualified` required only RF evidence. The header now uses
   explicitly aligned 64-bit fields, compatibility reasons are frozen, the
   example is deny-by-default with no entries, and all required evidence
   classes are schema conditions.
2. The initial tone layout could not express lower/upper fractional dithering,
   and a fixed tick divider was modeled incorrectly as an event field. Tones
   now carry bounded lower/upper Q16 values and counts; both submissions carry
   the fixed fractional/tick contract; events contain only duration, tone, and
   the bounded output flag.
3. Drive bitmap constants were named like literal milliamp values and query
   did not report the allowlist. Literal values and support bits are now
   distinct, the query reports the mask, and the stale event-write limit is
   named as the dithering-period limit.

Each correction was added to the execution prompt and the affected checks were
rerun before the next full assessment.

## Final assertions

- The canonical header has fixed-width, explicitly aligned layouts; immutable
  ioctl encodings; bounded arrays/durations; separate route, mode,
  compatibility, state, and reason identities; no raw addresses; and no
  arbitrary GPIO selection.
- The ABI test freezes all structure sizes, critical offsets, ioctl namespace,
  command numbers/directions/sizes, enums, capabilities, and limits examined.
- Byte identity is locked by SHA-256 and both identical-copy success and
  one-byte-drift failure are exercised.
- The manifest defaults to `Unavailable`, is closed to unknown properties,
  keeps GPIO4/GPIO20 distinct, prevents live eligibility for unavailable,
  rejected, and compatible-unqualified entries, and requires complete evidence
  classes for qualified entries.
- The Kbuild objects are route-neutral. Source scanning found no platform or
  misc registration, DT mapping, clock/DMA/pinctrl acquisition, raw MMIO,
  private-symbol lookup, or hardware-control calls. Every future API seam
  returns unavailable or has no effect.
- SPDX policy matches `LICENSE.md`; clean implementation provenance is
  recorded; repository-relative documentation links and whitespace pass.
- Documentation states that contracts/skeleton exist while functional module,
  endpoint, overlay, DKMS package, target behavior, and qualification do not.

No uncorrected objective Phase 2A finding remains in the evidence examined.

## Exact final checks

`make check` passed SPDX, UAPI digest, native manifest invariants, inert-source
scan, documentation links, ShellCheck, host C ABI compilation/assertions,
positive/negative UAPI copy identity, and `git diff --check`.

A full draft-2020-12 validator was unavailable, so manifest checking used JSON
parsing and repository-native structural/safety assertions. Representative
Linux kernel headers were not present on this macOS host, so no kernel-header
module build was attempted. These are remaining validation classes, not
evidence of a contract failure and not authorization to download headers,
access a target, install, or load the skeleton.

## Safety boundary

No module build, DKMS action, installation, load, bind, device creation,
overlay, target access, system change, clock, DMA, pinctrl, GPIO, transmission,
SDR, or RF operation was performed.
