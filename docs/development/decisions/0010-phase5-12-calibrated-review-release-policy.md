<!-- SPDX-License-Identifier: MIT -->

# Decision 0010: Phase 5.12 calibrated-review release policy

Status: accepted
Date: 2026-08-15

## Context

Packaging and representative lifecycle work must be able to mature without
turning receiver-relative Phase 4 evidence into a calibrated qualification
claim. Waiting to package until calibrated testing is complete would also
prevent qualification from using the exact artifact operators would receive.

## Decision

Phase 5 may produce and, under separate Gate F authority, publish an
`Experimental` prerelease after its applicable packaging, lifecycle,
integrity, and review gates pass. Its manifest must identify the exact lesser
state, receiver-relative evidence scope, limitations, and non-final status.
Packaging success never creates or preserves `Qualified`.

Calibrated qualification uses the exact frozen packaged candidate. Results are
incorporated into a newly reviewed final compatibility manifest and release
decision. An exact identity becomes final `Qualified` only when all required
calibrated and other evidence classes pass for each claimed route and mode.

Any calibrated-review change to module behavior or source, overlays, UAPI,
timing, package contents, signing, compatibility policy, lifecycle tooling, or
generated artifact bytes creates a new candidate identity and invalidates the
affected Phase 5 lifecycle and release evidence. Those affected checks must be
repeated before the revised identity can be released.

## Consequences

An Experimental prerelease can support packaging development and calibrated
testing, but it is not a final Qualified release and cannot be relabeled in
place. The reviewed final manifest may retain a lesser state when calibrated
evidence is incomplete or fails. Publication, target administration, and
calibrated output remain separately authorized gates.
