<!-- SPDX-License-Identifier: MIT -->

# Phase 5.37 complete retained-tool transition successor prompt

## Objective

Correct the exact Phase 5.36 pre-root failure by making the qualification
transition identity cover the complete retained permanent-tool inventory and
by rejecting an incomplete transition graph before any DKMS or filesystem
installation work begins.

## Verified context

- Phase 5.36 passed archive, envelope, recovered-ledger, and read-only pre-root
  validation, then failed closed at the existing canonical
  `rp1-gpclk-diagnostics` path.
- The sealed identity and envelope agreed on 18 paths, but the installed
  permanent inventory contained 22 paths and also retained `gate-d-attempts`,
  `rp1-gpclk-diagnostics`, `lifecycle-policy`, and `gate-d-residue`.
- Journal-authorized recovery completed. No module, endpoint, overlay, GPIO
  output, clock, DMA, Si5351, SDR, transmission, or RF state remains active.

## Authorized scope

1. Define one canonical administrator inventory for every permanent file that
   may be retained across a qualification successor install.
2. Before creating the administrator transaction or running DKMS, require the
   transition graph to match every existing retained destination exactly.
3. Preserve normal first-install behavior for absent destinations and preserve
   exact predecessor, successor, mode, canonical-path, duplicate, symlink,
   leftover-transition, commit, and recovery validation.
4. Add complete-inventory success and boundary-failure recovery tests covering
   all retained tools, including diagnostics, lifecycle policy, and residue.
5. Add explicit omitted, extra, duplicate, tampered predecessor, tampered
   successor, and non-permanent-path rejection assertions.
6. Run focused and complete offline validation and perform a separate
   adversarial assessment. Correct every actionable finding and repeat the
   affected checks until clean.
7. Commit and push only attributable clean changes.

## Constraints and non-goals

- Do not retry or alter the sealed Phase 5.36 candidate or control set.
- Do not connect to or mutate `wspr5` in this successor implementation step.
- Do not install, load, bind, unbind, or remove a real module or overlay.
- Do not operate GPIO, GPCLK, DMA, the separate I2C Si5351 path, SDR,
  transmitter, antenna, or RF equipment.
- Do not change the release version, freeze a candidate, generate a target
  control set, or claim target qualification in this step.
- Do not weaken fail-closed handling merely to tolerate an existing file.

## Required evidence

- A complete temporary-root successor install replaces every retained
  permanent destination exactly once and commits only after all identities are
  verified.
- Omitting any one retained destination fails before transaction creation and
  before the fake DKMS runner is invoked.
- Failure at each replacement boundary restores every earlier predecessor and
  removes all successor-owned files.
- Malformed, duplicate, extra, symlinked, and digest-tampered identities remain
  rejected.
- Focused installation checks, complete offline checks, SPDX, documentation
  links, and whitespace checks pass.

## Exit criteria

Exit only when implementation, complete-inventory tests, and independent
adversarial assessment agree with no actionable finding. The next separately
gated step is a Phase 5.37 freeze and representative build, followed by a new
control set that binds the recovered Phase 5.36 ledger and preserved Phase
5.34 archive. Target execution remains separately sealed and authorized.
