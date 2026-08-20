<!-- SPDX-License-Identifier: MIT -->

# Phase 5.50 metadata-free staging and pre-root independent review

Status: BLOCKED after the authenticated schema-5 pre-root transition and
before lifecycle attempt 1. The target failed closed and no attempt started.

Two fresh 7,082-byte captures were byte-identical to the canonical snapshot
and passed exact archived target-side and local validation. The staging and
qualification namespaces were absent beforehand, runtime was inactive, and
all six services were inactive.

The metadata-free transport contained exactly 759 regular files in 34
directories: 63 envelope inputs, 696 extracted archive members, and the
separately sealed envelope. Target inspection found exact path-set equality,
all 63 input hashes correct, no extended attributes, and no forbidden, link,
special, AppleDouble, Finder, VCS, cache, backup, bytecode, or PAX content.
The archived executor's read-only pre-root validation passed.

The authenticated transition completed at
`2026-08-17T21:51:52.498645+00:00`, checkpoint `commit`, with live output
disabled. Independent verification passed for the terminal journal, root
marker, all 55 transition files, all 22 installed tools, inactive runtime,
inactive services, absent Phase 5.50 attempt namespace, and standalone
schema-6 execution-instance validation with readiness required.

The final installed permanent-executor check exposed a frozen-tool defect:
`bootstrap_root_validator()` accepts instance schemas 3, 4, or 5, but Phase
5.50 uses schema 6. It rejected the exact authorized instance with
`installed trust bootstrap requires execution-instance schema 3, 4, or 5`.
The earlier offline archived test validated `gate_d_instance` directly and did
not exercise this permanent-executor bootstrap path. Lifecycle execution must
not proceed. Correct resolution requires a successor candidate that adds
schema 6 to the permanent executor's authenticated trust bootstrap, plus a new
freeze, representative build, snapshot/control set, authorization, and
staging transition.

The transient transport and capture files were removed. The sealed staging
directory, qualification root, terminal pre-root journal, and installed
output-disabled package state remain as authenticated evidence and recovery
state. No GPIO operation, active pinctrl, clock enablement, DMA submission,
Si5351 or SDR operation, antenna connection, transmission, or RF occurred.
