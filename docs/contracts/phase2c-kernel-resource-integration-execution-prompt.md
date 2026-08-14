<!-- SPDX-License-Identifier: MIT -->

# Phase 2C kernel resource integration execution prompt

## Outcome and boundary

Implement and adversarially review the clock-disabled Linux integration layer
that binds the Phase 2B policy core to a reference-counted platform object and
a restrictive misc-device lifetime. Discover, validate, acquire, and unwind
the GPIO4 feasibility resources using supported exported APIs. Derive the
GPCLK0 fractional-divider DMA target from the authoritative clock-provider
device-tree resource and map that resource through the consumer DMA device.

This is source and offline-build work only. Do not install, load, bind, unbind,
or remove the module; apply an overlay; access a Raspberry Pi; prepare, enable,
or change a clock; select a pinctrl state; prepare, submit, issue, terminate, or
synchronize DMA; change GPIO state; transmit; or produce RF. The registered
endpoint must reject every ioctl and there must be no live-output parameter or
path.

## Authorities and identities

Follow `AGENTS.md`, the module engineering contract, phased plan, frozen V1
UAPI, and accepted Phase 2A/2B decisions. For this slice the only accepted DT
identity is:

- consumer compatible `wsprrypi,rp1-gpclk-dkms-v1`;
- one `clocks` entry named `gpclk`;
- provider compatible `raspberrypi,rp1-clocks`;
- exactly one clock argument equal to RP1 GPCLK0 ID 33;
- provider resource index zero; and
- GPCLK0 `DIV_FRAC` offset `0x17c`, contained as one aligned 32-bit register
  inside that translated resource.

The register offset is a reviewed compatibility datum from the identified
stock `clk-rp1` source, not a fixed physical address. Unknown identities,
extra clock arguments, missing names/resources/states/channels, arithmetic
overflow, invalid DMA mapping, or contention fail closed.

## Required implementation

- Add one platform driver and dynamically allocated device object. Hold a
  platform reference plus one reference for every successful open. Removal
  first deregisters the misc endpoint, atomically marks the object dead,
  synchronously quiesces the still-inert execution layer, releases only owned
  resources, clears driver data, and drops the platform reference. Final
  memory destruction occurs only after the last file closes.
- Register a misc device only after all resources are acquired. Use mode
  `0600`. Open must reject a dead object and take its reference while protected
  by the same lock used by removal. Release must perform owner-close policy
  before dropping the file reference. Allocate nonzero owner identities
  without signed wrap; permanent exhaustion fails closed. All ioctls remain
  `-EOPNOTSUPP`.
- Parse the actual clock phandle and validate provider compatible, argument
  count, exactly one clock/name pair, memory-resource type, and GPCLK0 ID
  before acquiring the clock. Obtain exclusive rate
  protection and never prepare, enable, or change its rate in this slice. The
  stock consumer API exposes no acceptable GPCLK enable/prepare ownership
  query: do not depend on provider-internal `__clk_*` interfaces. Consequently
  the Phase 2C endpoint remains ioctl-inert; a later reviewed target gate must
  establish an acceptable startup-conflict check before activation exists.
- Obtain named `default`, `active`, and `safe` pinctrl states without selecting
  any state. Obtain the named exclusive DMAengine channel `tx` without
  preparing or submitting work.
- Translate provider resource zero with `of_address_to_resource()`. Use checked
  arithmetic and containment to derive the CPU physical divider register.
  Convert it for this consumer with `dma_map_resource()` and retain the exact
  mapped address only while owned. Reject mapping failure; unmap it exactly
  once before releasing the DMA channel.
- Express acquisition state explicitly. A failure at every step must unwind in
  exact reverse order. Release must be idempotent and must not release or
  restore anything not acquired by this module. Pinctrl ownership must be
  explicitly released between DMA and clock release; managed cleanup deferred
  beyond clock release does not satisfy this ordering assertion.
- Keep cancellation bounded structurally: no descriptor can exist in Phase
  2C, quiesce prevents successors and therefore has zero residual work. Do not
  claim this proves real DMA cancellation.

## Deterministic evidence

Add host-side tests for aligned checked target derivation, lower/upper
containment, too-small resources, overflow, wrong provider/ID/argument count,
and an acquisition fault at every boundary. Assert exact reverse-order cleanup,
one release per acquisition, idempotent release, dead-open rejection, retained
open lifetime after removal, and final destruction after the last close.

Update the offline checks so forbidden live-output operations remain absent,
the endpoint remains mode `0600` and ioctl-inert, and registration/resource
APIs required by this phase are present. Run strict host compilation, repeated
tests, sanitizers when available, documentation/link/SPDX/UAPI/manifest checks,
whitespace checks, and representative Raspberry Pi kernel-header builds when
headers are available. Record exact skips.

## Adversarial exit loop

Separately attempt to falsify provider and clock identity, resource
containment, CPU-to-DMA translation, exclusive acquisition, reverse unwind,
dead/open/remove races, final-reference destruction, ioctl inertness, zero
descriptor/output behavior, bounded quiesce, licensing, and evidence claims.
Use targeted source mutations for the derivation containment guard and the
open-after-dead guard. Reinject each objective finding into this prompt or its
decision record, correct it, rerun affected and complete checks, and repeat
until no finding remains.

## Exit statement

Passing Phase 2C establishes only source-level integration, deterministic host
policy, and any explicitly recorded build identities. It does not establish
module loadability, probe success, DT/overlay correctness on a target, DMA
translation correctness on RP1, clock/pinctrl coexistence, cleanup under real
callbacks, GPIO behavior, timing, transmission, or RF qualification. The Phase
2 gate remains open pending separately authorized clock-disabled target work.
