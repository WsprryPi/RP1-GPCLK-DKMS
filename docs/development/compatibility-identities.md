<!-- SPDX-License-Identifier: MIT -->

# Compatibility identities

## Principle

Compatibility is an exact evidence claim. A header or DKMS build establishes at
most `Compatible-unqualified`. Unknown prerequisites are `Unavailable`;
known unsafe combinations are `Rejected`.

## Demonstrated historical identities

### Stock probe and DMA baseline

- host label `wspr5`
- Raspberry Pi 5 Model B Rev 1.0, revision `c04170`
- `aarch64`, Debian 13.6
- kernel `6.18.34+rpt-rpi-2712`, package `1:6.18.34-1+rpt1`
- provider compatible `raspberrypi,rp1-clocks`
- historical `clk_gp0`, clock ID 33
- GPIO4 on `gpiochip0`
- Raspberry Pi Linux `89586905b8603e545cce9089a81f5f35d65bc998`
- observed CPU physical `DIV_FRAC` `0x1f0001817c`
- observed translated DMA address `0xc04001817c`
- DMA request `RP1_DMA_DMA_TICK_TICK0` (`0x30`)

Addresses and numeric identities are observations, not portable constants. The
module must derive and validate provider resources, offsets, and translation.

### Custom-provider baseline

- custom kernel `6.18.44-v8-16k+`
- Phase 7A parent `dbfb9b3d0b41a864dcae923ef3dce0c9b508562d`
- WSPR-Transmitter `fe8a03b17a817175553968f91508fccd48c78bdf`
- provider source version `D33AD651DB5EA8776DE0AAF`
- GPIO4, clock disabled, prepare/enable counts zero

This validates historical algorithms and failures, not stock DKMS behavior.

## Required build identity

Record module tag/commit, archive checksum, UAPI version/header checksum,
architecture, compiler, exact kernel release/build, headers/package,
configuration checksum, symbol-version context, exported symbols, page size,
preemption configuration, vermagic, signing result, and diagnostics.

## Required runtime identity

Validate Pi model/revision, authoritative RP1 identity when available, kernel,
relevant firmware/bootloader, base DT identity, overlay version/parameters and
checksum, provider and clock arguments, resource start/size and relative
offsets, DMA controller/request, route/pinctrl states, module/UAPI/signature,
and the matching compatibility-manifest entry.

Do not expose raw addresses to userspace merely for identity reporting.

## Unknowns requiring target evidence

- supported stock Raspberry Pi kernel range;
- provider-layout stability across RP1/DT/firmware revisions;
- stock ownership of DMA-tick resources;
- authoritative GPIO20 GPCLK0 pinmux/overlay representation;
- unbind and overlay removal with open descriptors;
- representative signing/key-enrollment behavior;
- APT update, downgrade, rollback, and recovery; and
- coexistence with cooperative consumers and common overlays.

## State rules

- Build success: no higher than `Compatible-unqualified`.
- Unknown/missing prerequisite: `Unavailable`.
- Known unsafe state or cleanup fault: `Rejected`.
- Clock-disabled gates plus explicit enrollment: potentially `Experimental`,
  subject to the product contract.
- Only exact complete route/mode/timing/cleanup/recovery/RF evidence:
  `Qualified`.
- Relevant kernel, DT, firmware, overlay, module, or UAPI changes demote the
  result unless an explicit manifest rule recognizes them.
