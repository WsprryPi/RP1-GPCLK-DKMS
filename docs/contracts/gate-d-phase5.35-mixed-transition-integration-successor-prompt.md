<!-- SPDX-License-Identifier: MIT -->

# Phase 5.35 mixed-transition integration successor prompt

## Objective

Correct the exact offline integration defect exposed by the authorized Phase
5.34 output-disabled execution: a qualification install containing both
declared permanent-tool transitions and ordinary package files must resolve a
transition only when the current canonical installed path is present in the
transition map.

## Verified context

- Phase 5.34 failed closed while installing the ordinary
  `/usr/libexec/rp1-gpclk-dkms/rp1-gpclk-diagnostics` path because unrelated
  transitions remained in the map.
- The sealed recovery path completed without retry and restored the retained
  predecessor tools.
- The defect is in the local `install_tool()` transition lookup, not in DKMS,
  kernel headers, route selection, GPIO state, or RF behavior.

## Authorized scope

1. Change the transition lookup to consume only an exact canonical installed
   path match.
2. Add a complete-release offline regression that transitions retained admin
   and executor tools while installing ordinary files between them.
3. Add a complete-release failure/recovery regression in which a late invalid
   successor identity restores every predecessor and removes intervening owned
   files.
4. Run the focused installation check and the complete offline suite.
5. Perform and record a separate adversarial assessment.
6. Commit and push only attributable changes if every required check passes.

## Constraints and non-goals

- Do not connect to or change `wspr5`.
- Do not install, load, bind, unbind, or remove a real module or overlay.
- Do not touch GPIO, enable GPCLK, transmit, or produce RF output.
- Do not create another candidate freeze, build bundle, control set, execution
  authorization, or target attempt in this step.
- Do not relax transition identity, canonical-path, predecessor, successor,
  mode, recovery, or leftover-transition checks.
- Do not change the release version.

## Required evidence and adversarial assertions

- The formerly failing mixed inventory completes under a temporary root.
- Ordinary files are installed normally while later transitions remain.
- Every declared transition is consumed exactly once and commits only after
  predecessor and successor verification.
- A wrong late successor digest fails closed; recovery restores both retained
  predecessors and removes an ordinary file installed between them.
- Existing malformed, duplicate, uninstalled, symlink, tamper, and ordinary
  installation checks remain green.
- The complete offline suite is green and no target/system/hardware action is
  performed.

## Exit criteria

Exit only when the implementation, exact mixed integration regressions, full
offline checks, and independent adversarial assessment agree. The next gated
step after this successor is a new candidate freeze and representative build;
target execution remains separately authorized and sealed.
