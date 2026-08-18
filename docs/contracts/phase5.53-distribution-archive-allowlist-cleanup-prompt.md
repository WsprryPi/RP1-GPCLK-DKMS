<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 distribution-archive allowlist cleanup prompt

Replace the source-archive blacklist with a fail-closed allowlist derived from
the active release layout. Include only source and header trees, build inputs,
canonical UAPI, overlay sources, required schemas and tools, active release
contracts, operator documentation, current release notes, license/security
material, and the release generator and validator needed for reproduction.

Keep repository-only prompts, reviews, development notes, historical release
notes, tests, target identities, qualification attempts, phase controls, and
evidence out of the distribution archive. Preserve the one explicitly
contracted Phase 5.24 residue-recovery document until the release layout is
separately changed. Reject missing allowlisted inputs and unsafe files.

Add deterministic archive-inventory regression coverage, generate two
independent development release units, require byte identity, validate both,
and inspect the archive for forbidden classes. This is offline packaging work
only. Do not perform a representative build, access a target, mutate a system,
or operate GPIO, clocks, DMA, SDR, Si5351, transmission, or RF hardware.
