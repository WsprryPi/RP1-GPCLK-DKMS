<!-- SPDX-License-Identifier: MIT -->

# ABI v3 passive state snapshot

`RP1_GPCLK_IOC_GET_SNAPSHOT_V3` (`0x2a`, 392 bytes) is the sole ABI-v3
addition. ABI-v1 and ABI-v2 layouts and command numbers remain byte-for-byte
available. Callers initialize only the v3 header (`size`, `version`, zero
flags) and zero every reserved field. Unknown versions, flags, enum values,
capability bits, or nonzero reserved fields fail closed.

The ioctl is non-owning. It does not acquire the execution owner, allocate or
return a lease token, advance a generation, submit work, change output state,
or clear retained terminal state. Opening a descriptor allocates only the
ordinary per-file bookkeeping identity; closing a descriptor that never
acquired a lease cannot stop or otherwise mutate another operation.

The module takes its device mutex and returns one coherent observation of the
route, compatibility state/reason and identity, live-output and
live-eligibility booleans, owner/lease presence, generation, operation state,
terminal reason, current event, drain state, cleanup fault, and resource
quiescence. Owner and lease values are presence-only; no owner ID or lease
token crosses this interface.

`current_event`, `elapsed_ns`, and `remaining_ns` are meaningful only when the
corresponding `RP1_GPCLK_SNAPSHOT_F_*_VALID` bit is set. Elapsed time is bounded
to the known total duration. Remaining time is zero for a terminal operation.
A generation-zero idle module does not claim timing or event validity.

GPIO safety, clock quiescence, DMA quiescence, and other observations use the
tri-state values `unknown`, `false`, and `true`. A resource is false when its
module-owned active flag is set. It is true only after execution completion,
worker exit, plan release, and absence of the active flag; otherwise it is
unknown. The module does not inspect or make claims about unrelated direct-MMIO
software. `stable=true` additionally requires idle or terminal operation state,
no cleanup fault, and all three resource observations true.

After an operation finishes and its owner releases the lease, the core retains
the last generation, terminal state/reason, and completed-unit count for
passive inspection. Owner and lease presence become false. The next successful
acquire clears the retained operation record before accepting new work. A
cleanup fault remains latched according to the existing recovery contract.

Concurrent transitions are serialized at the device snapshot boundary. A
snapshot describes one instant and is not a subscription or proof of future
state. Consumers must compare generation and operation state across samples if
they need transition detection. `unknown`, a generation change, a cleanup
fault, or `stable` other than true is a fail-closed result for qualification.

This source change creates a new exact artifact identity. The GPIO4 and GPIO20
candidate IDs therefore advance independently to r3 and remain live-ineligible
until the exact r3 artifact for each route receives separate target evidence.
No r2 target evidence transfers to r3 or between routes.
