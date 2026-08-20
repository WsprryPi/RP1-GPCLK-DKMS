<!-- SPDX-License-Identifier: MIT -->

# Phase 2C adversarial assessment

Date: 2026-08-14
Scope: clock-disabled platform, misc-device, resource, and object lifetimes
Result: pass for the offline evidence examined after three correction cycles

## Method

The assessment separately attempted to falsify the Phase 2C execution prompt,
Decision 0004, provider/clock identity, target containment, CPU-to-DMA resource
mapping, exclusive acquisition, partial unwind, dead/open/remove ordering,
final-reference destruction, ioctl inertness, and the prohibition on clock,
pinctrl, descriptor, GPIO, and output operations. It used source review,
deterministic host models, strict compilation, repeated execution,
ASan/UBSan, Clang static analysis, forbidden-interface scanning, and targeted
containment-guard and dead-open-guard mutations.

## Reinjected findings and resolutions

1. The first acquisition design used managed pinctrl ownership, whose deferred
   cleanup could occur after explicit clock release. Pinctrl is now acquired
   and released explicitly, between DMA and clock cleanup, and the static
   contract checks that reverse ordering.
2. The first clock-conflict check called `clk_is_enabled()`, which is not a
   stock 6.12 consumer API. The available exported `__clk_is_enabled()` is a
   provider/internal interface prohibited by the engineering contract. That
   check was removed, Decision 0004 records the unresolved activation gate,
   and every ioctl remains unavailable. Exclusive rate protection is not
   represented as enable ownership.
3. Initial DT validation accepted additional clock entries and did not
   explicitly require a memory resource. It now requires one clock/name pair,
   one argument equal to ID 33, the exact provider compatible, resource zero
   of `IORESOURCE_MEM`, and checked aligned containment. File-owner allocation
   also now uses compare/exchange with a permanent `S64_MAX` exhaustion result
   rather than permitting signed atomic wrap.

## Final assertions

- The only accepted source identity is provider `raspberrypi,rp1-clocks`, one
  GPCLK0 argument with ID 33, and contained offset `0x17c` in provider memory
  resource zero. No fixed physical base is present.
- The divider CPU address is converted with `dma_map_resource()` for the
  consumer and unmapped exactly once before channel release.
- Resource failure unwinds DMA mapping, DMA channel, pinctrl, exclusive-rate
  ownership, and clock reference in reverse order. Repeated release is inert.
- Misc registration occurs last at mode `0600`. Open and removal serialize the
  dead check/reference acquisition. Removal deregisters, permanently marks
  dead, quiesces zero possible descriptors, releases resources, and leaves
  final allocation destruction to the last open-file close.
- No ioctl is operational. There is no module parameter or call that prepares,
  enables, or changes a clock; selects pinctrl; prepares, submits, issues, or
  terminates DMA; maps raw MMIO; changes GPIO; or produces output.
- The containment and dead-open mutations are killed by the offline evidence.

## Evidence and limitations

`make check` passes SPDX, UAPI identity, manifest structural checks, Phase 2C
source boundaries, documentation links, ShellCheck, the host ABI test, the 16
Phase 2B lifecycle groups twice, derivation/unwind/dead-lifetime tests twice,
ASan/UBSan, positive and negative UAPI-copy identity, and whitespace checks.
Clang static analysis completed without a diagnostic.

An official Raspberry Pi `rpi-6.12.y` sparse source tree was inspected at
`f7b06ac140e17a0e6d30fcc9ddeebc0e60943cea`. It confirmed the GP0 fractional
divider offset and revealed the invalid initial clock API. A representative
external-module build was attempted but not completed: kernel configuration
preparation stopped because the host has GNU Make 4.4 but no `ld.lld`; no
cross-kernel build result is claimed. The full JSON Schema validator is also
unavailable, so the native structural manifest check is the recorded evidence.

No module was installed, loaded, bound, unbound, or removed. No overlay,
Raspberry Pi, system configuration, pinctrl state, clock state, DMA engine,
GPIO, transmission, SDR, or RF activity was touched. This review does not
establish that a future overlay's automatically selected default pinctrl state
is safe, that RP1 DMA translation succeeds, that the platform object probes,
or that real callbacks and target cleanup are correct. The lack of an accepted
startup prepare/enable ownership check remains an explicit activation blocker.

No uncorrected objective Phase 2C finding remains in the offline evidence
examined. The Phase 2 hardware gate remains open.
