<!-- SPDX-License-Identifier: MIT -->

# Phase 5.37 complete retained-tool transition adversarial assessment

Status: PASS; no actionable successor-scope finding remains

## Scope reviewed

The review challenged the administrator preflight, the canonical retained-file
inventory, the complete temporary-root install, every replacement-boundary
recovery case, and the malformed-identity cases. It did not treat offline
success as target, lifecycle, GPIO, clock, timing, transmission, or RF
evidence.

## Findings and disposition

The first review pass found that the Phase 5.36 execution assessment and the
initial successor prompt counted three omitted paths. Direct set comparison
proved four omissions: `gate-d-attempts`, `gate-d-residue`,
`lifecycle-policy`, and `rp1-gpclk-diagnostics`. The implementation and tests
already used the correct 22-path canonical inventory; both documents were
corrected before acceptance.

No implementation blocker remains:

1. The administrator now computes the exact existing subset of its closed
   22-path permanent inventory before transaction creation.
2. A qualification transition graph must equal that subset. An omitted path
   or extra non-permanent path fails before a transaction file exists and
   before the external command runner is called.
3. Existing predecessor digest, real-file, non-symlink, successor digest,
   mode, duplicate, and leftover-transition checks remain enforced.
4. A complete temporary-root install replaces and commits all 22 retained
   files, including all four Phase 5.36 omissions.
5. A wrong successor digest injected separately at every one of the 22
   replacement boundaries fails closed. Recovery restores every retained
   predecessor byte-for-byte and reports `liveOutput=false`.
6. First-install behavior remains available through the existing schema-1
   qualification identity and normal publishable installation paths; the new
   exact-set rule applies only to schema-2 retained-tool transitions.

## Evidence

- `python3 tests/check_phase5_3_installation.py` — PASS.
- `tests/run-offline-checks.sh` — PASS.
- Documentation links, shellcheck, SPDX, and whitespace — PASS in the complete
  suite.
- The three Linux-target-only UAPI client compile checks remained explicitly
  skipped on macOS; applicable Gate D C compilation checks passed.

No target connection, installation, module or overlay operation, GPIO, GPCLK,
DMA, Si5351, SDR, reboot, transmission, or RF action occurred. The next gate is
a new Phase 5.37 freeze and exact representative build. A new control set and
any target execution remain later, separately reviewed and authorized steps.
