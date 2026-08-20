<!-- SPDX-License-Identifier: MIT -->

# Decision 0004: Phase 2C clock-disabled resource integration

- Status: Accepted for offline prototype evidence
- Date: 2026-08-14
- Scope: Linux object/resource integration with no executable output path

The platform object is heap allocated and owns one platform reference. Each
successful open takes another reference under the same mutex used to publish
the permanent dead state. Removal deregisters the endpoint, marks the object
dead, marks the portable core `DEAD / PROVIDER_REMOVED`, quiesces the inert
execution layer, releases resources, and drops the platform reference. Open
files may close after removal; the last reference destroys the object.

Resource acquisition is DT identity, clock rate exclusion, pinctrl ownership,
and DMAengine channel/resource mapping, in that order. Cleanup is exact reverse
order and idempotent. Pinctrl states are looked up but never selected. No clock
is prepared, enabled, or changed. No DMA descriptor is prepared or submitted.

The accepted provider identity is `raspberrypi,rp1-clocks`, one clock argument
equal to GPCLK0 ID 33, provider resource zero, and aligned `DIV_FRAC` offset
`0x17c`. Checked containment derives the CPU physical target. The consumer
maps that resource with `dma_map_resource()` and never treats a fixed absolute
address as a contract.

The stock common-clock consumer API has no acceptable query that proves
GPCLK0 has no existing prepare/enable owner. The exported `__clk_is_enabled()`
provider interface is intentionally rejected as a production dependency under
the module contract. Exclusive rate protection is narrower than enable
ownership. Therefore Phase 2C exposes no operational ioctl and makes no
startup-conflict, coexistence, loadability, or target-safety claim. A later
reviewed target gate must resolve this activation precondition without private
symbols before an output path can be authorized.
