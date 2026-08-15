<!-- SPDX-License-Identifier: MIT -->

# Phase 5.2 release-unit adversarial assessment

Date: 2026-08-15
Scope: offline release-unit implementation only

## Method

The review attempted to falsify the Phase 5.2 execution prompt, engineering
contract, installation inventory, generator, validator, compatibility claims,
diagnostics, lifecycle boundary, and generated artifacts independently of the
ordinary green test result. It inspected all commands before execution and
performed no DKMS registration, installation, loading, overlay application,
boot change, target access, GPIO, DMA, transmission, SDR, or RF activity.

## Reinjected findings

1. **New version retained an old live allowlist.** Merely changing module
   metadata from `0.0.0-phase4d-combined` to `0.0.0-phase5.2` left the Phase 4
   model/kernel allowlist capable of marking the new, unqualified module
   identity `Experimental`. The release manifest correctly had no positive
   entry, so the kernel behavior and manifest conflicted. The release gate now
   returns live-ineligible, the query reports the Phase 5.2 no-positive-entry
   identity, the release notes state the demotion, and a deterministic test
   enforces it. Historical Phase 4 clients remain pinned to their original
   candidate identity.
2. **Tool paths polluted reproducibility metadata.** Absolute Python and `dtc`
   paths differed across otherwise equivalent hosts. Metadata now records the
   implementation/command, version, and executable SHA-256, while the resolved
   path is used only internally during generation.
3. **Archive modes depended on checkout metadata.** Filesystem executable bits
   could differ across checkouts. Archive modes are now normalized to `0755`
   for shebang tools and `0644` for all other source inputs.
4. **Diagnostic symlink status was misleading.** Resolving the supplied release
   path before testing whether it was a symlink could report a symlink as a
   real directory. The diagnostic now evaluates the supplied path separately
   and reports the resolved path only as context.
5. **Raw overlay compilation produced known plugin-context warnings.** The
   standalone overlays depend on labels and parent cell counts resolved only
   when applied to the base tree. The generator now uses an explicit recorded
   suppression list for only those expected standalone plugin warnings and
   rejects every remaining `dtc` warning or error. The resulting GPIO4 and
   GPIO20 DTBO hashes match the independently used Phase 4 artifacts.

## Final falsification result

No unresolved objective finding remains within Phase 5.2. The inventory covers
every required artifact class and destination; validation rejects dirty or
untagged publishable output, version/tag/archive mismatch, unsafe archive
members, missing or extra artifacts, checksum tampering, UAPI/overlay/manifest
identity drift, incomplete inventory records, and a non-publishable unit unless
explicitly accepted for development validation. Two real-`dtc` generations in
fresh directories produced byte-identical archives and DTBOs.

Phase 5.2 remains non-publishable and default `Unavailable`. A clean commit and
expected tag are still required to generate publishable bytes. Representative
header builds, target lifecycle, signing enforcement/key enrollment, complete
removal on target, calibrated qualification, tag/release publication,
post-download verification, and WSPR-Transmitter/WsprryPi integration remain
separate gated work and are not findings against this offline slice.
