<!-- SPDX-License-Identifier: MIT -->

# Decision 0006: Phase 3 GPIO20 injection and first interface freeze

- Status: Accepted; exact Phase 3B clock-disabled target gate passed
- Date: 2026-08-14
- Scope: route model and first public module-facing contracts

The module accepts exactly two administrative route/pin pairs: GPIO4/4 and
GPIO20/20. One route-specific overlay may bind the shared GPCLK0/DMA endpoint
at a time. The second overlay uses the same route-neutral driver and UAPI;
neither overlay references the other pin. Invalid routes and inconsistent
route/pin declarations fail before resource acquisition.

The first public UAPI ABI is frozen at version 1 with the exact bytes recorded
in `uapi-identity.json`. Numeric assignments, ioctl identities and directions,
structure sizes and offsets, reserved fields, flags, capabilities, and meanings
are immutable. Future evolution is additive or uses a deliberately new
version/command.

The following names and DT contract are frozen: module `rp1_gpclk_dkms`, device
`rp1-gpclk`, compatible `wsprrypi,rp1-gpclk-dkms-v1`, properties
`wsprrypi,route` and `wsprrypi,pin`, state names `default`, `active`, `safe`,
and overlay sources `rp1-gpclk-gpio4.dts` and `rp1-gpclk-gpio20.dts`.

Compatibility-manifest schema version 1 is frozen with default `Unavailable`,
the published state/route/mode vocabularies, module/build/runtime/artifact
identity fields, and route-specific evidence. Evidence naming both routes does
not allow one route's qualification classes to satisfy the other route's
entry; each entry must be validated against evidence that contains its route.

This decision freezes contracts, not general compatibility or live-output
qualification. The separately authorized Phase 3B matrix passed GPIO4 and
GPIO20 pinctrl identity, conflict, cleanup, descriptor/process lifetime, and
repeated route changes on the exact recorded target. Timing, active pinctrl,
live-output, and RF gates remain unresolved and separately authorized. GPIO4
and GPIO20 evidence remain distinct; neither satisfies the other's row.
