<!-- SPDX-License-Identifier: MIT -->

# Phase 2E adversarial assessment

Date: 2026-08-14
Scope: exact GPIO4 clock-disabled target execution and evidence
Result: pass for evidence 13 after 31 reinjected findings

## Method

A separate reviewer repeatedly attempted to falsify the execution prompt,
authorization boundary, source/artifact/target identity, route and provider
validation, resource translation, conflict behavior, descriptor and process
lifetime, partial cleanup, signing claims, simulated update failure, command
bounds, kernel-log attribution, evidence integrity, final target state, and
compatibility ceiling. Every objective finding was appended to the Phase 2E
prompt and the affected work plus complete safety suite were repeated.

## Final assessment

The final review independently verified evidence archive
`/private/tmp/rp1-gpclk-phase2e-evidence-13.tar.gz`, outer SHA-256
`f9f19c5be727ef8da1ea265f529258acffe9d875adca2cd0c8490c9b57aa1cc1`.
It extracted the archive at a different path and passed every relative inner
manifest entry. All 81 recorded source hashes mapped to and matched the
pre-final-report worktree. The raw production DT artifact was nonempty and its
machine validator independently proved the same provider, resource, route,
and DMA identities.

The reviewer confirmed the exact Pi 5/kernel/header/FDT/signing identities,
module and overlay hashes, bounded command/status matrix, holder PID/lease and
wait status 137, missing-header Make failure and status 2, explicit final
absence assertions, full dmesg baseline-prefix proofs, and exact nine-line
diagnostic classification. The complete offline suite and `git diff --check`
also passed.

## Reinjected findings

The durable numbered log in the Phase 2E execution prompt records all 31
findings and resolutions. The corrections include target compiler and header
integration, exact module inspection/signing and selected-artifact identity,
cleanup trapping and final absence, command bounds and ledger integrity,
UAPI/DT/provider/resource/DMA validation, diagnostic attribution, portable
evidence hashing, open-descriptor/process-death records, composite endpoint
exclusion and ARM64 release ordering, and correct kernel-update failure
provenance. Every affected target result was followed by the complete safety
matrix; evidence 13 is the final candidate.

## Disposition and limits

No unresolved objective Phase 2E finding remains. The only changes after the
evidence-13 source snapshot complete this evidence/review prose and clarify the
DMA request name; no tested source, overlay, runner, or behavior changed.

This assessment closes Phase 2 only for the exact recorded GPIO4
clock-disabled identity. It does not qualify GPIO20, active pinctrl/clock/DMA,
timing, transmission, RF, direct-MMIO coexistence, enforced signing, DKMS/APT
packaging lifecycle, another target identity, or WsprryPi product behavior.
