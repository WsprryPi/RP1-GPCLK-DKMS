<!-- SPDX-License-Identifier: MIT -->

# Decision 0008: Phase 5.6 compatibility and update policy

Status: accepted
Date: 2026-08-15

## Context

The release generator emitted an empty deny-by-default manifest. That was safe
for development but could not explain exact historical identities or determine
kernel-update, signing, overlay, cleanup, and enrollment transitions. A DKMS
automatic rebuild must not inherit qualification merely because it compiles.

## Decision

`release/compatibility-decisions-v1.json` is the reviewed source for populated
release entries. Each entry is exact across hardware, kernel/headers/config,
firmware/base DT, module/vermagic/signature, UAPI, overlay, route, drive, modes,
and evidence. Unknown values are recorded explicitly and make the decision
unavailable; they are never wildcards.

The two current entries preserve the exact Phase 4 GPIO4 and GPIO20 evidence
identities but are `Unavailable` and non-live because that evidence used module
`0.0.0-phase4d-combined`, historical DTBO bytes, and did not record firmware or
calibrated absolute RF evidence. Release `0.0.0-phase5.2` does not inherit the
earlier candidate's compatibility state.

`scripts/compatibility_policy.py` is a pure fail-closed update evaluator.
Successful new-kernel compilation reaches at most `Compatible-unqualified`.
Build or signing failure retains the prior bootable installation but marks the
successor unavailable. Module or overlay mismatch prohibits use or binding.
Cleanup failure latches `Rejected` until explicit recovery succeeds, after
which full identity revalidation is still required. Missing/malformed
manifests are unavailable, and stale Experimental enrollment revokes live
eligibility. No transition permits another physical backend.

An identical rebuild preserves a prior state only when both byte-relevant
identity equality and an explicit manifest preservation rule are supplied.
Compilation alone is never such a rule.

## Consequences

The compatibility schema now requires at least one complete entry and the
release inventory packages the decision source and evaluator. This is a
pre-release schema tightening; UAPI ABI 1 is unchanged. A later positive entry
requires exact packaged build/signature/overlay identities and evidence under
the separately authorized target and qualification gates.

## Rejected alternatives

- leaving the release manifest empty;
- treating unknown firmware or module identity as a wildcard;
- preserving `Qualified` after an automatic DKMS build;
- loading unsigned bytes after signing failure;
- binding a different overlay; and
- clearing a cleanup latch through reinstall, reboot, or an ordinary run.
