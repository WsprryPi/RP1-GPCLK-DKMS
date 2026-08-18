<!-- SPDX-License-Identifier: MIT -->

# Phase 5.53 product and qualification artifact split prompt

Split the release unit into a DKMS product source archive and a separate
release-qualification tooling archive. The product archive owns module source,
headers, Kbuild/DKMS inputs, UAPI, overlays, product installation and lifecycle
tools, compatibility/signing/diagnostic policy, operator documentation, current
release notes, licensing, and release reproduction tools.

The qualification archive owns generic Gate D executors, schemas, probes,
representative-system matrix, release gates, and calibrated-review policy.
Historical phase controls, target identities, prompts, reviews, evidence,
development notes, and tests remain repository-only and enter neither archive.

Give each archive its own explicit layout-derived allowlist, deterministic
versioned root, SHA-256 identity, provenance inventory, checksum coverage, and
independent validation. Require two exact-source generations to be byte
identical. Do not perform representative builds, target access, system
mutation, GPIO, clock, DMA, SDR, Si5351, transmission, or RF work.
