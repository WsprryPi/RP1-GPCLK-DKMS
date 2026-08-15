<!-- SPDX-License-Identifier: MIT -->

# Gate D target runbook

## Current hard stop

The frozen candidate and five row inputs are ready, but the complete execution
instance is not. This command must fail before any target command is prepared:

```sh
gate-d-instance release/gate-d-execution-instance-v1.json --require-ready
```

Do not execute a ready subset. `gate-d-lifecycle` requires the complete frozen
15-row instance so a convenient row cannot bypass missing representative
kernel, signing, conflict, predecessor, or busy-state evidence.

## Preconditions for a future authorized run

Resolve every blocker in `docs/evidence/gate-d-candidate-preflight.md`, update
the concrete instance with exact identities, pass full JSON Schema and semantic
validation, and seal its digest. Confirm the Si5351 leads are disconnected from
GPIO4 and GPIO20, no antenna is connected, SDRplay is unused, rescue SD and
physical power access remain available, and the candidate artifact hashes match
the instance.

Before each row, record the exact installation transaction's owned files,
symlinks, and empty directories with their SHA-256 identities. Generate a new
operation document with one unique operation ID and an attempt directory below
that row's evidence directory. Validate and print its fixed command plan
offline:

```sh
gate-d-lifecycle validate OPERATION.json
gate-d-lifecycle plan OPERATION.json
```

Reject any plan containing `live_output=1`, an unallowlisted route, boot or
service mutation, forced removal, `/dev/mem`, raw MMIO, GPIO output, clock
enablement, DMA submission, transmitter, SDR, or RF activity.

## Per-attempt dispatch

Only after a separately recorded target-execution release may the root operator
dispatch the reviewed operation:

```sh
sudo gate-d-lifecycle execute OPERATION.json \
  --instance SEALED-EXECUTION-INSTANCE.json \
  --journal NEW-IMMUTABLE-ATTEMPT/transaction.json \
  --execute
```

An interrupted attempt remains immutable. Recovery reads it and writes a new
journal:

```sh
sudo gate-d-lifecycle execute RECOVERY.json \
  --instance SEALED-EXECUTION-INSTANCE.json \
  --journal NEW-RECOVERY-ATTEMPT/transaction.json \
  --recover-from FAILED-ATTEMPT/transaction.json \
  --execute
```

Never reuse an evidence directory or journal. Preserve every failed attempt.
Every operation shares one total row deadline, records UTC and monotonic timing,
and must end inactive. An ordinary upgrade/downgrade failure must restore the
exact retained predecessor or become recovery-required.

## Row evidence and cleanup

For both GPIO4 and GPIO20 where listed, retain the operation document, sealed
instance, candidate hashes, command plan, transaction journal, bounded output,
scoped kernel-log delta, baseline comparison, DKMS status, module/endpoint and
platform-binding absence, exact owned-path audit, and final state. Refusal rows
must name an actual retained installation and prove the exact open or owner
blocker without dispatching removal.

Planned reboot rows use only the two named installed stock kernels. Announce the
reboot, verify rescue readiness first, wait at most 600 seconds for SSH, begin
the declared automatic recovery by 900 seconds, and stop for operator help at
1,800 seconds. Do not improvise boot edits or a third kernel.

No row passes from a plan, mock output, a later successful attempt that erases a
failure, or evidence from another kernel, signing policy, route, artifact, or
host. After every row remove only exact attempt-owned state and restore its
declared inactive baseline.
