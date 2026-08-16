<!-- SPDX-License-Identifier: MIT -->

# RP1 GPCLK DKMS

`RP1-GPCLK-DKMS` is the planned stock-kernel, out-of-tree Linux module for
bounded control of Raspberry Pi RP1 GPCLK0 resources on behalf of WsprryPi.
It is intended to be distributed as source and compiled locally for the
operator's installed kernel through DKMS.

The project exists so WsprryPi can support Raspberry Pi 5-family RP1 hardware
without distributing or maintaining a custom kernel. The stock Raspberry Pi
`clk-rp1` driver remains installed and authoritative for ordinary CPU-side
clock operations.

## Current status

Phase 2A public contracts and a kernel source skeleton are implemented. Phase
2B adds a portable lifecycle core and deterministic host tests for
ownership, leases, generations, bounded request validation, finite work,
STOP/RELEASE, stable terminal outcomes, stale-event rejection, and cleanup
faults. Phase 2C adds a platform driver, reference-counted misc endpoint, and
fail-closed discovery of the GPCLK0 DT, clock, pinctrl, and DMAengine resources.
It derives and DMA-maps the divider target from the provider resource.
Phase 2D adds an explicit prerelease module version, DKMS build configuration,
and identity-specific representative stock Raspberry Pi kernel-header build
evidence. Phase 2E adds the GPIO4 safe/default overlay, exact resource and UAPI
identity checks, and a bounded target lifecycle runner. The complete
clock-disabled matrix passed on the recorded `wspr5` Pi 5 / stock
`6.18.34+rpt-rpi-2712` identity; this closes the Phase 2 gate for that exact
identity while retaining the `Compatible-unqualified` compatibility ceiling.
Phase 3 now injects GPIO20 as the second independently allowlisted route,
requires exact route/pin pairs, adds a route-specific safe/default overlay, and
freezes UAPI ABI 1 plus the first overlay/name/manifest contracts. Phase 3B's
complete clock-disabled target matrix passed independently for GPIO4 and
GPIO20 on the recorded `wspr5` identity. This closes the Phase 3 target gate
for that exact identity while retaining the `Compatible-unqualified` ceiling;
neither route inherits evidence from the other. Phase 4A implements the bounded
stock-kernel submission, state, STOP, DMA-pacing, exact-readback, and restoration
path behind an immutable-at-load `live_output` gate. Its complete two-route
clock-disabled regression passed on the same exact `wspr5` identity with the
gate false.

`QUERY`, `ACQUIRE`, `SUBMIT_WSPR`, `SUBMIT_EVENTS`, `STOP`, `GET_STATE`, and
`RELEASE` now have production dispatch. With `live_output=false`, submission is
rejected before plan allocation or any pinctrl, clock, tick, or DMA mutation;
`LIVE_ELIGIBLE` is not reported. The implementation and build evidence do not
qualify GPIO output, timing, a mode, or RF, and do not generalize to another
kernel, DT, firmware, route, or host. Phase 5 includes a guarded
output-disabled DKMS install transaction and an offline-tested Gate D
coordinator for upgrade, downgrade, rollback, checkpoint recovery,
exact-version removal, complete and repeated removal, reinstall,
output-disabled UAPI query/acquire/release, and explicit unbind/rebind. Its
concrete execution instance remains fail-closed and non-executable. Frozen
`0.0.0-phase5.2` is retained as the genuine predecessor; distinct successor
`0.0.0-phase5.42` is the selected frozen development successor. The output-disabled open and owner
injector is separately tested and excluded from package bytes. Thirteen rows
remain blocked by exact manifest or representative-system inputs, and no
representative-system lifecycle row has executed. No qualified GPIO output is
implemented.

Phase 5.2 adds a deterministic, machine-verified release unit and an explicit
output-disabled DKMS, signing, overlay, and diagnostic tool surface. The
release compatibility manifest is populated deny-by-default with no positive
runtime entries; Phase 4 evidence belongs to an earlier exact module identity.
See the [release-unit contract](docs/contracts/phase5-2-release-unit-execution-prompt.md)
and [operator lifecycle guide](docs/operator/lifecycle.md).

