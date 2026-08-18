<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 final split-candidate offline-checks-twice prompt

## Objective

Execute the final offline gate twice against the unchanged installed product
archive and one exact qualification-only successor, without reusing or
rebinding historical Phase 5.53 lifecycle controls.

## Fixed boundaries

- Product archive SHA-256:
  `032a0ca214427ebb6115b933042e7135f03c2ed6ce4f5c399686b2cf61395a76`.
- Product source: `4e7a64a0ca353d2fcab6e25891f5254746e2b91a`.
- Qualification successor must come from one clean commit and two
  byte-identical independently validated generations.

## Execution requirements

1. Verify the clean source, frozen predecessor release unit, product hash, and
   all eight historical archive hashes.
2. Before each pass, independently validate the exact qualification successor,
   including retained product artifacts, archive inventory, metadata,
   checksums, and source bytes.
3. Run the complete offline suite twice with all eight historical archives
   supplied to their exact archived validators.
4. Require identical transcripts, zero failures, and explicit classification
   of every skip. The two Phase 5.53 current-directory skips are required
   because those tests are historical controls bound to retired artifacts; do
   not supply the new directory to or patch those controls.
5. Record repo-only machine-readable evidence, the canonical transcript, a
   regression, and an adversarial review. Do not mutate the frozen artifact
   closures merely to record gate completion.

## Non-goals and safety

Do not generate lifecycle controls, access a target, stage files, administer
DKMS, load or bind a module, apply an overlay, reboot, access GPIO, enable a
clock, submit DMA, transmit, or produce RF.

## Exit criteria

Two complete byte-identical transcripts pass against the exact split candidate;
all historical archived validators pass; the two historical Phase 5.53 skips
and three Linux-only compile skips are explicit; evidence is independently
reviewed; and representative lifecycle control reconstruction is the sole next
gate.
