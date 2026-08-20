<!-- SPDX-License-Identifier: MIT -->

# Gate D Phase 5.16 tooling-identity adversarial assessment

Status: target execution blocked before installation

## Scope

This review attacks the Phase 5.16 correction that separates immutable source
identities from installed executable identities. It does not qualify target
lifecycle behavior and authorizes no target mutation.

## Assertions and results

1. **A historical single-digest plan cannot execute.** Passed. Schema version
   1 remains structurally inspectable only; live validation rejects it.
2. **Source and installed identities cannot be omitted or substituted.**
   Passed. Schema version 2 requires both 64-hex digests and rejects missing,
   malformed, or changed source identities.
3. **Installation semantics cannot be relabeled.** Passed. Python tools are
   required to be `copied`; C helper sources are required to be
   `target-built`. Copied identities must be equal.
4. **Installed bytes are independently enforced.** Passed. Target preflight
   compares regular-file installed bytes only with `installedSha256`; changed,
   missing, and symlinked paths fail closed.
5. **Historical evidence cannot silently become current.** Passed. The sealed
   Phase 5.14 attempt index intentionally differs from the advanced executor;
   the superseded instance skips live bundle validation and remains blocked.
6. **The correction expands no output authority.** Passed by static contract
   and the complete offline suite. No live-output, GPIO, clock, DMA, SDR, or RF
   permission changed.

## Sealed results

- Source commit: `ff92ffcbc588494dd89f303b73c31fe24554583a`.
- Two release builds were byte-identical; archive SHA-256:
  `7c7b7c4741717796b0a128c3f163f2921a25ea646d815b6ba59aae3fedd3ae8d`.
- The representative module build passed; module SHA-256:
  `a237bf6228ef7280efa5399377e7bc1f6e569f5fae9b6569ffe8b3c0234bf2c5`.
- Target-built helper SHA-256 values are
  `c01d97301fcbad4266e6fd41c040f561da0c106affc28cf353455e4a071331dd`
  and `1ee335da403784a775efc049f49eb598e3541c625418b65015b322e29b0a1742`.
- The schema-version-2 target plan validates, the generated attempt index
  binds exactly 38 documents, and the execution instance reports all ten
  required rows ready with five environmental rows explicitly deferred.
- `--require-ready` fails only with `fresh target-execution authorization is
  required`, as intended.

The adversarial review also caught an incorrectly expanded abbreviated commit
in the first target evidence labels. Those immutable directories are failed,
non-authoritative attempts. The representative build and helper seal were
repeated in distinct directories using the verified full commit above; only
the corrected evidence is referenced by the control set.

## Remaining gate

Fresh authorization was received and recorded. Immediate live preflight passed,
but the sealed bootstrap command failed closed before mutation with:

```text
ValueError: only the exact publishable release is installable
```

Phase 5.16 is intentionally `publishable=false`: it is a qualification
candidate, not a release. Its permanent executor must be installed before any
attempt document can run, but the same sealed administrator refuses to install
that candidate. This is an internal bootstrap contradiction, not a missing
operator authorization.

The disposable bootstrap directory was removed. Read-only verification found
no permanent executor, test DKMS version, module, endpoint, or overlay; all
four named services retained their expected pre-state. None of the 38 attempts
executed.

A successor must add a narrowly scoped, explicit qualification-install mode
that accepts only the exact sealed development identity, remains output
disabled, and cannot promote the artifact to a publishable release. That
correction requires new offline review, candidate freeze, representative build,
helper sealing, control-set construction, and authorization; Phase 5.16 must
not be patched or bypassed on the target.
