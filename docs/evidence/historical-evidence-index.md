<!-- SPDX-License-Identifier: MIT -->

# Historical RP1 evidence index

## Purpose

This index makes the DKMS project independent of chat history without copying
WsprryPi's historical reports and target logs. Links identify immutable
repository objects. Evidence remains authoritative only for the exact system
and operation recorded in its source report.

The WsprryPi parent was inspected at
`d50dbf9447cdf72e49f8e94278516c6a08313ca6`; its recorded
WSPR-Transmitter submodule was inspected at
`747db7e5f8b857c432eb96b05e74944de6b58940`. These inspection tips are
not qualification identities.

## Evidence classes

- **Design evidence:** informs requirements; it is not runtime qualification.
- **Clock-disabled target evidence:** exercised RP1 while GPCLK output remained
  disabled.
- **Historical live evidence:** exercised the custom provider and does not
  qualify the DKMS module.
- **Application evidence:** informs the consumer contract but remains owned by
  WsprryPi.

## Core evidence

| Evidence | Immutable source | Supported claim | Disposition and limitation |
| --- | --- | --- | --- |
| Phase 4 RF-inhibited probe | [report at `0a5d1de`](https://github.com/WsprryPi/WsprryPi/blob/0a5d1de5445b4941be141b000a5b4967ab96ca0e/docs/research/rp1-gpclk-phase4-rf-inhibited-probe.md) | Pi 5 Rev 1.0, kernel `6.18.34+rpt-rpi-2712`, RP1 GP0 clock ID 33, GPIO4 kept disconnected. | Revalidate every identity. The ownership probe itself changed pin state, so cleanup cannot assume a probe is neutral. |
| Phase 6C DMA proof | [report at `2a87cc6`](https://github.com/WsprryPi/WsprryPi/blob/2a87cc6fa9f119a2b08da8eb80676e8812449ca8/docs/research/rp1-gpclk-phase6c-provider-dma-proof.md) | Packed fractional writes reached `DIV_FRAC`; CPU physical `0x1f0001817c` translated through DMAengine to `0xc04001817c`. Immediate termination was unsafe. | Preserve packing and translation requirements, not absolute addresses or kprobe methods. |
| Phase 6D bounded cancellation | [report at `2a87cc6`](https://github.com/WsprryPi/WsprryPi/blob/2a87cc6fa9f119a2b08da8eb80676e8812449ca8/docs/research/rp1-gpclk-phase6d-bounded-cancellation.md) | No successor plus one finite current descriptor, normal completion, readback, cleanup, and channel reuse was safe. | Initial cancellation invariant; revalidate through the DKMS module. |
| Phase 6E production backend | [report at `d4db49e`](https://github.com/WsprryPi/WsprryPi/blob/d4db49e94a1ceb1af5d774c1142ffb099f93ec8d/docs/research/rp1-gpclk-phase6e-production-backend.md) | Userspace modeled running, draining, terminal completion/failure, and delayed release. | Application evidence; informs module observability only. |
| Phase 6F provider UAPI | [report at `6c5f4e6`](https://github.com/WsprryPi/WsprryPi/blob/6c5f4e6685d89607b4eb54d5afc0a301ac32d988/docs/research/rp1-gpclk-phase6f-provider-uapi.md) | Stock `clk-rp1` at Raspberry Pi Linux `89586905b8603e545cce9089a81f5f35d65bc998` exposed no provider-private divider lease. | Explains weaker DKMS ownership. The proposed in-tree lease is superseded as a distribution path. |
| Phase 6H clock-disabled runtime | [report at `92e04cb`](https://github.com/WsprryPi/WsprryPi/blob/92e04cbfe04a22b8718e98d62342f0bc6d72e992/docs/research/rp1-gpclk-phase6h-clock-disabled-runtime.md) | Custom provider passed descriptors on `6.18.44-v8-16k+`; pre-translating the CPU physical address caused double translation. | Required negative test; does not qualify stock-module derivation or lifetime. |
| Phase 6Q lease generation | [report at `eea6bfb`](https://github.com/WsprryPi/WsprryPi/blob/eea6bfb6771db00e2f6833b5c8269d01d03dcab3/docs/research/rp1-gpclk-phase6q-lease-generation.md) | Generations increase within a lease and reset only after a new exclusive acquisition. | Preserve semantics; reimplement and retest independently. |
| Phase 7A keyed modes | [report at `5f8029d`](https://github.com/WsprryPi/WsprryPi/blob/5f8029d2d66b9ed0fe9164c2ef29db78cf86cd55/docs/research/rp1-gpclk-phase7a-clock-disabled-cw.md) | Finite events represented QRSS, FSKCW, and DFCW; WSPR retained the 162-symbol path. | Preserve bounded events and mode separation; do not infer module qualification. |
| Phase 8 drive selection | [report at `ce90102`](https://github.com/WsprryPi/WsprryPi/blob/ce90102f7d17b6f6118dbac06cfdfb72d3a85474/docs/research/rp1-gpclk-phase8-operator-drive-selection.md) | 2, 4, 8, and 12 mA were allowlisted; 2 mA was the safe default. | Revalidate pad behavior independently for GPIO4 and GPIO20. |
| Phase 9 visibility | [report at `43c98bc`](https://github.com/WsprryPi/WsprryPi/blob/43c98bc8ac1855b722285a0d043ce34d6bba61ab/docs/research/rp1-gpclk-phase9-operator-visibility-and-docs.md) | Operator controls and installation remained gated. | WsprryPi owns UI and product policy; the module supplies facts. |

## Historical source evidence

| Artifact | Immutable source | Disposition |
| --- | --- | --- |
| Userspace UAPI | [header at `fe8a03b`](https://github.com/WsprryPi/WSPR-Transmitter/blob/fe8a03b17a817175553968f91508fccd48c78bdf/src/rp1_gpclk_uapi.h) | Conceptual baseline; do not copy until ABI and explicit licensing are reviewed. |
| Kernel include shim | [file at `c86d5eb`](https://github.com/WsprryPi/WsprryPi/blob/c86d5ebf11d32c9c7f118ac9db300ca5beacd4ea/tools/rp1_gpclk_provider/kernel/include/linux/rp1_gpclk.h) | Superseded relative include; new project publishes one canonical UAPI. |
| Kernel validation contract | [file at `314c576`](https://github.com/WsprryPi/WsprryPi/blob/314c576c0883027b796f5f45444863c6d3ab9ba9/tools/rp1_gpclk_provider/kernel/include/rp1-gpclk-contract.h) | Reference behavior; licensing and stock assumptions require review. |
| Historical provider | [file at `314c576`](https://github.com/WsprryPi/WsprryPi/blob/314c576c0883027b796f5f45444863c6d3ab9ba9/tools/rp1_gpclk_provider/kernel/rp1_gpclk_provider.c) | GPL reference only; depends on custom lease APIs. |
| KUnit tests | [file at `314c576`](https://github.com/WsprryPi/WsprryPi/blob/314c576c0883027b796f5f45444863c6d3ab9ba9/tools/rp1_gpclk_provider/kernel/rp1_gpclk_provider_kunit.c) | Reusable test ideas; copied code remains GPL-2.0 unless affirmatively relicensed. |
| Historical overlay | [file at `45d2598`](https://github.com/WsprryPi/WsprryPi/blob/45d259810f68c4f78d11ed75667b3be225955c84/tools/rp1_gpclk_provider/kernel/rp1-gpclk-provider-overlay.dts) | Reference only; fixed resources and GPIO4-only binding are rejected final architecture. |
| Custom-kernel patches | [directory at `314c576`](https://github.com/WsprryPi/WsprryPi/tree/314c576c0883027b796f5f45444863c6d3ab9ba9/tools/rp1_gpclk_provider/kernel) | Historical evidence and prohibited production dependency. |

## Evidence not imported

Large raw logs remain in WsprryPi or at recorded target-only locations. Those
locations are not durable evidence for a future DKMS claim. Any claim that
needs those logs must first archive them with checksums in a repository or
release artifact.

## Qualification boundary

Nothing here qualifies a DKMS build, module load, stock-kernel ownership,
GPIO20, another kernel or Pi, installation, signing, update survival, timing,
RF output, or coexistence.
