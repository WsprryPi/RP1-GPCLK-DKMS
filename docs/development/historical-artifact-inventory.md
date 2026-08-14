<!-- SPDX-License-Identifier: MIT -->

# Historical RP1 artifact inventory

## Classes

- **Reusable:** may be reused under documented licensing after stock review.
- **Reference only:** useful evidence; do not copy directly.
- **Superseded:** replaced by the current project contract.
- **Prohibited production dependency:** must not ship in the module path.
- **Licensing review required:** resolve provenance/grant before adaptation.

## Inventory

| Artifact | Classification | Reason and next action |
| --- | --- | --- |
| Historical UAPI concepts | Reusable; licensing review for copying | Bounded ownership, generations, states, events, and reasons remain useful. Design the canonical header and add explicit SPDX. |
| Historical ioctl/layout ABI | Superseded | The project selected a clean DKMS UAPI in Decision 0001. Retain old values only as semantic and migration evidence. |
| Relative kernel include shim | Superseded | Cannot be standalone. Replace with one project-owned installed UAPI. |
| Portable core/tests | Reusable concepts; licensing review for copying | Parent is MIT but files are unmarked and model the custom provider. Prefer clean implementation and record any migrated fragment. |
| GPL provider/KUnit | Reference only; GPL if copied | Explicit GPL-2.0 and custom-lease coupling. Reuse invariants and test ideas. |
| Custom `clk-rp1` patches | Superseded; prohibited dependency | Maintained custom kernel is rejected. Retain only as ownership-gap evidence. |
| Kprobes/private symbols | Prohibited dependency | Internal symbols are not stable APIs. Use exported APIs or fail closed. |
| Fixed addresses | Prohibited dependency | Exact observations for one layout. Derive from DT/provider resources. |
| GPIO4 overlay | Reference; licensing review | Fixed resources and one route. Create reviewed route-specific stock overlays. |
| Phase 4/6C/6D/6H findings | Reference only | Convert failures and safety discoveries into Phase 2 tests. |
| Phase 6E/6F/6Q/7A semantics | Reusable concepts | Re-express after ABI decision. |
| Phase 7B/live RF evidence | Historical only | Does not qualify DKMS or GPIO20. Use later to design evidence format. |
| Phase 8 drive allowlist | Reusable concept | Validate pad behavior per route. |
| Phase 9 operator gating | WsprryPi-owned reference | Define module diagnostics sufficient for application policy. |
| Target-only raw logs | Reference until archived | Publish checksummed artifacts before relying on them for a new claim. |

## Production denylist

No custom kernel, patched `clk-rp1`, private lock/lease hook, kprobe, private
symbol, fixed absolute address, raw userspace MMIO, `/dev/mem`, WsprryPi
source-tree relative include, moving repository branch, or warning-as-ownership
substitute may become a production dependency.

## Intake result

The record supports a clean offline stock-module design but not a directly
reusable DKMS driver. No historical implementation source was copied.
