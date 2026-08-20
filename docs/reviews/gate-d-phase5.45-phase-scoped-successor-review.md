<!-- SPDX-License-Identifier: MIT -->

# Phase 5.45 phase-scoped successor prerequisite review

Status: PASS for the offline path-namespace prerequisite. No Phase 5.45
candidate is frozen or authorized by this result.

The attempt generator now accepts a path namespace only when it exactly equals
the candidate release without the `0.0.0-` prefix, a hyphen, and the first
twelve hexadecimal characters of the candidate source commit. Execution
instance schema 5 requires that namespace and requires every row evidence root
to be exactly `gate-d/runs/<namespace>/<row-id>`.

For a namespaced successor, all 38 main evidence directories and journals,
staging directories, owned-path inventories, subordinate transition and
recovery directories and journals, and reboot-resume journals are below
`/var/lib/rp1-gpclk-dkms/gate-d/runs/<namespace>/`. Historical schema 1
through 4 controls retain their sealed paths and validate unchanged.

The independent path-closure test enumerated the complete proposed successor
path set, every Phase 5.42 and Phase 5.43 attempt path, and the retained Phase
5.42 history destination. The proposed set is internally unique and has an
empty intersection with every historical path. Negative tests rejected a
candidate-mismatched namespace and one unscoped row.

The complete archive-bound offline suite passed, including deterministic
generation of Phase 5.39, 5.41, 5.42, and 5.43 controls and exact archived
Phase 5.43 pre-root validation. No target connection, staging, build,
installation, DKMS operation, module operation, overlay operation, service or
boot change, GPIO, clock, DMA, Si5351, SDR, antenna, transmission, or RF work
occurred.

The next slice may bump and freeze the Phase 5.45 candidate from these clean
bytes. It must then perform an exact representative build before generating
schema-5 execution controls with the candidate-derived namespace. Target
execution remains a later, separately authorized gate.
