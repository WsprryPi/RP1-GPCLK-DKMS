<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 roadmap prerequisite cleanup prompt

## Objective

Correct the post-freeze release roadmap so it requires one exact two-pass
split-candidate offline gate, then one qualification-only installation, then
the output-disabled representative lifecycle matrix.

## Frozen identities

- Product archive SHA-256:
  `032a0ca214427ebb6115b933042e7135f03c2ed6ce4f5c399686b2cf61395a76`.
- Qualification archive SHA-256:
  `6dd18ef1543cf824aba1c9d9057fd014c529df149ef705b721e9d75ad4bbe3bc`.
- Qualification source commit:
  `17b8ed285450c37aaf858080b53857737638c6e9`.

These artifacts are frozen. This post-freeze roadmap edit must not regenerate,
replace, or silently redefine either archive.

## Required work

1. Make the two exact artifact-bound offline passes the sole next execution
   gate and retain their blocked status until both pass.
2. Add a distinct qualification-only installation gate after the offline gate.
   Require final read-only recapture, literal archive and member validation,
   the separate qualification ledger, preservation of the existing inactive
   product and both inactive overlays, and a stop before lifecycle attempt 1.
3. Make that installation gate the strict prerequisite of the representative
   lifecycle matrix.
4. Require future path-bearing lifecycle consumers to be reconstructed from
   the final product and qualification closures after literal installed-path
   validation. Do not patch historical controls.
5. Update the machine-readable regression so missing, reordered, or bypassed
   prerequisites fail closed.

## Non-goals and safety

Do not execute the two-pass gate, access a target, stage an archive, install or
remove tooling or product files, administer DKMS, operate a module or overlay,
reboot, access GPIO, enable a clock, submit DMA, transmit, or produce RF.

## Validation and exit

Validate JSON and the release-gate regression, run documentation/link and
whitespace checks, inspect the complete diff, and adversarially verify that the
edit neither advances a blocked gate nor changes a frozen artifact identity.
Exit only with the exact linear order encoded and the two-pass offline gate as
the next executable slice.
