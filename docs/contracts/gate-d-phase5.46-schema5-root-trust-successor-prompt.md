<!-- SPDX-License-Identifier: MIT -->

# Phase 5.46 schema-5 root-trust successor repair prompt

Correct the offline permanent-executor defect proven by the Phase 5.45 attempt
1 safe stop at commit `934b3587ab4464b6b6079617566911a5a5626355`.
`bootstrap_root_validator()` currently maps execution-instance schema 5 to
target-plan schema 4 even though the sealed Phase 5.45 instance and target plan
are both schema 5. Make the supported relationship explicit: instance schema 3
requires target-plan schema 4, while instance schemas 4 and 5 require
target-plan schema 5. Continue to reject every unknown or mismatched pair.

Add an installed-permanent-executor regression whose primary accepted fixture
is an exact schema-5 instance/schema-5 target-plan pair with the complete
authenticated Python import graph. Retain coverage for the supported legacy
schema-4/schema-5 pair and add a negative schema-5/schema-4 assertion. Preserve
the existing missing, substituted, symlinked, writable, extra-module,
unbounded-import, and initialization-failure checks.

Run focused trust-bootstrap and installed-import-graph tests, deterministic
Phase 5.45 generation checks, archived pre-root validation, documentation and
whitespace checks, and the complete archive-bound offline suite. Perform a
separate adversarial assessment and correct every actionable finding before
handoff.

This is an offline source-and-test repair only. Do not modify frozen Phase 5.45
release or control bytes, relabel them as passing, stage target inputs, connect
to `wspr5`, invoke recovery, execute an attempt, administer DKMS or overlays,
operate GPIO, clocks, DMA, I2C, Si5351, SDR, an antenna, transmission, or RF.
Do not freeze or build Phase 5.46 in this slice.
