<!-- SPDX-License-Identifier: MIT -->

# Decision 0009: Gate D blocker-resolution identities

## Decision

Frozen `0.0.0-phase5.2` remains the immutable predecessor. Changed
blocker-resolution source advances to `0.0.0-phase5.13` as the successor. The
pair is acceptable only after the successor has its own commit, deterministic
archive and sidecar hashes, and two clean-commit offline passes.

The open/busy injector is a separately sealed test tool. It may open the exact
endpoint or acquire a non-live lease, but it rejects `LIVE_ELIGIBLE`, requests
no submission capability, exposes a readiness event while holding the blocker,
has a maximum 900-second timeout, handles SIGINT/SIGTERM, and releases only its
own state. It is excluded from candidate and installed package bytes.

No representative-matrix requirement is revised in this slice. The following
remain distinct external evidence classes:

- an exact successor build on the named stock kernel and headers;
- a genuinely newer installed stock Pi 5 kernel;
- a real signature-enforcing stock system with enrolled administrator key;
- a real installed kernel with absent matching headers; and
- a genuine pre-existing foreign overlay/resource owner.

Fixtures and fake identities remain negative policy tests only. Unavailability
does not turn them into representative evidence.

## Consequences

The version-pair and removal-refusal tooling blockers can close offline after
sealing. The current-supported-kernel and four distinct-system classes cannot.
Therefore `executionReady` must remain false and complete Gate D target
authorization cannot yet be requested as executable authority.

## Gate C follow-up

The authorized 2026-08-15 `wspr5` successor build subsequently passed and is
recorded in `release/gate-c-representative-build-manifest-v1.json`. It closes
the route-neutral build prerequisite at `Compatible-unqualified` and
`liveEligible: false`; it does not create a route-specific compatibility entry
or satisfy any lifecycle row. The distinct external evidence classes above
remain unchanged.
