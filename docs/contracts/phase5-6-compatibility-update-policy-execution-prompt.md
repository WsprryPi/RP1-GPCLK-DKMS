<!-- SPDX-License-Identifier: MIT -->

# Phase 5.6 compatibility and update policy execution prompt

## Authority and exit condition

Execute only the compatibility-manifest and update-policy portion of Phase 5A
through Phase 5C in `phase5-packaging-operator-enablement-execution-prompt.md`.
Repository changes, deterministic release generation, and offline tests are
authorized. Target access, DKMS registration or installation, signing, module
load or binding, overlay application, boot changes, GPIO, clock, DMA,
transmission, RF, tagging, release publication, and consuming-repository
changes are not authorized.

Phase 5.6 closes when a populated, release-generated manifest replaces the
empty development example; every entry binds the complete hardware, build,
firmware/DT, module/signature, UAPI, overlay/route/drive/mode, evidence,
decision, and live-eligibility identity; missing or malformed input fails
closed; update events have machine-checked outcomes; automatic DKMS rebuilds
cannot preserve `Qualified`; the complete offline suite passes twice; and a
separate adversarial assessment has no finding.

## Governing inputs and truthful evidence boundary

Follow `AGENTS.md`, the module contract, the Phase 5 packaging prompt, frozen
UAPI v1, release layout, overlay contract, permissions/enrollment policy, and
the Phase 4 closeout. The release is `0.0.0-phase5.2`; Phase 4 live evidence is
for `0.0.0-phase4d-combined`. Record both exact route identities, but classify
them `Unavailable` for this release because their module version and artifact
identity differ. Receiver-relative Phase 4 evidence does not establish
calibrated absolute frequency, power, spectrum, or a `Qualified` release row.
Never invent an unrecorded firmware, header, configuration, module, signature,
overlay, or evidence identity.

## Manifest contract

Maintain one version-controlled compatibility decision source. Release
generation copies it and binds the generated release module identity (release,
source commit/archive, UAPI ABI/header hash) without weakening any entry.
Require unique entry IDs and complete entries containing:

- Pi model and revision, architecture, exact kernel release and header package,
  relevant configuration hash and named settings;
- firmware and base-DT identity;
- module version, unsigned and installed module hashes, vermagic, signature
  kind, signer, key fingerprint, and signature policy;
- UAPI ABI and canonical-header hash;
- overlay source/DTBO hash, exactly one route, and supported drive in mA;
- nonempty supported modes and exact evidence IDs/hashes/classes;
- compatibility state, immutable live eligibility, and a nonempty decision
  reason.

Unknown values are not wildcards. Missing/malformed manifests and entries are
`Unavailable`. `Compatible-unqualified`, `Unavailable`, and `Rejected` are
never live eligible. `Experimental` requires current exact-identity enrollment;
stale enrollment revokes eligibility. `Qualified` requires exact complete
evidence and must never be inferred from compilation.

## Update transition contract

Implement a pure, offline, deny-by-default evaluator. It accepts a validated
prior decision and one explicit event; it performs no discovery or mutation.

| Event | Required result |
| --- | --- |
| Same qualified identity rebuilt identically | Preserve only the state/live decision explicitly permitted by a matching manifest rule; otherwise demote |
| New kernel builds successfully | At most `Compatible-unqualified`, non-live, until an explicit rule and required evidence cover it |
| DKMS build fails | `Unavailable`, non-live; preserve the prior bootable installation as rollback state |
| Signing fails | `Unavailable`, non-live; unsigned loading prohibited |
| Module loads but identity differs | `Unavailable`, non-live; reject use of the loaded bytes |
| Overlay identity differs | `Unavailable`, non-live; reject binding and live eligibility |
| Cleanup failure is latched | `Rejected`, non-live until explicit reviewed recovery succeeds |
| Manifest missing or malformed | `Unavailable`, non-live |
| Experimental enrollment becomes stale | Preserve the compatibility classification but revoke live eligibility |

No event selects another physical backend. A successful automatic DKMS rebuild
has no path that preserves or creates `Qualified` merely because it compiled.
The evaluator reports state, live eligibility, reason, prior-installation
disposition, whether loading/binding is permitted, and whether explicit
recovery is required.

## Offline implementation and validation

Update the JSON Schema, populated decision source, release generator,
independent release validator, documentation, and deterministic tests. Test
every required field, unique identities, both routes, all modes, route/evidence
agreement, impossible state/live combinations, exact rebuild with and without
an explicit preservation rule, every event above, missing/unknown fields,
malformed manifests, stale enrollment, cleanup recovery, no fallback, and
preservation of the prior bootable kernel after build failure. Inspect commands
before running them. Run SPDX, whitespace, links, release checks, and the full
offline suite twice.

## Adversarial reinjection loop

Separately try to falsify identity completeness, evidence linkage, route/mode
isolation, schema strictness, state/live combinations, build-success ceiling,
automatic-rebuild demotion, signature/load/overlay rejection, prior-bootable
retention, cleanup latching and explicit recovery, malformed-manifest handling,
stale enrollment revocation, read-only purity, and absence of backend fallback
or system/hardware actions. Record each objective finding below, correct it,
invalidate and rerun affected checks, then repeat until none remains.

### Reinjected findings

1. The first manifest draft attributed mode coverage to Phase 3B clock-disabled
   evidence even though that phase did not execute modes. Remove that evidence
   link rather than overstate it; the exact Phase 4 route archives retain the
   actual mode and cleanup linkage.
2. The GPIO4 archive used a different disposable signing-key fingerprint than
   GPIO20. Inspect its preserved `modinfo.txt` and record the route-specific
   fingerprint rather than copying GPIO20's identity.
3. The first evaluator accepted impossible prior state/live combinations and
   could report loading permitted when preserving an `Unavailable` identity.
   Validate prior invariants and keep unavailable/rejected identities unloadable.

All three findings were reinjected into implementation and regression tests.

## Completion report

Report files and behavior changed, exact tests and results, manifest decisions
and their evidence boundary, skipped validation, licensing/documentation/UAPI
impact, all system/hardware/RF and publication actions not performed, final Git
state, and the next separately authorized gate. Do not call the whole Phase 5
complete.
