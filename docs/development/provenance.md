<!-- SPDX-License-Identifier: MIT -->

# Historical source provenance and reuse policy

## Inspected repositories

| Repository | Inspection identity | License observation |
| --- | --- | --- |
| `WsprryPi/WsprryPi` | `d50dbf9447cdf72e49f8e94278516c6a08313ca6` | Root project declares MIT for version 2.x; individual kernel files may be GPL-2.0. |
| `WsprryPi/WSPR-Transmitter` | `747db7e5f8b857c432eb96b05e74944de6b58940` | Root `LICENSE.md` is MIT. |
| Raspberry Pi Linux | Historical pin `89586905b8603e545cce9089a81f5f35d65bc998` | Linux and per-file notices govern adapted kernel material. |

Inspection identities show what was reviewed, not qualification.

## Artifact provenance

| Artifact | Last content commit | Blob | Marking | Classification |
| --- | --- | --- | --- | --- |
| WSPR-Transmitter UAPI | `fe8a03b17a817175553968f91508fccd48c78bdf` | `ac3f9db187bbbd489c99362ed99efd32dd0b2b6d` | No SPDX; repository MIT | Reusable concepts; explicit notice required before copying. |
| Kernel include shim | `c86d5ebf11d32c9c7f118ac9db300ca5beacd4ea` | `47d8962b6dd75ad90defac41efe0ab363aeef2a0` | No SPDX | Superseded; do not copy. |
| Kernel contract header | `314c576c0883027b796f5f45444863c6d3ab9ba9` | `64b776c74e54eda46eb3e1bf06c0a45d7a22c063` | No SPDX; coupled to GPL provider | Licensing review before expression reuse. |
| Provider | `314c576c0883027b796f5f45444863c6d3ab9ba9` | `d52ce82154cc7137d27d5f2350ace6c8a524b9c2` | GPL-2.0 and `MODULE_LICENSE("GPL")` | GPL historical reference; custom APIs prohibit direct production reuse. |
| KUnit tests | `314c576c0883027b796f5f45444863c6d3ab9ba9` | `44963035e4b07fc50b1599f06a4cf8288d75352f` | GPL-2.0 | GPL unless affirmatively relicensed; reuse test ideas. |
| Overlay | `45d259810f68c4f78d11ed75667b3be225955c84` | `6807411537475a39f5f0cb45c32c6c80fadb1fc8` | No SPDX | Reference only and licensing review required. |
| Portable core source | `b7330b800723180cf2bafb77cfa45ba709b28129` | `8a9156fd9c81eda0703c843b7a166a13917de276` | No SPDX; parent MIT | Reusable concepts; explicit grant required before migration. |
| Portable core header | `b7330b800723180cf2bafb77cfa45ba709b28129` | `89cdd5352ce4248e14a4ee75d4d4de172cd7b28d` | No SPDX; parent MIT | Same condition as core source. |
| Portable core tests | `b7330b800723180cf2bafb77cfa45ba709b28129` | `81610e1d7077f7ac032c4950792502a014b95d64` | No SPDX; parent MIT | Reusable ideas; explicit marking required before migration. |

## Intake rules

- Repository-level MIT applies to original unmarked project work, but this
  review does not assume every kernel-adjacent line is independently original.
- Explicit GPL-2.0 files remain GPL-2.0 unless all copyright holders grant
  relicensing.
- Public availability or common authorship is not permission to remove notices.
- Linux-derived or other GPL-only code must not be relabeled MIT.
- New module code should use `GPL-2.0-only OR MIT`; new UAPI should use
  `(GPL-2.0-only WITH Linux-syscall-note) OR MIT`; independent tooling and
  documentation should use MIT.
- Every migrated fragment needs source commit/path, old marking, copyright
  basis, destination, and resulting SPDX expression recorded here.

## Safe conceptual reuse

Bounded validation, single ownership, lease-scoped generations, finite work,
no-successor cancellation, terminal states, divider packing, translation
failures, and test scenarios may guide a clean implementation.

No historical implementation source was copied during this intake.

## Phase 2A clean implementation

The Phase 2A UAPI, schema, Kbuild/source skeleton, test fixtures, and checks
were authored cleanly in this repository on 2026-08-14 from the project
contracts and documented semantic requirements. No historical provider,
portable-core, overlay, KUnit, or UAPI implementation text was copied or
adapted. The historical numeric ioctl namespace and byte layouts were not
reused.

The canonical UAPI is dual-licensed with the Linux syscall exception as
required by `LICENSE.md`. Kernel-facing skeleton files are
`GPL-2.0-only OR MIT`; independent schema, build metadata, tests, fixtures, and
documentation are MIT. Future implementation work that imports or adapts a
fragment must add a source identity and disposition to this record before the
fragment is accepted.

## Phase 2B clean implementation

The portable lifecycle core, host-only fault injection, tests, decision, and
review were authored cleanly in this repository from the Phase 2A contracts.
No historical portable-core or provider implementation text was copied or
adapted. Historical work informed only the already-recorded concepts of
bounded ownership, generations, cancellation, and terminal outcomes.
