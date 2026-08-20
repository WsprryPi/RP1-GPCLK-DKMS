<!-- SPDX-License-Identifier: MIT -->

# GPIO20 RP1 GPCLK0 route evidence

Date reviewed: 2026-08-14
Upstream line: Raspberry Pi Linux `rpi-6.18.y`
Evidence class: source and device-tree representation only

The authoritative Raspberry Pi RP1 pinctrl driver lists one group per RP1 GPIO,
including `gpio20`, and maps GPIO20's function slot 3 to `gpclk0`:

- [`drivers/pinctrl/pinctrl-rp1.c`, RP1 groups and function table](https://github.com/raspberrypi/linux/blob/rpi-6.18.y/drivers/pinctrl/pinctrl-rp1.c#L340-L517)
- [raw source used for independent inspection](https://raw.githubusercontent.com/raspberrypi/linux/rpi-6.18.y/drivers/pinctrl/pinctrl-rp1.c)

The same table maps GPIO4's slot 0 to `gpclk0`. GPIO20 is therefore not a copy
of GPIO4's selector position; the generic pinctrl function name is the stable
device-tree representation that lets the RP1 driver select the correct mux.

The Phase 3 GPIO20 overlay consequently uses:

```dts
function = "gpclk0";
pins = "gpio20";
```

Its future active state requests 2 mA, while both default and safe states use
GPIO input with bias disabled. The module never selects the active state in
Phase 3. The overlay binds GPCLK0 and the same validated RP1 DMA TICK0 endpoint
as GPIO4, but declares route 2 and pin 20. Exact route/pin-pair validation
prevents a property-only mismatch from being accepted.

This establishes source-level pinmux capability and DT representation. It does
not establish target pinctrl acceptance, header electrical behavior, conflict
cleanup, timing, live output, RF behavior, or qualification. Those remain
route-specific target evidence gates.
