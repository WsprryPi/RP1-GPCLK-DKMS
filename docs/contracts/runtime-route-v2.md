<!-- SPDX-License-Identifier: MIT -->

# Experimental runtime route protocol v2

The engine is explicitly `ModelEngine`/`ModelAdapter`; its atomic effects are
synthetic and must not be implemented by inventing Linux observations.
`runtime_inventory.py` is a separate read-only collector. This model has no
result-preserving write adapter. Real runtime administration is defined by the
separate [runtime controller](runtime-controller-v1.md).

This is an **offline implementation with target execution blocked**, not a
deployable rebootless route manager. It implements closed request validation,
dual-route artifact identity validation, an append-only transaction engine,
same-boot reconciliation, and explicit resume/rollback against an injected
offline adapter. It does not implement a Linux hardware adapter or claim that
the required atomic hardware operations already exist.

Existing [v1 package operations](route-manager-v1.md) and query-only
development integration are unchanged. Neither their socket nor their
deployment command routes requests to v2. The module, canonical UAPI, and
release identities are unchanged. No kernel lifetime safety is inferred from
this userspace engine.

## Public boundary

`python3 scripts/rp1-gpclk-runtime-route.py` accepts one bounded JSON object on
stdin and no arguments. It always exits 2 with one JSON response. Valid v2
requests return `status: blocked`, `mutationAvailable: false`, and the fixed
list of implementation blockers. Invalid, oversized, duplicate-key, or
nonfinite JSON requests return `status: rejected`. It does not inspect the
host, open the endpoint, create a journal, select an adapter, enroll a binding,
or execute a command. There is no environment variable, execute flag, or input
evidence that enables target mutation. The entry point is not installed as a
runtime command and is not suitable as a replacement systemd ExecStart.

The closed [request/response schema](../../schema/rp1-gpclk-runtime-route-v2.schema.json)
defines these operations:

| Operation | Additional fields | Current public result |
| --- | --- | --- |
| `query` | None | Blocked capability report, not a host-state query |
| `preflight` | `route` | Blocked; no readiness assertion |
| `switch` | `route`, `execute: true`, `requestId`, `actor` | Blocked; no effects |
| `recover` | `transactionId`, `strategy`, `execute: true`, `requestId`, `actor` | Blocked; no effects |

Routes are exactly `gpio4` and `gpio20`. Recovery strategy is `resume` or
`rollback`. Request IDs are bounded strings, unique across switch and recovery
requests; reusing an ID with changed content fails closed. `actor` records
attribution, not authentication. A future privileged transport must derive or
verify caller authority independently. No paths, commands, services, overlay
indices, UAPI payloads, or authorization digests are accepted.

## Identity and observations

The [v2 identity schema](../../schema/rp1-gpclk-runtime-binding-v2.schema.json)
binds manager and module commits, executable and module artifact hashes,
module build hash, UAPI hash, kernel/configuration and firmware identities,
and independent GPIO4/GPIO20 overlay hashes and compatibility IDs.
`binding()` validates closed structure, route association, and distinct
overlay hashes. These checks validate syntax, **not artifact authenticity**.
The unavailable adapter must authenticate enrolled records and actual bytes;
neither a matching version string nor caller-provided hashes suffice.

The engine accepts an internal `Observation` only from its adapter, never from
the public protocol. It includes:

- Boot ID, binding digest, and a compare-and-effect revision. That revision is
  not the existing UAPI execution generation.
- Effective boot selection, runtime origin/route, module route, independently
  observed module/overlay identities, overlay ownership, and foreign-stack
  identity. Firmware origin requires migration. Unknown, foreign, non-topmost,
  duplicate, or inconsistent route states reject execution.
- Admission state and states of exactly `wsprrypi.service` and
  `soapyremote-server.service` in that order. Unknown/transitional service state
  rejects execution.
- Explicit owner, lease, operation authorization, immutable gate, pending-work,
  cleanup-fault, GPIO-safe, clock-quiescent, DMA-quiescent and stable observations.
  There are no default safe values. Unknown observations reject execution.
- Adoption bound to the current boot, binding, route, overlay owner, and
  transaction identity. A loaded initial route requires matching adoption;
  a safely route-neutral initial state does not.

Adoption digests detect disagreement; they are not signatures. These internal
records do not replace or overwrite v1 current-boot adoption records.

## Engine and storage

`scripts/runtime_route.py` contains `ModelEngine` and has no subprocess, shell,
network, module, or overlay executor. `ModelAdapter.model_effect` assumes atomic
comparison of the complete observation and a synthetic successor. It requires
an explicit `model_only` marker and is only a reference experiment. A real
executor must use actual operation-specific kernel guarantees, not emulate this interface with read-then-execute shell commands.

The ordinary modeled switch is:

1. Persist intent and establish persistent administrative exclusion while
   quiescing the fixed services.