Phase 5.8 freezes the bounded read-only diagnostic contract and its six
operator-visible outcome categories. Diagnostics report package, kernel,
module, endpoint, UAPI, manifest, route, enrollment, cleanup, hardware
identity, scoped kernel-log, and interrupted-transaction residue evidence;
they never load, configure, repair, or operate hardware. See the
[diagnostics guide](docs/operator/diagnostics.md).

The comprehensive [Phase 5 exit-gate execution prompt](docs/contracts/phase5-exit-gate-execution-prompt.md)
audits the remaining contract-to-implementation and external evidence gates.
Its [adversarial assessment](docs/reviews/phase5-exit-gate-adversarial-assessment.md)
records why passing offline policy tests is not yet a Phase 5 exit.

Nothing in this repository generally authorizes module installation, target
binding, system configuration, GPIO operation, transmission, or RF activity;
each target task still requires explicit bounded authority.

## Intended scope

This project will own:

- the loadable RP1 GPCLK kernel-module source;
- Kbuild and DKMS packaging;
- route-specific device-tree overlay sources;
- the canonical bounded and versioned UAPI;
- compatibility and provenance metadata;
- module signing, installation, update, rollback, removal, and diagnostics;
- kernel-header, lifecycle, static-contract, and target safety tests; and
- tagged source releases with checksums.

The allowlisted routes are GPIO4 and GPIO20. They share route-neutral module
machinery but use separate one-route overlays and compatibility evidence.
Neither route inherits the other's qualification.

## Project boundary

