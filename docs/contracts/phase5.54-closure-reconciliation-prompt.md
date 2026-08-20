<!-- SPDX-License-Identifier: MIT -->

# Phase 5.54 closure reconciliation prompt

## Objective

Close the documentation and machine-readable contract gap after the proven
Phase 5.54 Debian-package lifecycle without rerunning completed target work or
reusing the obsolete Phase 5.53 archive-installer control graph.

## Frozen evidence inputs

- product package SHA-256:
  `f61286a6e63c2735413a0e86d13c5dc2d91f4581e8a20aab7291234b1991f90b`;
- inactive configured installation evidence commit: `c5f278c`;
- GPIO4 output-disabled lifecycle evidence commit: `4018b0e`;
- GPIO20 output-disabled lifecycle evidence commit: `5b0cadd`;
- package removal and reinstall evidence commit: `d7e9141`.

Phase 5.53 product and qualification archives, controls, failures, and evidence
remain immutable historical records. They are not active Phase 5.54 package
installation prerequisites.

## Required work

1. Replace the active release-integration status graph with a Phase 5.54 graph
   whose prerequisites follow the conventional Debian package lifecycle.
2. Mark only the exact completed inactive installation, GPIO4, GPIO20, and
   package removal/reinstall gates passed. Preserve their claim ceilings.
3. Correct documentation that still says no representative lifecycle ran or
   presents Phase 5.53 as the active candidate.
4. Correct the legacy build-contract test so it validates the `dh-dkms`
   `#MODULE_VERSION#` template through `debian/rules`, without weakening direct
   non-Debian DKMS version matching.
5. Keep semantic version selection after this reconciliation. Do not invent a
   release version, tag, compatibility claim, publication, or consumer pin.
6. Commit the reconciled source state. From clean worktrees at that exact
   commit, run the complete offline suite and package suite twice. Record exact
   transcript hashes, skips, and failures.
7. Only if both passes succeed, mark reconciliation and offline validation
   passed in a later evidence commit. Then perform one final adversarial audit
   of claim ceilings and roadmap ordering.

## Safety and authority

This slice is repository-only and offline. Do not contact `wspr5`, install or
remove packages, load modules, apply overlays, alter boot state, reboot, touch
GPIO/clocks/DMA, transmit, produce RF, tag, publish, or modify a consuming
repository.

## Exit

Exit with a clean synchronized branch and one unambiguous next gate: explicit
semantic release-version selection followed by final candidate construction
and reproduction. Publication remains separately authorized.
