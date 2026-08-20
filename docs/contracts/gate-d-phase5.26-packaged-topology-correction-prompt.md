<!-- SPDX-License-Identifier: MIT -->

# Phase 5.26 packaged Si5351 topology correction execution prompt

## Objective

Create and freeze a distinct `0.0.0-phase5.26` offline successor whose packaged
operator documentation correctly describes the transmitter topology: the
Si5351 is a separate I2C-controlled RF output path and is not wired to GPIO4 or
GPIO20; GPIO4 and GPIO20 are reserved for the RP1 GPCLK DKMS module.

Preserve Phase 5.25 as immutable historical evidence. Do not contact a
Raspberry Pi or advance into representative build or lifecycle execution.

## Verified starting point

- Branch: `codex/phase-5-12-calibrated-review-relationship`.
- Phase 5.25 frozen source:
  `d9f8fd8b17f1c2ee9324704c6b6630dfccfb5e4e`.
- Phase 5.25 archive SHA-256:
  `e615750897009b79d0ead1e3bbf4133e0c4d5c157cc259d513a76ad65bd993e4`.
- Phase 5.25 passed its representative build and offline control-set checks,
  but its frozen archive contains incorrect Si5351-to-GPIO wording in the
  packaged target runbook and authorization dossier.
- Commit `10dfc2e` preserves the Phase 5.25 control set and corrected source
  wording as the clean successor basis.

## Required implementation

1. Advance the complete release-owned version identity to
   `0.0.0-phase5.26`, including module metadata, DKMS metadata, installer and
   diagnostics identities, release layout, installation paths, compatibility
   text, lifecycle and representative-matrix metadata, integration gates,
   release notes, and generic offline tests.
2. Preserve every Phase 5.25 frozen archive, manifest, representative-build
   record, qualification identity, control document, attempt bundle, review,
   and test of those historical bytes unchanged.
3. Record Phase 5.25 as superseded before lifecycle execution solely because
   its packaged documentation misstates the Si5351/GPIO topology.
4. Make Phase 5.26 the selected documentation-corrected successor. Do not
   alter module behavior, UAPI, overlays, schemas, or permanent lifecycle
   semantics beyond unavoidable release-version identities.
5. Add Phase 5.26 behavior and security notes stating the topology correction,
   unchanged output-disabled safety boundary, and claim ceiling.
6. Add deterministic regression coverage proving packaged runbook and dossier
   text states the correct topology and rejects the former wording.

## Validation and adversarial review

- Run focused version, packaging, installation, release-gate, documentation,
  and topology tests.
- Run the complete offline suite twice.
- Inspect the exact archive member bytes for both corrected documents.
- Build the exact clean implementation commit twice in separate directories;
  require byte-identical archives and sidecars.
- Validate both release units independently and record exact hashes, tool
  identities, source commit, tag absence, and non-publishable status.
- Conduct a separate adversarial assessment challenging historical-evidence
  preservation, accidental module/UAPI/tool changes, stale Phase 5.25 wording,
  archive membership, version closure, claim inflation, and any attempt to
  treat offline success as representative target evidence.
- Reinject every actionable finding and repeat affected checks until clean.

## Non-goals and prohibitions

Do not contact `wspr4` or `wspr5`; install packages; register, build through,
install, or remove DKMS; sign, load, bind, unbind, or unload a module; apply an
overlay; change services, boot state, kernels, or signing policy; reboot;
access GPIO, GPCLK, clocks, or DMA; execute target helpers; operate Si5351 or
SDRplay; connect an antenna; transmit; perform RF work; tag; publish; open a
pull request; or change consuming repositories.

## Exit criteria

Stop after the implementation and freeze commits are reviewed, pushed on the
current branch, and the worktree is clean. Report exact commits and artifact
hashes, validation results, skipped target evidence, licensing impact, and the
next separately authorized representative-build gate. Phase 5.26 may be called
offline reproducible and adversarially reviewed only; it cannot exceed that
claim until its exact archive receives representative target evidence.