- [`WsprryPi/RP1-GPCLK-DKMS`](https://github.com/WsprryPi/RP1-GPCLK-DKMS)
  owns kernel-facing implementation and releases.
- [`WsprryPi/WSPR-Transmitter`](https://github.com/WsprryPi/WSPR-Transmitter)
  owns its userspace adapter and translation into the UAPI.
- [`WsprryPi/WsprryPi`](https://github.com/WsprryPi/WsprryPi) owns backend
  policy, configuration, scheduling, installer orchestration, operator
  workflow, and product qualification.

The projects coordinate through tagged artifacts, a canonical UAPI, explicit
compatibility manifests, and cross-repository checks. WsprryPi must not build
from this project's moving default branch.

See the [module engineering contract](docs/contracts/rp1-gpclk-dkms-module-contract.md)
and the upstream [WsprryPi product contract](https://github.com/WsprryPi/WsprryPi/blob/eb1c933ec20147aae987f06a2b8e4f1d988c00f6/docs/research/rp1-gpclk-stock-kernel-dkms-contract.md).

Phase 2 preparation is documented in the
[historical evidence index](docs/evidence/historical-evidence-index.md),
[source provenance policy](docs/development/provenance.md),
[UAPI conceptual baseline](docs/development/uapi-baseline.md),
[compatibility identities](docs/development/compatibility-identities.md), and
[historical artifact inventory](docs/development/historical-artifact-inventory.md).
The first accepted architecture decision is to
[start a clean DKMS UAPI](docs/development/decisions/0001-clean-dkms-uapi.md).
The Phase 2A choices are frozen in
[Decision 0002](docs/development/decisions/0002-phase2a-public-contracts.md),
and the exact bounded slice is preserved in the
[Phase 2A execution prompt](docs/contracts/phase2a-public-contracts-execution-prompt.md).
The Phase 2B lifecycle choices are recorded in
[Decision 0003](docs/development/decisions/0003-phase2b-portable-lifecycle.md),
with its bounded work preserved in the
[Phase 2B execution prompt](docs/contracts/phase2b-portable-lifecycle-execution-prompt.md).
Its independent offline result is recorded in the
[Phase 2B adversarial assessment](docs/reviews/phase2b-adversarial-assessment.md).
The Phase 2C slice is preserved in its
[execution prompt](docs/contracts/phase2c-kernel-resource-integration-execution-prompt.md)
and [Decision 0004](docs/development/decisions/0004-phase2c-resource-integration.md).
Its bounded offline result is recorded in the
[Phase 2C adversarial assessment](docs/reviews/phase2c-adversarial-assessment.md).
The Phase 2D build slice is preserved in its
[execution prompt](docs/contracts/phase2d-representative-build-qualification-execution-prompt.md).
Its exact build identities and bounded result are in the
[representative build evidence](docs/evidence/phase2d-representative-build-qualification.md),
with the separate
[Phase 2D adversarial assessment](docs/reviews/phase2d-adversarial-assessment.md).
The separately authorized target slice is preserved in the
[Phase 2E execution prompt](docs/contracts/phase2e-clock-disabled-target-execution-prompt.md),
with its exact [target evidence](docs/evidence/phase2e-clock-disabled-target.md),
[Decision 0005](docs/development/decisions/0005-phase2e-gpio4-clock-disabled.md),
and independent
[Phase 2E adversarial assessment](docs/reviews/phase2e-adversarial-assessment.md).
The Phase 3 implementation and interface freeze are preserved in
the [Phase 3 execution prompt](docs/contracts/phase3-gpio20-interface-freeze-execution-prompt.md),
[GPIO20 route evidence](docs/development/gpio20-route-evidence.md),
[Decision 0006](docs/development/decisions/0006-phase3-interface-freeze.md),
and [Phase 3 adversarial assessment](docs/reviews/phase3-adversarial-assessment.md).
The separately authorized closure is recorded in the
[Phase 3B execution prompt](docs/contracts/phase3b-clock-disabled-route-closure-execution-prompt.md),
[target evidence](docs/evidence/phase3b-clock-disabled-route-closure.md), and
[Phase 3B adversarial assessment](docs/reviews/phase3b-adversarial-assessment.md).

The canonical header is
[`include/uapi/linux/rp1_gpclk.h`](include/uapi/linux/rp1_gpclk.h). The strict,
deny-by-default compatibility format is
[`schema/rp1-gpclk-compatibility-manifest-v1.schema.json`](schema/rp1-gpclk-compatibility-manifest-v1.schema.json).
Run the offline contract suite with `make check`. Building the module source
requires an explicitly supplied local kernel build directory, for example
`make KERNEL_BUILD=/path/to/kernel/build`; it is never installed or loaded by
the repository build.

## Safety model

The design is fail-closed. Unknown or unsupported kernel, hardware, device-tree,
resource, signing, route, capability, or cleanup states must leave RP1 output
unavailable. It will not fall back to `/dev/mem`, raw userspace MMIO, a custom
kernel, or another physical transmitter backend.

The stock-kernel module cannot reproduce the stronger provider-private lease
used by the historical custom-kernel proof of concept. Cooperative kernel
resource ownership and explicit operator exclusions reduce risk but cannot
prove the absence of direct-MMIO or uncoordinated interference.

## Licensing

Original project work is MIT licensed wherever that is practical. Kernel-facing
module source is dual-licensed under `GPL-2.0-only OR MIT`, and the module will
declare `MODULE_LICENSE("Dual MIT/GPL")`. Userspace-visible UAPI headers are
intended to use `(GPL-2.0-only WITH Linux-syscall-note) OR MIT`.

See [LICENSE.md](LICENSE.md) for the authoritative per-file policy. Third-party
or adapted material retains its original license and attribution.

## Development

Read [AGENTS.md](AGENTS.md) and the module contract before working in this
project. Ordinary development and validation must remain offline,
unprivileged, hardware-free, and safe to repeat unless an exact target action
is separately authorized.

Compilation demonstrates build compatibility only. It does not qualify module
loading, GPIO timing, coexistence, cleanup, transmission, RF behavior, or an
operator installation path.
