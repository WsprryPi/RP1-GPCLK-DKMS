<!-- SPDX-License-Identifier: MIT -->

# Exact-target execution and adversarial assessment

**Executed on wspr5 with user authorization. Final state: runtime GPIO20 selected,
consumer/controller loaded, output disabled, WsprryPi masked and stopped.**
The user confirmed physical isolation/termination and disabled shared sources
before the first target mutation. No transmission/RF output was requested.

## Deployment and migration

Initial read-only inventory confirmed Pi 5 Model B Rev 1.0, aarch64,
6.18.34+rpt-rpi-2712, firmware-owned GPIO20, live_output=N, no endpoint holder and
zero GPCLK enable/prepare counts. The predecessor's installed/decompressed bytes
and loaded build note matched. The target boot config differed from the header
build config only by omission of CONFIG_BUILD_SALT and an empty
CONFIG_SYSTEM_TRUSTED_KEYS setting; signing and lockdown were disabled.

The actual administrator service file and compressed predecessor were preserved
by exact hash before masking or moving them. Root-owned backups are under
`/var/lib/rp1-gpclk-dkms/runtime-test-a0f2794`. Only the owned firmware route block
was removed; kernel/initramfs selection and unrelated boot settings were retained.
The first reboot established a neutral tree and masked/inactive application.
The initial neutral-node review was overbroad and stopped on stock provider pin
labels before moving any module. Comparing the exact six canonical names used by
the controller distinguished those base definitions from owned route nodes; none
of the canonical route nodes remained. No runtime removal of firmware ownership
was attempted.

The exact installed bundle and bootstrap hashes were verified, the target plan
reviewed and executed, and module resolution and loaded build notes checked.
The actual systemd socket accepted runtime-profile queries and mutations. The
package executable and source-development drop-in remain preserved.

## Finding, repair and repeat assessment

The first GPIO4 → GPIO20 → GPIO4 sequence and cleanup succeeded, but kernel logs
reported allocation-leak warnings for each exported `/__symbols__` property. This
was an actionable failed assessment, not a clean run. Both modules were unloaded
from clean no-route state before repair.

Runtime generation now removes only compiled `/__symbols__` exports. A regression
compares all remaining decoded nodes/properties against the canonical overlay,
including phandles and both fixup tables. Packaged firmware overlay generation and
the canonical DTS files are unchanged; downstream overlays cannot reference runtime
route labels. The controller was rebuilt against the same cached exact headers
using GCC 14.2.0 (Debian 14.2.0-19), with networking disabled. Consumer bytes matched
the preceding build exactly. The repaired binding and controller hashes are in
[symbolfix-build.json](symbolfix-build.json).

The coherent repaired update passed on the neutral target. Its GPIO4 → GPIO20 →
GPIO4 sequence, explicit cleanup to no route, and subsequent GPIO20 selection all
passed in one boot with no new kernel warnings. The old and new deployment/route
journals were retained. A second authorized reboot discarded allocations from the
initial warned build and verified fresh startup; it was not needed to switch
routes. A supported neutral deployment reset archived/cleared completed session
journals first, rather than silently adopting an old controller session.

On fresh boot `41d02ec7-c78c-4f25-9406-86e4d401d1c9`, the repaired build again passed
GPIO4 → GPIO20 → GPIO4 → GPIO20. All four operations shared that boot and controller
session; generations were 1, 3, 5 and 7 with errno zero. Every step independently
verified one expected DT route/pin and platform binding, exact loaded notes,
live_output=N, zero endpoint holders, input-mode pins, zero GPCLK enable/prepare
counts and persistent application masking. Overlay ID reuse was accompanied by
new generations; ID equality alone was not used as proof of ownership continuity.

The complete fresh-boot kernel-log review found no overlay allocation warnings,
WARNING, BUG, Oops, call-trace or use-after-free matches. Expected out-of-tree
module taint was recorded. Stale-token and legacy mutation requests were also
rejected with unchanged observed state in the initial run; manager bytes were
unchanged in the repair. No remaining actionable finding was identified within
this bounded clock-disabled test scope. This is not proof of absence of all leaks,
interference or lifetime defects under untested conditions.

## Evidence and limits

[results.json](results.json) retains the initial warned run, repaired run, fresh-boot
run, deployment plans, independent observations, rejection evidence and cleanup
proof. The raw DMA summary reports channel allocation, not an independent DMA
activity measurement; no DMA program or clock output was submitted. Software
clock/pin observations are not a measurement of electrical silence.

The full offline suite passes, including 16 controller/admin tests and 16
manager/deployment tests, with the real controller ioctl fixture. The repaired
opt-in pair compiles against the reviewed headers. Documentation links, SPDX and
whitespace checks pass. The application source/binary, transmission UAPI and
licensing policy are unchanged; new tooling/tests/docs remain MIT.

Final runtime route is GPIO20 with the repaired binding
`66e3bda60fa91c4ec8035d9af4471f070edb8b4a48a485e5f6c2ce032548f16d`.
The controller intentionally retains its owned overlay and module reference.
The application remains masked/stopped, and the firmware configuration remains
neutral: runtime GPIO20 selection is not automatically restored after reboot.
No normal application restart, output authorization, release or RF qualification
was performed. The companion application remains an offline-tested separate
branch; its binary/browser workflow was not deployed in this test.

Target crash injection, busy-owner failure injection, kernel notifier/removal
error injection, broader kernel/board coverage and endurance testing remain
unperformed. Offline injected-failure evidence is not promoted to target proof.
These results establish limited exact-artifact clock-disabled rebootless switching
and normal cleanup observations, not production or transmission readiness.