2. Unload the old module and attest teardown while its overlay still exists.
3. Remove the owned old runtime overlay and attest zero route endpoints.
4. Apply the destination overlay without implicit module autoload.
5. Load the exact destination-compatible module with output inhibited and
   attest binding and cleanup state.
6. Publish same-boot adoption for the verified destination.
7. Restore only the captured fixed-service states **with administrative
   admission still closed**.

Same-route requests inhibit, adopt, and restore services without touching the
module or overlay. Route-neutral startup skips unload/removal. Successful
completion does not release admission or authorize a later live operation.
The engine has no release-admission operation. Application integration for
that separately authorized future action remains outside this implementation.

The ledger is an append-only JSONL hash chain in an existing private 0700
directory. Its file must be a regular, single-link, owner-only 0600 file.
Directory traversal rejects symlinks. An exclusive nonblocking flock covers
reading, replay validation, intent, effect, readback, and completion. Records
are bounded to 16 KiB and the ledger to 4 MiB. File and creation-directory
fsync protect durability; no truncation or automatic pruning is provided.
Exhaustion blocks progress and needs an explicitly designed archival policy
before any production deployment. Hashes detect corruption, not malicious
rewriting by the file owner. The lock coordinates only cooperating engine
instances; it is not a hardware or root-administrator exclusion mechanism.

Every effect has a durable intent followed by an independently checked
observation and a durable result. A write/effect failure retains evidence and
leaves a pending transaction. No subsequent switch may run while it is pending.
Ledger reload verifies hashes, sequence, attribution, plan, and legal state
transitions. Partial final writes or semantic corruption block all operation;
no journal is renamed, deleted, rewritten, or presumed successful.

## Recovery

Recovery first checks identity, boot, foreign state, and all safety observations.
For an interrupted intent it accepts only the exact preceding state or its
expected attested successor. The former allows a guarded retry; the latter
records the effect without repeating it. Any other state requires external
recovery and causes no further effects. A reboot invalidates the transaction's
same-boot evidence and blocks automatic recovery.

`resume` continues the recorded plan. `rollback` plans a bounded return to the
original route (or route-neutral state), under the same exclusion and identity
rules. It creates new adoption, retains original evidence, and never restores
an obsolete overlay instance token. A failed rollback remains pending. An
operator may issue a new attributable recovery request to change strategy;
reusing an existing request ID with different content is rejected.

Completed switch and recovery replays return their recorded result only while
the complete current observation still matches. Historical completion is not
current readiness. No automatic reboot or output command exists. Once acquired,
the adapter must retain administrative exclusion through process death and
partial restoration; cleanup cannot depend on Python exception handling.

## Missing target mechanisms and next gated work

The following limitations apply to this offline model, not the separate
runtime controller. Do not add UAPI merely to satisfy a synthetic atomic
adapter. The configfs removal interface discards overlay-removal errors;
it cannot provide the model's required result and retained recovery handle.

Code review of `rp1_gpclk_open()` and the canonical ABI-v4 header found no
persistent administrative admission API spanning endpoint closure, unload,
overlay replacement, and reload. `GET_SNAPSHOT_V3` exposes useful observations
including operation-scoped live state, but grants no exclusion. Holding a file
open to guard the endpoint would itself obstruct the proposed unload sequence.

Three substantive requirements therefore remain before a hardware adapter can
be implemented and enabled:

1. Implement and review persistent administrative admission, including restart,
   autoload, service, endpoint and application interactions. It must survive
   manager process death and module replacement, and have separately authorized
   release semantics. Do not claim an ordinary userspace lock supplies this.
2. Establish an attributable runtime-overlay ownership and comparison mechanism
   on the exact stock target kernel/tool version, covering dependent overlays
   and competing privileged administration without touching foreign overlays.
3. Establish supported post-unload teardown/cleanup attestation and audit
   kernel-created versus module-created platform-device and OF-node lifetimes
   for that exact kernel. Existing passive snapshots are pre-unload evidence;
   successful unload alone does not prove overlay-memory safety afterward.

These are missing implementation and validation mechanisms, not optional
qualification labels that can be cleared with a configuration flag. Until
resolved, deployment/enrollment and a real adapter are deliberately absent.
The public capability report names these blockers and the absent adapter.

For firmware-selected routes, migration remains a separately authorized,
journaled boot-file change and reboot to neither route. The default future
boot policy is route-neutral; no automatic startup route activator is supplied.
Read-only target inventory must identify the exact kernel, firmware, boot
includes/conditionals, loaded/installed artifacts, providers, overlay stack,
and service ownership before selecting implementation details.

Only after those mechanisms and the adapter are reviewed may a separately
authorized target campaign install or administer anything. It must validate
both routes independently, repeated switching and safe failure recovery, with
output inhibited. Offline fixture success establishes no GPIO, electrical
silence, waveform, frequency, transmission, RF, product, or release qualification.
