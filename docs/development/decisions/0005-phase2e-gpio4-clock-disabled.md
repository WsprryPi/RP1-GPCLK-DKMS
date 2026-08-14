<!-- SPDX-License-Identifier: MIT -->

# Decision 0005: Phase 2E GPIO4 clock-disabled target boundary

- Status: Accepted for the exact recorded target identity
- Date: 2026-08-14
- Scope: GPIO4 resource and lifecycle administration with output disabled

The Phase 2 endpoint implements only `QUERY`, `ACQUIRE`, and `RELEASE` for
administrative ownership tests. It advertises route and compatibility identity
plus cleanup-fault reporting, but no submit or STOP capability. All output
operations remain `EOPNOTSUPP`.

The production overlay identifies route GPIO4, GPCLK0, and RP1 DMA TICK0
(specifier `0x30`). Its default and safe states are GPIO input; the active
GPCLK state exists
for a later phase but Phase 2 code never selects it. The module validates exact
clock/DMA providers, arguments, common RP1 parent, provider resource bounds,
and the derived fractional-divider target before binding. Mapping uses the
allocated DMA controller device.

The exact composite GPCLK0/GPIO4/DMA-request endpoint has one module-owned
claim. A successful compare/exchange claim is released only after reverse
resource teardown, with release ordering before another claimant may enter.
This supplements cooperative kernel clock, pinctrl, and DMA ownership; it does
not exclude direct MMIO or hostile/uncoordinated kernel software.

On `wspr5`, stock kernel `6.18.34+rpt-rpi-2712`, the full clock-disabled matrix
proved build/load identity, local signing, production bind, pin and duplicate
endpoint conflicts, single-owner UAPI behavior, open-descriptor unbind/unload,
process-death cleanup, partial-probe unwind, simulated missing-header update
failure, known-good recovery, exact diagnostic attribution, and final removal.
GPIO4 remained input and GPCLK0 prepare/enable remained zero throughout.

This closes Phase 2 only for the exact recorded identity. The compatibility
state remains `Compatible-unqualified`; administrator enrollment may be a
future prerequisite for `Experimental`. GPIO20, active clock/DMA execution,
timing, transmission, RF, DKMS packaging, enforced module-signing policy, and
other target identities remain outside this decision.
