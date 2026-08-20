<!-- SPDX-License-Identifier: MIT -->

# Phase 5.35 mixed-transition integration adversarial assessment

## Outcome

**PASS.** No actionable finding remains within the Phase 5.35 successor scope.
The exact mixed transition/ordinary-file boundary that stopped Phase 5.34 is
now exercised by the real administration implementation against a complete
temporary release inventory.

## Assessment boundary

This assessment reviewed the implementation diff, the new complete-release
success and recovery regressions, and the full offline-check result. It did not
reuse an ordinary green test result as proof of target, GPIO, clock, timing, or
RF behavior.

## Assertions challenged

1. **Ordinary path while transitions remain:** `install_tool()` now removes a
   transition only by the current canonical installed path. The regression
   leaves the later executor transition pending while diagnostics is installed
   as an ordinary owned file.
2. **Declared predecessor enforcement:** both retained tools begin as real
   predecessor files whose exact digests are declared in the schema-version-2
   identity. Existing replacement validation remains unchanged.
3. **Declared successor enforcement:** the successful case verifies installed
   executor bytes and committed replacement ledger entries. A separate case
   supplies a wrong late executor digest and is rejected.
4. **Recovery across mixed operations:** after the deliberately late failure,
   recovery restores both predecessor byte streams and removes diagnostics,
   which was installed between the two declared transitions.
5. **No silent unused transition:** the final leftover-transition rejection is
   unchanged, so an identity path absent from the permanent install inventory
   still fails closed.
6. **No safety-boundary expansion:** qualification remains output-disabled and
   temporary-root-only in this step. No module, overlay, GPIO, GPCLK,
   transmission, RF, reboot, or target operation occurred.

## Evidence

- `python3 tests/check_phase5_3_installation.py` — PASS.
- `tests/run-offline-checks.sh` — PASS, including Phase 5.34 controls,
  installed-import and CLI rehearsal, compilation checks, lifecycle/resource/
  execution checks, documentation links, shellcheck, SPDX, and whitespace.
- `git diff --check` — PASS.

The macOS-only run continued to report the three existing Linux-target UAPI
client compile checks as `SKIP (Linux target only)`; the suite's applicable
Gate D probe and busy-injector compile checks passed.

## Residual boundary and next gate

This result fixes and validates the offline integration defect. It does not
alter or retroactively pass the failed Phase 5.34 target attempt. The next
step is a new clean candidate freeze and representative build containing this
commit, followed by a newly generated and independently validated control set.
Any later `wspr5` execution remains a separate sealed authorization.
