<!-- SPDX-License-Identifier: MIT -->

# Phase 5.5 permissions and enrollment execution prompt

## Authority and exit condition

Execute only the permissions and enrollment portion of Phase 5A through Phase
5C in `phase5-packaging-operator-enablement-execution-prompt.md`. Repository
changes and deterministic offline validation are authorized. Target access,
device creation, module load or binding, udev changes, boot changes, DKMS
mutation, GPIO, clock, DMA, transmission, RF, tagging, publication, and changes
to consuming repositories are not authorized.

Phase 5.5 closes when the root-owned `0600` device-node contract is frozen and
machine-checked; installed, available, enrolled, live eligible, and active are
independent fail-closed states; Experimental enrollment is explicit, durable,
administrator-attributable, release-and-route-specific, completely identity
bound, revocable, and never inherited; Qualified operation still requires an
explicit route and ordinary operator authorization; the complete offline suite
passes twice; and a separate adversarial assessment has no finding.

## Permissions contract

`/dev/rp1-gpclk` is owned by UID 0 and GID 0 with mode `0600`. A missing node
means inactive, not an installation failure. A node with another owner, group,
mode, type, or identity is unavailable and never repaired by a read-only
command. Do not install a udev rule, group grant, ACL, capability, setuid helper,
container escape, or proxy. Any later non-root access is a separate security
architecture decision owned with WsprryPi.

## State separation

- **installed**: the exact package files and DKMS entry exist. It says nothing
  about the current kernel or permission to output.
- **available**: the complete runtime and compatibility identity matches one
  manifest entry and all prerequisites pass without a cleanup latch.
- **enrolled**: a current administrator record authorizes Experimental risk for
  exactly one identity and route. It is false for Qualified identities because
  Experimental-risk acceptance is unnecessary, not implicitly granted.
- **live eligible**: availability plus either current Experimental enrollment,
  or Qualified state with deliberate route selection and normal operator
  authorization, permits output. It is not the module parameter or active state.
- **active**: one owner currently holds the device. This may be an
  output-disabled administrative owner; availability or enrollment never
  implies ownership, and ownership alone never permits output.

## Experimental enrollment record

Enrollment requires an explicit `enroll-experimental --execute` action by UID
0, the exact acknowledgement text frozen in the policy, and a complete identity
snapshot. The durable JSON record is root-owned `0600`, written atomically, and
records administrator UID/name, UTC time, policy version, compatibility entry,
module release and hash, UAPI ABI/hash, kernel release/config, base DT, firmware,
overlay source/DTBO, route, signing identity, and compatibility-manifest hash.

Every recorded identity field is equality checked. A module, UAPI, kernel,
kernel configuration, base DT, firmware, overlay, route, signer, manifest, or
compatibility-entry change makes enrollment stale. Missing and unknown fields
fail closed. Installation, rebuild, upgrade, route change, a previous custom
kernel, or a record for the other route never creates or transfers enrollment.
Revocation is a separate explicit root action: atomically replace the record
with a durable tombstone before any later removal. Repeated revocation is safe.

## Offline implementation and validation

Add a machine-readable policy and pure evaluator. The evaluator accepts only a
complete explicit snapshot and optional enrollment record; performs no system
discovery or mutation; returns the five independent states and reasons; rejects
impossible combinations; and never enables a backend. Add narrowly scoped
enroll and revoke writers with root, acknowledgement, real-file, owner, mode,
atomicity, and attribution checks. Installation must package but never create
the administrator enrollment record.

Test every identity invalidator, both routes, all compatibility states, missing
and unknown fields, cleanup latch, permission mismatch, stale/tampered records,
Qualified route/authorization requirements, active-owner consistency, custom-
kernel non-inheritance, explicit acknowledgement, root-only mutation, atomic
`0600` files, idempotent revocation, read-only evaluation, and absence of udev,
ACL, group, setuid, fallback, hardware, or RF commands. Run SPDX, whitespace,
documentation links, release checks, and the complete offline suite twice.

## Adversarial reinjection loop

Separately attempt to falsify permission restriction, state independence,
identity completeness, administrator attribution, durable atomicity,
invalidation, revocation, route isolation, Qualified authorization, active
single ownership, custom-kernel non-inheritance, and absence of implicit system
mutation. Reinject every objective finding into this prompt and implementation,
invalidate affected results, and repeat until none remains.
