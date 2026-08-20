<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 split-artifact roadmap alignment prompt

Align the release roadmap and repository-only engineering contract with the
sealed product/qualification artifact split. Name both archives wherever
qualification, reproduction, publication, or public-download verification
requires both. Preserve ordinary product installation as product-only, and
limit WSPR-Transmitter and WsprryPi dependency pins to the product archive,
UAPI, compatibility manifest, and adapter identities.

Clarify that the later artifact-reproduction gate is a post-adversarial-review
reproduction of both archives and both DTBOs and is not satisfied merely by
the initial candidate-freeze builds. Do not change gate status, archive hashes,
packaging behavior, current release notes, operator files, or sealed artifact
bytes. Perform no target, system, GPIO, clock, DMA, SDR, transmission, or RF
work.
