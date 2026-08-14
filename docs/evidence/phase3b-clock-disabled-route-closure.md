<!-- SPDX-License-Identifier: MIT -->

# Phase 3B clock-disabled route-closure evidence

Date: 2026-08-14
Target: `wspr5`
Result: pass; Phase 3 closed for this exact identity only
Compatibility ceiling: `Compatible-unqualified`

## Evidence identity and integrity

- Raspberry Pi 5 Model B Rev 1.0
- stock kernel/headers `6.18.34+rpt-rpi-2712`, Debian package
  `1:6.18.34-1+rpt1`
- boot ID `0f9d1f9b-c27b-4e6a-962f-b8e8ac3683d7`
- base FDT SHA-256
  `e7b48c32347c4862d354c2ed2001590bcd2165a3fa432395c74112095ed77212`
- compiler GCC 14.2.0 (`Debian 14.2.0-19`)
- exact source archive SHA-256
  `1661fe591240dc89fa17f4df8157b6b441f2edd34f77f1f7923de2e5bc916438`
- final evidence archive: `/tmp/rp1-gpclk-phase3b-evidence-6.tar.gz`
- final evidence archive SHA-256
  `d70055d4edf249ea2ef8a17735e4df0bde200375d625b53315caf449a89251a4`
- unsigned module SHA-256
  `71b919b9b87625bfe55fafcd408ab3aa967429c81f54ccec90e95d5619b683fa`
- production GPIO4 overlay SHA-256
  `ae4041aad58cc03cb0cdcf5a8de3b9d5322fd863035c09a4dcf8ede3239fcc96`
- production GPIO20 overlay SHA-256
  `e94d136931be70743020d1bf804f13a975d61cc7ec3470246e4b8daeccd7faae`

The target generated a relative-path source hash list and a `SHA256SUMS`
manifest covering every evidence file. The archive was downloaded, its outer
digest matched the target, it was extracted into a different directory, and
every inner hash verified. Earlier failed attempts were preserved locally;
each stopped or cleaned to GPIO4/GPIO20 input, zero clock prepare/enable/protect
counts, and no loaded overlay, module, device node, or client.
All tested implementation, overlay, runner, contract, and review files match
the final worktree. Only this evidence document changed after the target
snapshot to insert its final source and evidence archive digests; it does not
affect executable bytes.

## Exact runtime identity

Both production routes independently machine-validated UAPI ABI 1, route/pin
pairs GPIO4/4 and GPIO20/20, module/build/compatibility identifiers
`rp1-gpclk-dkms`, `0.0.0-phase3b`, and `phase3b-clock-disabled`, GPCLK0 ID 33,
provider resource `0x1f00018000` size `0x10038`, derived divider target
`0x1f0001817c`, and DMA request `0x30` under the same RP1 parent. Query reported
capabilities `0x70`, state `Compatible-unqualified`, and administrator
enrollment required.

## Matrix result

The complete runner passed warnings-fatal target compilation, strict UAPI and
DT identity checks, route mismatch, cross-route production-overlay rejection,
route-specific pin and DMA conflicts, missing-active and bad-DMA partial-probe
cleanup, owner process death and reacquisition, and three administrative cycles
in both GPIO4-to-GPIO20 and GPIO20-to-GPIO4 order.

For each route independently, unload failed while an existing descriptor was
open, unbind removed the device and released resources safely, a new open
failed, unload remained blocked by the old descriptor, close succeeded, and
rebind/recovery completed. A simulated missing-header update failed closed and
both known-good routes subsequently recovered.

The warning-or-higher dmesg delta contained exactly the 22 classified negative
fixture diagnostics and no severe or unclassified line. Final assertions found
both pins input, clock prepare/enable/protect `0/0/0`, no overlay, module,
device, installed module artifact, bound device, or client.

## Boundary

No active pinctrl state was selected. No clock was prepared, enabled, or
rate-changed. No DMA descriptor was prepared or submitted. No GPIO output,
transmission, RF, reboot, boot/configuration, service, or WsprryPi product
operation occurred. This result does not qualify timing, jitter, divider
programming, cancellation under live work, active restoration, GPIO output,
any transmission mode, RF, another kernel/DT/firmware, enforced signing, or
upgrade/rollback workflows. GPIO20 does not inherit GPIO4 qualification.
